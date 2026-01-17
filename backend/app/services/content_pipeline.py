# =============================================
# 統一內容生成流水線 (Content Pipeline)
# =============================================
# 整合 文案生成 → SEO 優化 → GEO 結構化數據
# 一次輸入產品資訊，輸出完整的內容包

import uuid
import json
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product
from app.models.content import AIContent
from app.models.seo import SEOContent, StructuredData
from app.models.database import utcnow
from app.services.ai_service import AIAnalysisService, AISettingsService


# =============================================
# 結果數據結構
# =============================================

@dataclass
class LocalizedContent:
    """單一語言的內容"""
    language: str = ""

    # 文案部分
    title: str = ""
    selling_points: List[str] = field(default_factory=list)
    description: str = ""

    # SEO 部分
    meta_title: str = ""           # max 70 chars
    meta_description: str = ""     # max 160 chars
    primary_keyword: str = ""
    secondary_keywords: List[str] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    seo_score: int = 0
    score_breakdown: Dict[str, int] = field(default_factory=dict)
    og_title: str = ""
    og_description: str = ""

    # AI 摘要部分
    ai_summary: str = ""
    ai_facts: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    """流水線完整結果（支持多語言）"""
    success: bool = True
    product_info: Dict[str, Any] = field(default_factory=dict)

    # 多語言內容（key = language code，如 "zh-HK", "zh-CN", "en"）
    localized: Dict[str, LocalizedContent] = field(default_factory=dict)

    # 共用部分（不需要翻譯）
    tone: str = "professional"
    product_schema: Dict[str, Any] = field(default_factory=dict)
    faq_schema: Optional[Dict[str, Any]] = None

    # 存儲的記錄 ID（每語言一個）
    content_ids: Dict[str, uuid.UUID] = field(default_factory=dict)
    seo_content_ids: Dict[str, uuid.UUID] = field(default_factory=dict)
    structured_data_id: Optional[uuid.UUID] = None

    # 元數據
    languages: List[str] = field(default_factory=list)
    generation_time_ms: int = 0
    model_used: str = ""
    error: Optional[str] = None


# =============================================
# GoGoJap 品牌背景（共用）
# =============================================

GOGOJAP_BRAND_CONTEXT = """
## GoGoJap 品牌背景

### 核心優勢
- 香港米芝蓮星級餐廳及五星酒店食材供應商（半島酒店、文華東方、四季酒店、Zuma、Amber、Sushi Shikon）
- 柴灣自有 HACCP 認證加工中心，日處理量達 5,000+ 訂單
- -18°C 全程專業冷鏈，從倉庫到府最快 4 小時送達
- 每週空運/海運直送，產地直採無中間商
- 多位五星酒店鐵板燒/壽司主廚私下指定使用

### 品牌承諾
「餐廳級食材，屋企價享受」— 米芝蓮同級品質，只需餐廳 1/5 價格
"""


# =============================================
# 內容生成流水線服務
# =============================================

class ContentPipelineService:
    """
    統一內容生成流水線

    一次 AI 調用生成完整內容包：
    - 文案：標題、賣點、描述
    - SEO：Meta 標籤、關鍵詞、評分
    - GEO：AI 摘要、結構化數據 (Schema.org JSON-LD)
    """

    def __init__(self, db: AsyncSession, ai_service: AIAnalysisService):
        self.db = db
        self.ai_service = ai_service

    @classmethod
    async def create(cls, db: AsyncSession) -> "ContentPipelineService":
        """工廠方法：創建服務實例"""
        config = await AISettingsService.get_config(db)
        ai_service = AIAnalysisService(config)
        return cls(db, ai_service)

    # =============================================
    # 主入口：執行流水線
    # =============================================

    async def run(
        self,
        product_id: Optional[uuid.UUID] = None,
        product_info: Optional[Dict[str, Any]] = None,
        languages: Optional[List[str]] = None,
        tone: str = "professional",
        include_faq: bool = False,
        save_to_db: bool = True,
    ) -> PipelineResult:
        """
        執行內容生成流水線（一次 AI 調用生成多語言內容）

        Args:
            product_id: 產品 ID（從數據庫獲取）
            product_info: 產品信息字典（手動提供）
            languages: 目標語言列表，如 ["zh-HK", "zh-CN", "en"]，默認 ["zh-HK"]
            tone: 文案語氣 (professional/casual/luxury)
            include_faq: 是否生成 FAQ Schema
            save_to_db: 是否保存到數據庫

        Returns:
            PipelineResult 包含所有語言的生成內容
        """
        start_time = datetime.now()

        # 默認語言
        if not languages:
            languages = ["zh-HK"]

        result = PipelineResult(tone=tone, languages=languages)

        # 獲取產品信息
        product_data = await self._get_product_data(product_id, product_info)
        if not product_data:
            result.success = False
            result.error = "必須提供 product_id 或 product_info"
            return result

        result.product_info = product_data

        # 一次 AI 調用生成全部語言的內容（文案 + SEO + AI 摘要）
        await self._generate_all_content(result, product_data, languages, tone)

        # 構建 Product Schema（用代碼構建，不需要 AI）
        # 使用第一個語言的描述
        first_lang = languages[0]
        description = result.localized.get(first_lang, LocalizedContent()).description
        result.product_schema = self._build_product_schema(product_data, description)

        # 可選：生成 FAQ Schema（需要額外 AI 調用）
        if include_faq:
            result.faq_schema = await self._generate_faq_schema(product_data)

        # 保存到數據庫
        if save_to_db:
            await self._save_results(result, product_id)

        # 計算執行時間
        end_time = datetime.now()
        result.generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
        result.model_used = self.ai_service.config.model if self.ai_service.config else "unknown"

        return result

    # =============================================
    # 一次生成全部內容
    # =============================================

    async def _generate_all_content(
        self,
        result: PipelineResult,
        product_data: Dict[str, Any],
        languages: List[str],
        tone: str,
    ) -> None:
        """一次 AI 調用生成多語言內容（文案 + SEO + AI 摘要）"""

        # 語言名稱映射
        lang_names = {
            "zh-HK": "繁體中文（香港）",
            "zh-TW": "繁體中文（台灣）",
            "zh-CN": "簡體中文",
            "en": "English",
            "ja": "日本語",
        }

        lang_list = ", ".join([f'"{lang}"' for lang in languages])
        lang_desc = ", ".join([lang_names.get(lang, lang) for lang in languages])

        prompt = f"""{GOGOJAP_BRAND_CONTEXT}

## 任務
為以下產品生成完整的電商內容，**同時輸出 {len(languages)} 種語言版本**：
- 語言: {lang_desc}

每種語言都需要：
1. 產品文案（標題、賣點、描述）
2. SEO 優化（Meta 標籤、關鍵詞、評分）
3. AI 搜索引擎摘要（給 Perplexity/ChatGPT 等 AI 搜索引擎用）

## 產品資訊
- 名稱: {product_data.get('name', '')}
- 品牌: {product_data.get('brand', 'GoGoJap')}
- 分類: {product_data.get('category', '')}
- 描述: {product_data.get('description', '')}
- 特點: {', '.join(product_data.get('features', []))}
- 價格: {product_data.get('price', '')}
- 產地: {product_data.get('origin', '')}

## 文案要求
1. 語氣: {tone}
2. 標題要吸引眼球，突出核心賣點
3. 賣點用 3-5 個精煉短句
4. 描述要詳細但不冗長，150-300 字
5. **每種語言要地道自然，不是機械翻譯**

## SEO 要求（每種語言獨立優化）
1. Meta Title: 最多 70 個字符，包含該語言的主關鍵詞
2. Meta Description: 最多 160 個字符，包含 CTA
3. 主關鍵詞: 1 個核心搜索詞（該語言用戶常用的搜索詞）
4. 次要關鍵詞: 3-5 個相關詞
5. 長尾關鍵詞: 2-3 個精準詞組

## AI 摘要要求
1. ai_summary: 50-100 字的產品摘要，突出核心價值
2. ai_facts: 3-5 個客觀事實，方便 AI 引用

## SEO 評分標準
- title_score: 標題關鍵詞覆蓋 (0-100)
- description_score: 描述完整性 (0-100)
- keyword_score: 關鍵詞相關性 (0-100)
- readability_score: 可讀性 (0-100)

## 返回格式 (JSON)
以語言代碼為 key，每種語言的內容為 value：
```json
{{
    {lang_list.replace('"', '').split(', ')[0] if languages else "zh-HK"}: {{
        "title": "產品標題",
        "selling_points": ["賣點1", "賣點2", "賣點3"],
        "description": "詳細產品描述...",
        "meta_title": "SEO 標題 (max 70 chars)",
        "meta_description": "SEO 描述 (max 160 chars)",
        "primary_keyword": "主關鍵詞",
        "secondary_keywords": ["次要1", "次要2"],
        "long_tail_keywords": ["長尾1", "長尾2"],
        "seo_score": 85,
        "score_breakdown": {{"title_score": 90, "description_score": 85, "keyword_score": 80, "readability_score": 85}},
        "og_title": "OG 標題",
        "og_description": "OG 描述",
        "ai_summary": "AI 摘要...",
        "ai_facts": ["事實1", "事實2"]
    }}
}}
```

請為以下語言生成內容: [{lang_list}]
請只返回 JSON，不要其他內容。"""

        # 多語言需要更多 token
        max_tokens = 1500 * len(languages)
        response = await self.ai_service.call_ai(prompt, max_tokens=max_tokens)

        if response.success:
            try:
                content = self._parse_json_response(response.content)

                # 解析每種語言的內容
                for lang in languages:
                    lang_content = content.get(lang, {})
                    if not lang_content:
                        continue

                    localized = LocalizedContent(
                        language=lang,
                        # 文案部分
                        title=lang_content.get("title", ""),
                        selling_points=lang_content.get("selling_points", []),
                        description=lang_content.get("description", ""),
                        # SEO 部分
                        meta_title=lang_content.get("meta_title", "")[:70],
                        meta_description=lang_content.get("meta_description", "")[:160],
                        primary_keyword=lang_content.get("primary_keyword", ""),
                        secondary_keywords=lang_content.get("secondary_keywords", []),
                        long_tail_keywords=lang_content.get("long_tail_keywords", []),
                        seo_score=lang_content.get("seo_score", 0),
                        score_breakdown=lang_content.get("score_breakdown", {}),
                        og_title=lang_content.get("og_title", ""),
                        og_description=lang_content.get("og_description", ""),
                        # AI 摘要部分
                        ai_summary=lang_content.get("ai_summary", ""),
                        ai_facts=lang_content.get("ai_facts", []),
                    )
                    result.localized[lang] = localized

            except Exception:
                # 如果解析失敗，為第一個語言創建基本內容
                first_lang = languages[0] if languages else "zh-HK"
                result.localized[first_lang] = LocalizedContent(
                    language=first_lang,
                    title=product_data.get("name", ""),
                    description=response.content[:500] if response.content else "",
                )

    def _build_product_schema(
        self,
        product_data: Dict[str, Any],
        description: str = None,
    ) -> Dict[str, Any]:
        """構建 Product Schema.org JSON-LD"""

        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product_data.get("name", ""),
            "description": description or product_data.get("description", ""),
            "brand": {
                "@type": "Brand",
                "name": product_data.get("brand", "GoGoJap")
            },
        }

        # 添加價格信息
        if product_data.get("price"):
            schema["offers"] = {
                "@type": "Offer",
                "price": str(product_data["price"]),
                "priceCurrency": "HKD",
                "availability": "https://schema.org/InStock",
            }

        # 添加產地
        if product_data.get("origin"):
            schema["countryOfOrigin"] = {
                "@type": "Country",
                "name": product_data["origin"]
            }

        # 添加分類
        if product_data.get("category"):
            schema["category"] = product_data["category"]

        return schema

    async def _generate_faq_schema(
        self,
        product_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """生成 FAQ Schema"""

        prompt = f"""為以下產品生成 3-5 個常見問題及答案。

產品: {product_data.get('name', '')}
品牌: {product_data.get('brand', 'GoGoJap')}
分類: {product_data.get('category', '')}

返回格式 (JSON):
```json
{{
    "faqs": [
        {{"question": "問題1?", "answer": "答案1"}},
        {{"question": "問題2?", "answer": "答案2"}}
    ]
}}
```

請只返回 JSON。"""

        response = await self.ai_service.call_ai(prompt, max_tokens=800)

        faqs = []
        if response.success:
            try:
                content = self._parse_json_response(response.content)
                faqs = content.get("faqs", [])
            except Exception:
                pass

        # 構建 FAQ Schema
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": faq.get("question", ""),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq.get("answer", "")
                    }
                }
                for faq in faqs
            ]
        }

        return schema

    # =============================================
    # 輔助方法
    # =============================================

    async def _get_product_data(
        self,
        product_id: Optional[uuid.UUID],
        product_info: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """獲取產品數據"""

        if product_id:
            product = await self.db.get(Product, product_id)
            if product:
                return {
                    "name": product.name,
                    "brand": product.brand,
                    "category": product.category,
                    "description": product.description,
                    "price": float(product.price) if product.price else None,
                    "origin": getattr(product, "origin", None),
                    "features": getattr(product, "features", []) or [],
                }

        if product_info:
            return product_info

        return None

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析 AI 返回的 JSON"""
        content = content.strip()

        # 移除 markdown 代碼塊
        if content.startswith("```"):
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)

        return json.loads(content)

    async def _save_results(
        self,
        result: PipelineResult,
        product_id: Optional[uuid.UUID],
    ) -> None:
        """保存結果到數據庫（每種語言獨立保存）"""

        # 為每種語言保存內容
        for lang, localized in result.localized.items():
            if not localized.title:
                continue

            # 提取關鍵詞列表
            all_keywords = [localized.primary_keyword] if localized.primary_keyword else []
            all_keywords.extend(localized.secondary_keywords)
            all_keywords.extend(localized.long_tail_keywords)

            # 保存文案內容
            ai_content = AIContent(
                id=uuid.uuid4(),
                product_id=product_id,
                title=localized.title,
                description=localized.description,
                selling_points=localized.selling_points,
                keywords=all_keywords,
                status="draft",
                generated_at=utcnow(),
            )
            self.db.add(ai_content)
            result.content_ids[lang] = ai_content.id

            # 保存 SEO 內容
            seo_content = SEOContent(
                id=uuid.uuid4(),
                product_id=product_id,
                meta_title=localized.meta_title,
                meta_description=localized.meta_description,
                primary_keyword=localized.primary_keyword,
                secondary_keywords=localized.secondary_keywords,
                long_tail_keywords=localized.long_tail_keywords,
                seo_score=localized.seo_score,
                score_breakdown=localized.score_breakdown,
                og_title=localized.og_title,
                og_description=localized.og_description,
                language=lang,
                status="draft",
                created_at=utcnow(),
                updated_at=utcnow(),
            )
            self.db.add(seo_content)
            result.seo_content_ids[lang] = seo_content.id

        # 保存結構化數據（共用，不按語言分）
        if result.product_schema:
            # 使用第一個語言的 AI 摘要
            first_lang = result.languages[0] if result.languages else "zh-HK"
            first_localized = result.localized.get(first_lang, LocalizedContent())

            structured_data = StructuredData(
                id=uuid.uuid4(),
                product_id=product_id,
                schema_type="Product",
                json_ld=result.product_schema,
                ai_summary=first_localized.ai_summary,
                ai_facts=first_localized.ai_facts,
                is_valid=True,
                created_at=utcnow(),
                updated_at=utcnow(),
            )
            self.db.add(structured_data)
            result.structured_data_id = structured_data.id

        await self.db.commit()

    # =============================================
    # 批量生成
    # =============================================

    async def run_batch(
        self,
        products: List[Dict[str, Any]],
        languages: Optional[List[str]] = None,
        tone: str = "professional",
        include_faq: bool = False,
        save_to_db: bool = True,
        max_concurrent: int = 3,
    ) -> "BatchPipelineResult":
        """
        批量執行內容生成流水線

        Args:
            products: 產品信息列表，每個包含 name, brand, category 等
            languages: 目標語言列表，如 ["zh-HK", "en"]
            tone: 文案語氣
            include_faq: 是否生成 FAQ
            save_to_db: 是否保存到數據庫
            max_concurrent: 最大並發數

        Returns:
            BatchPipelineResult 包含所有產品的結果
        """
        import asyncio
        from datetime import datetime

        start_time = datetime.now()

        if not languages:
            languages = ["zh-HK"]

        results: List[PipelineResult] = []
        errors: List[Dict[str, Any]] = []

        # 使用信號量限制並發
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_product(index: int, product_info: Dict[str, Any]) -> None:
            async with semaphore:
                try:
                    result = await self.run(
                        product_info=product_info,
                        languages=languages,
                        tone=tone,
                        include_faq=include_faq,
                        save_to_db=save_to_db,
                    )
                    results.append((index, result))  # 保持順序
                except Exception as e:
                    errors.append({
                        "index": index,
                        "product_name": product_info.get("name", "unknown"),
                        "error": str(e),
                    })

        # 並發處理所有產品
        tasks = [
            process_product(i, product)
            for i, product in enumerate(products)
        ]
        await asyncio.gather(*tasks)

        # 按原始順序排列結果
        results.sort(key=lambda x: x[0])
        sorted_results = [r[1] for r in results]

        end_time = datetime.now()
        total_time_ms = int((end_time - start_time).total_seconds() * 1000)

        return BatchPipelineResult(
            success=len(errors) == 0,
            total_products=len(products),
            successful_count=len(sorted_results),
            failed_count=len(errors),
            results=sorted_results,
            errors=errors,
            total_time_ms=total_time_ms,
            languages=languages,
        )


@dataclass
class BatchPipelineResult:
    """批量流水線結果"""
    success: bool = True
    total_products: int = 0
    successful_count: int = 0
    failed_count: int = 0
    results: List[PipelineResult] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    total_time_ms: int = 0
    languages: List[str] = field(default_factory=list)


# =============================================
# 工廠函數
# =============================================

async def get_content_pipeline_service(db: AsyncSession) -> ContentPipelineService:
    """獲取內容流水線服務實例"""
    return await ContentPipelineService.create(db)
