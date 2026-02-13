# =============================================
# Wellcome (惠康) 搜索策略
# =============================================
# 兩層降級搜索：本地索引 → 分類瀏覽
#
# 惠康搜索頁返回 HTTP 500，無法使用。
# 改用「分類瀏覽 + 本地索引」策略：
# 1. 先查本地索引（已爬取的 competitor_products）
# 2. 索引為空時，自動爬取對應分類頁填充索引
# 3. 用簡化關鍵詞 ILIKE 搜索本地索引
# =============================================

import re
import logging
from typing import List, Optional, Set

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.wellcome_client import (
    WellcomeProduct,
    get_wellcome_http_client,
    normalize_url,
    extract_product_id,
)
from app.connectors.agent_browser import get_agent_browser_connector
from app.config import get_settings

logger = logging.getLogger(__name__)


# =============================================
# GoGoJap 分類 → 惠康分類映射
# =============================================
# GoGoJap 賣日本進口食品，主要品類是肉類和海鮮。
# 惠康是本地超市，分類結構不同，需要手動映射。

CATEGORY_MAP = {
    # 肉類
    "豬肉": ["100015-100182-101093"],          # Pork
    "牛肉": ["100015-100182-101092"],          # Beef
    "肉類": ["100015-100182-101093", "100015-100182-101092", "100015-100186-101115"],
    # 海鮮
    "鮮魚": ["100015-100183"],                  # Seafood
    "貝類": ["100015-100183"],
    "蟹類": ["100015-100183"],
    "蝦類": ["100015-100183"],
    "其他海鮮": ["100015-100183"],
    "海鮮": ["100015-100183"],
    # 急凍
    "急凍肉": ["100015-100186-101115"],         # Other Frozen Meat
    "加工肉": ["100015-100186-101115"],
}

# 所有需要爬取的惠康分類（去重）
ALL_CATEGORIES = {
    "100015-100182-101093": "豬肉",
    "100015-100182-101092": "牛肉",
    "100015-100186-101115": "其他急凍肉",
    "100015-100183": "海鮮",
}

# 日本產地/等級前綴（搜索惠康時應移除）
_ORIGIN_PATTERNS = [
    r'北海道', r'宮崎', r'鹿兒島', r'青森', r'岩手',
    r'熊本', r'長崎', r'沖繩', r'廣島', r'挪威',
    r'加拿大', r'澳洲', r'美國', r'日本',
    r'A5', r'A4', r'A3',
    r'GOGOJAP[-\s]*',
    r'GGJ[-\s]*\d*',
]


class WellcomeSearchStrategy:
    """
    惠康搜索策略（本地索引 + 分類瀏覽）

    優先級：
    1. 本地索引（查詢 competitor_products 表，~50ms）
    2. 自動爬取分類頁填充索引 → 再搜本地索引（~60s，首次）
    """

    LOCAL_MIN_RESULTS = 3
    CATEGORY_URL = "https://www.wellcome.com.hk/en/category/{category_id}/{page}.html"

    def __init__(self):
        self.http_client = get_wellcome_http_client()
        self.agent_browser = get_agent_browser_connector()

    # =============================================
    # 關鍵詞簡化（適配惠康商品名稱）
    # =============================================

    @staticmethod
    def simplify_keyword(keyword: str) -> List[str]:
        """
        從日本進口商品名生成惠康可搜的簡化關鍵詞

        「宮崎A5和牛西冷」→ ["和牛西冷", "西冷", "牛"]
        「北海道豬腩」→ ["豬腩", "豬"]
        「急凍松葉蟹肉混合裝（棒肉+肉碎）」→ ["松葉蟹肉", "蟹肉", "蟹"]
        """
        results = []

        # 移除產地/等級前綴
        simplified = keyword
        for pattern in _ORIGIN_PATTERNS:
            simplified = re.sub(pattern, '', simplified, flags=re.IGNORECASE)

        # 移除括號內容和多餘空白
        simplified = re.sub(r'[（(].*?[）)]', '', simplified)
        simplified = re.sub(r'\s+', '', simplified).strip()

        if simplified and len(simplified) >= 2:
            results.append(simplified)

        # 提取核心產品詞（最後 2-3 個中文字）
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', simplified)
        if chinese_chars:
            core = chinese_chars[-1]  # 通常核心詞在最後
            if core and len(core) >= 2 and core != simplified:
                results.append(core)

            # 單字兜底（「豬」「牛」「蟹」「蝦」）
            if len(core) >= 2:
                single = core[-1]
                if single in "豬牛羊雞鴨魚蝦蟹蠔":
                    results.append(single)

        return results if results else [keyword]

    # =============================================
    # Layer 1: 本地索引搜索（多關鍵詞）
    # =============================================

    async def search_local_index(
        self,
        db: AsyncSession,
        keyword: str,
        limit: int = 20,
    ) -> List[WellcomeProduct]:
        """
        從本地 competitor_products 表搜索已爬取的惠康商品

        用簡化關鍵詞逐層搜索，精確 → 寬泛
        """
        from app.models.competitor import Competitor, CompetitorProduct

        keywords = self.simplify_keyword(keyword)
        seen_urls: Set[str] = set()
        products: List[WellcomeProduct] = []

        for kw in keywords:
            if len(products) >= limit:
                break

            search_pattern = f"%{kw}%"
            stmt = (
                select(CompetitorProduct)
                .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
                .where(
                    Competitor.platform == "wellcome",
                    CompetitorProduct.is_active == True,
                    CompetitorProduct.name.ilike(search_pattern),
                )
                .limit(limit - len(products))
            )

            result = await db.execute(stmt)
            rows = result.scalars().all()

            for row in rows:
                if row.url not in seen_urls:
                    seen_urls.add(row.url)
                    products.append(WellcomeProduct(
                        url=row.url,
                        name=row.name,
                        price=None,
                        product_id=extract_product_id(row.url),
                    ))

            if products:
                logger.info(
                    f"wellcome 本地索引: keyword='{kw}' → {len(rows)} 命中"
                )
                break  # 找到結果就不用更寬泛的詞

        logger.info(
            f"wellcome 本地索引搜索: original='{keyword}' → "
            f"keywords={keywords} → {len(products)} 商品"
        )
        return products

    # =============================================
    # Layer 2: 分類瀏覽（替代壞掉的搜索）
    # =============================================

    async def browse_category(
        self,
        db: AsyncSession,
        category_main: str = "",
        category_sub: str = "",
        max_pages: int = 3,
    ) -> int:
        """
        根據商品分類，瀏覽對應的惠康分類頁填充本地索引

        惠康搜索頁返回 500，用分類瀏覽替代。
        首次匹配時自動觸發，結果緩存在本地索引。

        Returns:
            新增的商品數量
        """
        settings = get_settings()
        if not settings.agent_browser_enabled:
            logger.warning("wellcome 分類瀏覽: agent_browser 已禁用")
            return 0

        # 確定要瀏覽哪些惠康分類
        category_ids = set()
        for key in [category_sub, category_main]:
            if key and key in CATEGORY_MAP:
                category_ids.update(CATEGORY_MAP[key])

        # 找不到映射時，爬取所有重點分類
        if not category_ids:
            category_ids = set(ALL_CATEGORIES.keys())
            logger.info(
                f"wellcome 分類瀏覽: 無分類映射 "
                f"(main='{category_main}', sub='{category_sub}'), "
                f"爬取全部 {len(category_ids)} 個分類"
            )

        total_new = 0
        for cat_id in category_ids:
            cat_name = ALL_CATEGORIES.get(cat_id, cat_id)
            try:
                count = await self.crawl_category(
                    db, cat_id, cat_name, max_pages=max_pages
                )
                total_new += count
            except Exception as e:
                logger.warning(f"wellcome 分類瀏覽失敗: {cat_name} - {e}")

        if total_new > 0:
            await db.commit()

        logger.info(f"wellcome 分類瀏覽完成: 新增 {total_new} 商品")
        return total_new

    async def ensure_local_index(
        self,
        db: AsyncSession,
        category_main: str = "",
        category_sub: str = "",
    ) -> int:
        """
        確保本地索引有惠康數據，沒有就自動爬取

        Returns:
            本地索引中的惠康商品總數
        """
        from app.models.competitor import Competitor, CompetitorProduct

        # 檢查本地索引是否有數據
        stmt = (
            select(func.count())
            .select_from(CompetitorProduct)
            .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
            .where(Competitor.platform == "wellcome")
        )
        result = await db.execute(stmt)
        count = result.scalar() or 0

        if count >= 10:
            return count

        # 本地索引太少，自動爬取
        logger.info(
            f"wellcome 本地索引不足 ({count} 商品)，開始自動爬取分類頁"
        )
        new_count = await self.browse_category(
            db, category_main, category_sub, max_pages=3
        )

        return count + new_count

    # =============================================
    # 後台任務：分類頁爬取
    # =============================================

    async def crawl_category(
        self,
        db: AsyncSession,
        category_id: str,
        category_name: str = "",
        max_pages: int = 5,
    ) -> int:
        """
        爬取惠康分類頁面，填充本地索引

        流程：
        1. Playwright 導航分類頁
        2. 提取所有產品 URL
        3. 翻頁（最多 max_pages 頁）
        4. HTTP GET JSON-LD 取詳情
        5. 寫入 competitor_products 表

        Returns:
            寫入/更新的商品數量
        """
        from app.models.competitor import Competitor, CompetitorProduct

        all_urls: Set[str] = set()

        for page_num in range(1, max_pages + 1):
            page_url = self.CATEGORY_URL.format(
                category_id=category_id, page=page_num
            )

            try:
                urls = await self.agent_browser.discover_wellcome_products(
                    page_url, max_products=50
                )
                if not urls:
                    break  # 空頁 = 已到末頁
                all_urls.update(urls)
                logger.info(
                    f"wellcome 分類爬取: {category_name} "
                    f"第{page_num}頁 → {len(urls)} URLs"
                )
            except Exception as e:
                logger.warning(
                    f"wellcome 分類爬取失敗: {category_name} "
                    f"第{page_num}頁 - {e}"
                )
                break

        if not all_urls:
            return 0

        # 批量取 JSON-LD
        products = await self.http_client.batch_fetch_products(list(all_urls))
        valid_products = [p for p in products if p.name]

        # 獲取或創建 Wellcome Competitor
        stmt = select(Competitor).where(
            Competitor.platform == "wellcome"
        ).limit(1)
        result = await db.execute(stmt)
        competitor = result.scalar_one_or_none()

        if not competitor:
            competitor = Competitor(
                name="Wellcome 惠康",
                platform="wellcome",
                base_url="https://www.wellcome.com.hk",
                is_active=True,
            )
            db.add(competitor)
            await db.flush()

        # 寫入 CompetitorProduct
        count = 0
        for p in valid_products:
            normalized = normalize_url(p.url)

            stmt = select(CompetitorProduct).where(
                CompetitorProduct.url == normalized
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                existing.name = p.name
                existing.sku = p.product_id
            else:
                cp = CompetitorProduct(
                    competitor_id=competitor.id,
                    name=p.name,
                    url=normalized,
                    sku=p.product_id,
                    is_active=True,
                )
                db.add(cp)
                count += 1

        await db.flush()

        logger.info(
            f"wellcome 分類爬取完成: {category_name} → "
            f"{len(all_urls)} URLs → {count} 新商品"
        )
        return count
