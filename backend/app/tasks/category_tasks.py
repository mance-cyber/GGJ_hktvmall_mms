# =============================================
# 類別數據庫 Celery 任務
# =============================================

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import logging
import re
import asyncio

from celery import shared_task
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.category import (
    CategoryDatabase,
    CategoryProduct,
    CategoryPriceSnapshot,
    CategoryAnalysisReport
)
from app.connectors.firecrawl import get_firecrawl_connector
from app.connectors.hktv_scraper import get_hktv_scraper, HKTVUrlParser

logger = logging.getLogger(__name__)

# 數據庫連接（用於 Celery 任務）
settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# =============================================
# 類別商品抓取任務
# =============================================

@shared_task(bind=True, name="scrape_category_products")
def scrape_category_products(self, category_id: str, max_products: Optional[int] = None):
    """
    抓取類別內的所有商品

    1. 使用 Firecrawl Map 發現類別頁面所有 URL
    2. 過濾出商品 URL
    3. 批量抓取商品資訊
    4. 保存到數據庫
    """
    return asyncio.run(_scrape_category_products_async(
        task_id=self.request.id,
        category_id=category_id,
        max_products=max_products
    ))


async def _scrape_category_products_async(
    task_id: str,
    category_id: str,
    max_products: Optional[int]
):
    """
    異步執行類別抓取

    使用 HKTVScraper 專用抓取器，針對 JavaScript SPA 優化
    """
    async with AsyncSessionLocal() as db:
        try:
            # 獲取類別
            result = await db.execute(
                select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
            )
            category = result.scalar_one_or_none()
            if not category:
                logger.error(f"類別 {category_id} 不存在")
                return {"success": False, "error": "類別不存在"}

            logger.info(f"開始抓取類別: {category.name} ({category.hktv_category_url})")

            # ==================== 階段 1: 發現商品 URL ====================
            # 使用 HKTVScraper 專用抓取器（針對 JavaScript SPA 優化）
            scraper = get_hktv_scraper()

            logger.info("正在使用 HKTVScraper 發現商品 URL（JavaScript 渲染模式）...")

            # 發現商品 URL（使用 JS 渲染等待）
            product_urls = scraper.discover_product_urls_from_store(
                category.hktv_category_url,
                max_products=max_products or 50
            )

            total_urls = len(product_urls)
            logger.info(f"發現 {total_urls} 個有效商品 URL")

            if total_urls == 0:
                logger.warning("未發現任何商品 URL - HKTVmall 頁面可能需要更長的渲染時間")
                return {
                    "success": True,
                    "products_scraped": 0,
                    "products_failed": 0,
                    "message": "未發現商品 URL，請檢查類別頁面是否正確"
                }

            # ==================== 階段 2: 批量抓取商品 ====================
            logger.info("開始批量抓取商品資訊...")

            products_scraped = 0
            products_failed = 0
            errors = []

            for i, url in enumerate(product_urls, 1):
                try:
                    logger.info(f"[{i}/{total_urls}] 抓取: {url[:60]}...")

                    # 使用 HKTVScraper 抓取商品詳情
                    raw_data = scraper.scrape_product_page(url)
                    product_info = scraper.parse_product_data(url, raw_data)

                    # 驗證商品名稱有效性
                    if not product_info.name or product_info.name == "未知商品":
                        logger.warning(f"  ⚠ 商品名稱無效，跳過: {url}")
                        products_failed += 1
                        errors.append(f"商品名稱無效: {url}")
                        continue

                    # 檢查商品是否已存在（通過 URL 或 SKU）
                    existing_result = await db.execute(
                        select(CategoryProduct).where(
                            CategoryProduct.category_id == UUID(category_id),
                            CategoryProduct.url == url
                        )
                    )
                    existing_product = existing_result.scalar_one_or_none()

                    if existing_product:
                        # 更新現有商品
                        existing_product.name = product_info.name
                        existing_product.price = product_info.price
                        existing_product.original_price = product_info.original_price
                        existing_product.discount_percent = product_info.discount_percent
                        existing_product.stock_status = product_info.stock_status
                        existing_product.is_available = product_info.stock_status != "out_of_stock" if product_info.stock_status else True
                        existing_product.rating = product_info.rating
                        existing_product.review_count = product_info.review_count
                        existing_product.image_url = product_info.image_url
                        existing_product.brand = product_info.brand
                        existing_product.sku = product_info.sku
                        existing_product.last_updated_at = datetime.utcnow()

                        # 計算標準化單價
                        if product_info.price:
                            existing_product.unit_price = _calculate_unit_price(
                                product_info.price,
                                product_info.name
                            )

                        # 創建價格快照
                        snapshot = CategoryPriceSnapshot(
                            category_product_id=existing_product.id,
                            price=product_info.price,
                            original_price=product_info.original_price,
                            discount_percent=product_info.discount_percent,
                            unit_price=existing_product.unit_price,
                            stock_status=product_info.stock_status,
                            is_available=existing_product.is_available,
                        )
                        db.add(snapshot)

                        logger.info(f"  ✓ 更新: {product_info.name[:40]}... (HK${product_info.price})")
                    else:
                        # 創建新商品
                        unit_price = None
                        if product_info.price:
                            unit_price = _calculate_unit_price(product_info.price, product_info.name)

                        new_product = CategoryProduct(
                            category_id=UUID(category_id),
                            name=product_info.name,
                            url=url,
                            sku=product_info.sku,
                            brand=product_info.brand,
                            price=product_info.price,
                            original_price=product_info.original_price,
                            discount_percent=product_info.discount_percent,
                            unit_price=unit_price,
                            stock_status=product_info.stock_status,
                            is_available=product_info.stock_status != "out_of_stock" if product_info.stock_status else True,
                            rating=product_info.rating,
                            review_count=product_info.review_count,
                            image_url=product_info.image_url,
                            attributes={
                                "origin": product_info.origin,
                                "weight": product_info.weight,
                                "store_name": product_info.store_name,
                                "store_code": product_info.store_code,
                            },
                        )
                        db.add(new_product)
                        await db.flush()  # 獲取 ID

                        # 創建價格快照
                        snapshot = CategoryPriceSnapshot(
                            category_product_id=new_product.id,
                            price=product_info.price,
                            original_price=product_info.original_price,
                            discount_percent=product_info.discount_percent,
                            unit_price=unit_price,
                            stock_status=product_info.stock_status,
                            is_available=new_product.is_available,
                        )
                        db.add(snapshot)

                        logger.info(f"  ✓ 新增: {product_info.name[:40]}... (HK${product_info.price})")

                    products_scraped += 1

                    # 每 5 個商品提交一次（減少丟失風險）
                    if products_scraped % 5 == 0:
                        await db.commit()
                        logger.info(f"已提交 {products_scraped}/{total_urls} 個商品")

                    # 防止請求過快（Firecrawl 速率限制）
                    await asyncio.sleep(0.3)

                except Exception as e:
                    products_failed += 1
                    error_msg = f"抓取失敗 {url}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue

            # 最終提交
            await db.commit()

            # ==================== 階段 3: 更新類別統計 ====================
            count_result = await db.execute(
                select(func.count(CategoryProduct.id)).where(
                    CategoryProduct.category_id == UUID(category_id)
                )
            )
            total_products = count_result.scalar() or 0

            category.total_products = total_products
            category.last_scraped_at = datetime.utcnow()
            await db.commit()

            logger.info(f"類別抓取完成: {products_scraped} 成功, {products_failed} 失敗")

            return {
                "success": True,
                "category_id": category_id,
                "category_name": category.name,
                "products_scraped": products_scraped,
                "products_failed": products_failed,
                "total_products": total_products,
                "urls_discovered": total_urls,
                "errors": errors[:10],  # 只返回前 10 個錯誤
            }

        except Exception as e:
            logger.error(f"類別抓取任務失敗: {e}")
            await db.rollback()
            return {
                "success": False,
                "error": str(e)
            }


def _calculate_unit_price(price: Decimal, product_name: str) -> Optional[Decimal]:
    """
    計算標準化單價（每 100g）

    從商品名稱中提取重量/容量，計算每 100g 的價格
    """
    try:
        # 匹配重量格式：500g, 1kg, 1.5kg 等
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s?(g|kg|克|公斤)', product_name, re.IGNORECASE)

        if not weight_match:
            return None

        weight_value = float(weight_match.group(1))
        weight_unit = weight_match.group(2).lower()

        # 統一轉換為克
        if weight_unit in ['kg', '公斤']:
            weight_value *= 1000

        # 計算每 100g 價格
        if weight_value > 0:
            unit_price = (price / Decimal(str(weight_value))) * 100
            return round(unit_price, 2)

        return None

    except Exception as e:
        logger.warning(f"計算單價失敗: {e}")
        return None


# =============================================
# AI 分析任務
# =============================================

@shared_task(bind=True, name="analyze_category_data")
def analyze_category_data(
    self,
    category_id: str,
    analysis_type: str,
    model: str = "claude-sonnet-4-20250514"
):
    """
    AI 分析類別數據

    - analysis_type: "summary" (數據摘要) 或 "trend" (趨勢預測)
    """
    return asyncio.run(_analyze_category_data_async(
        task_id=self.request.id,
        category_id=category_id,
        analysis_type=analysis_type,
        model=model
    ))


async def _analyze_category_data_async(
    task_id: str,
    category_id: str,
    analysis_type: str,
    model: str
):
    """異步執行 AI 分析"""
    async with AsyncSessionLocal() as db:
        try:
            # 獲取類別
            result = await db.execute(
                select(CategoryDatabase).where(CategoryDatabase.id == UUID(category_id))
            )
            category = result.scalar_one_or_none()
            if not category:
                logger.error(f"類別 {category_id} 不存在")
                return {"success": False, "error": "類別不存在"}

            logger.info(f"開始 AI 分析: {category.name} - {analysis_type}")

            # ==================== 階段 1: 收集數據 ====================
            products_result = await db.execute(
                select(CategoryProduct).where(
                    CategoryProduct.category_id == UUID(category_id),
                    CategoryProduct.is_available == True
                )
            )
            products = products_result.scalars().all()

            if len(products) == 0:
                return {
                    "success": False,
                    "error": "類別內沒有可用商品數據"
                }

            # 構建數據快照
            data_snapshot = {
                "total_products": len(products),
                "products": [
                    {
                        "name": p.name,
                        "brand": p.brand,
                        "price": float(p.price) if p.price else None,
                        "original_price": float(p.original_price) if p.original_price else None,
                        "discount_percent": float(p.discount_percent) if p.discount_percent else None,
                        "unit_price": float(p.unit_price) if p.unit_price else None,
                        "rating": float(p.rating) if p.rating else None,
                        "review_count": p.review_count,
                    }
                    for p in products[:100]  # 最多 100 個商品
                ],
                "price_stats": {
                    "avg": float(sum(p.price for p in products if p.price) / len([p for p in products if p.price])) if any(p.price for p in products) else None,
                    "min": float(min((p.price for p in products if p.price), default=0)),
                    "max": float(max((p.price for p in products if p.price), default=0)),
                },
                "brands": list(set(p.brand for p in products if p.brand))[:20],
            }

            # ==================== 階段 2: 調用 Claude AI ====================
            from anthropic import Anthropic

            anthropic_client = Anthropic(api_key=settings.anthropic_api_key)

            if analysis_type == "summary":
                prompt = _build_summary_prompt(category.name, data_snapshot)
                report_title = f"{category.name} - 數據摘要"
            else:  # trend
                prompt = _build_trend_prompt(category.name, data_snapshot)
                report_title = f"{category.name} - 趨勢預測"

            logger.info("正在調用 Claude AI...")

            response = anthropic_client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            ai_response = response.content[0].text

            # 解析 AI 響應
            summary, key_findings, recommendations = _parse_ai_response(ai_response)

            # ==================== 階段 3: 保存報告 ====================
            report = CategoryAnalysisReport(
                category_id=UUID(category_id),
                report_type=analysis_type,
                report_title=report_title,
                summary=summary,
                key_findings=key_findings,
                recommendations=recommendations,
                data_snapshot=data_snapshot,
                generated_by=model,
            )
            db.add(report)
            await db.commit()

            logger.info(f"AI 分析完成: {report_title}")

            return {
                "success": True,
                "report_id": str(report.id),
                "category_name": category.name,
                "analysis_type": analysis_type,
                "summary": summary[:200] + "...",  # 摘要前 200 字
            }

        except Exception as e:
            logger.error(f"AI 分析任務失敗: {e}")
            await db.rollback()
            return {
                "success": False,
                "error": str(e)
            }


def _build_summary_prompt(category_name: str, data: Dict[str, Any]) -> str:
    """構建數據摘要提示詞"""
    return f"""你是一位專業的電商數據分析師。請分析以下 HKTVmall「{category_name}」類別的商品數據，並提供數據摘要。

# 數據概覽
- 總商品數：{data['total_products']}
- 平均價格：HK${data['price_stats']['avg']:.2f} (如果有)
- 價格區間：HK${data['price_stats']['min']:.2f} - HK${data['price_stats']['max']:.2f}
- 品牌數量：{len(data['brands'])}
- 主要品牌：{', '.join(data['brands'][:5])}

# 商品樣本（前 20 個）
{chr(10).join(f"- {p['name']}: HK${p['price']} ({p['brand']})" for p in data['products'][:20] if p['price'])}

# 分析要求
請提供以下內容：

## 摘要（Summary）
用 2-3 句話概括這個類別的整體情況。

## 關鍵發現（Key Findings）
列出 3-5 個數據洞察，格式：
1. 發現標題 - 具體描述
2. ...

## 建議（Recommendations）
提供 3-5 個可執行的建議，格式：
1. 建議標題 - 具體描述
2. ...

請用繁體中文回答，語言專業且簡潔。"""


def _build_trend_prompt(category_name: str, data: Dict[str, Any]) -> str:
    """構建趨勢預測提示詞"""
    return f"""你是一位專業的電商市場分析師。請基於以下 HKTVmall「{category_name}」類別的數據，預測市場趨勢。

# 數據概覽
- 總商品數：{data['total_products']}
- 平均價格：HK${data['price_stats']['avg']:.2f} (如果有)
- 價格區間：HK${data['price_stats']['min']:.2f} - HK${data['price_stats']['max']:.2f}
- 品牌數量：{len(data['brands'])}
- 主要品牌：{', '.join(data['brands'][:5])}

# 商品樣本
{chr(10).join(f"- {p['name']}: HK${p['price']} ({p['brand']})" for p in data['products'][:20] if p['price'])}

# 分析要求
請提供以下內容：

## 摘要（Summary）
用 2-3 句話概括市場現狀和趨勢方向。

## 關鍵趨勢（Key Findings）
列出 3-5 個市場趨勢，格式：
1. 趨勢標題 - 具體描述和證據
2. ...

## 未來建議（Recommendations）
提供 3-5 個前瞻性建議，格式：
1. 建議標題 - 具體行動方案
2. ...

請用繁體中文回答，語言專業且具洞察力。"""


def _parse_ai_response(response: str) -> tuple[str, Dict[str, Any], Dict[str, Any]]:
    """
    解析 AI 響應

    返回：(summary, key_findings, recommendations)
    """
    lines = response.strip().split('\n')

    summary = ""
    key_findings = {}
    recommendations = {}

    current_section = None
    current_content = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # 檢測章節標題
        if '摘要' in line or 'Summary' in line:
            if current_section and current_content:
                _save_section(current_section, current_content, key_findings, recommendations)
            current_section = 'summary'
            current_content = []
        elif '關鍵發現' in line or '關鍵趨勢' in line or 'Key Findings' in line:
            if current_section == 'summary':
                summary = '\n'.join(current_content).strip()
            current_section = 'findings'
            current_content = []
        elif '建議' in line or 'Recommendations' in line:
            if current_section == 'findings' and current_content:
                _save_section(current_section, current_content, key_findings, recommendations)
            current_section = 'recommendations'
            current_content = []
        else:
            current_content.append(line)

    # 保存最後一個章節
    if current_section == 'summary':
        summary = '\n'.join(current_content).strip()
    elif current_section and current_content:
        _save_section(current_section, current_content, key_findings, recommendations)

    return summary, key_findings, recommendations


def _save_section(section: str, content: List[str], findings: Dict, recommendations: Dict):
    """保存章節內容"""
    text = '\n'.join(content).strip()

    # 解析列表項
    items = {}
    for line in content:
        # 匹配 "1. 標題 - 描述" 格式
        match = re.match(r'^(\d+)\.\s*(.+?)\s*[-–—]\s*(.+)$', line)
        if match:
            num = match.group(1)
            title = match.group(2).strip()
            desc = match.group(3).strip()
            items[f"item_{num}"] = {"title": title, "description": desc}
        elif line.strip():
            items[f"item_{len(items) + 1}"] = {"text": line.strip()}

    if section == 'findings':
        findings.update(items if items else {"text": text})
    elif section == 'recommendations':
        recommendations.update(items if items else {"text": text})
