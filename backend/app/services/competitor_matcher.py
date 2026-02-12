# =============================================
# Competitor Matcher Service
# 自動化對手搜索與智能匹配服務
# Market Response Center (MRC) - Phase 2
# =============================================
"""
核心功能：
1. 根據 GogoJap SKU 的 name_ja/name_en 自動搜索競品
2. 使用 LLM 智能判斷商品是否為同級商品
3. 自動建立 ProductCompetitorMapping 關聯
"""

import re
import json
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductCompetitorMapping
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot
from app.connectors.firecrawl import get_firecrawl_connector, ProductInfo
from app.connectors.claude import get_claude_connector
from app.connectors.hktv_http_client import get_hktv_http_client
from app.connectors.hktv_api import get_hktv_api_client, HKTVProduct
from app.connectors.hktv_scraper import get_hktv_scraper, HKTVUrlParser
from app.connectors.agent_browser import get_agent_browser_connector
from app.config import get_settings


# =============================================
# Data Classes
# =============================================

@dataclass
class MatchCandidate:
    """匹配候選項"""
    url: str
    name: str
    price: Optional[Decimal]
    product_info: Optional[ProductInfo] = None


@dataclass
class MatchResult:
    """匹配結果"""
    product_id: str
    product_name: str
    candidate_url: str
    candidate_name: str
    match_confidence: float  # 0.0 - 1.0
    match_reason: str
    is_match: bool


# =============================================
# Search Strategies
# =============================================

class HKTVMallSearchStrategy:
    """
    HKTVmall 三層搜索策略

    優先級：
    1. HKTVmall Product API（~200ms，零成本，帶價格）
    2. Playwright 瀏覽器搜索（~25s，零成本，只有 URL）
    3. Firecrawl（1 credit，備用）
    """

    # API 結果信任閾值：低於此數量降級到瀏覽器搜索
    # 改為 1：即使只有 1 個結果也進入 Claude 判斷，避免無謂降級
    API_MIN_RESULTS = 1

    BASE_URL = "https://www.hktvmall.com"
    SEARCH_URL = "https://www.hktvmall.com/hktv/zh/search_a?keyword={query}"

    def __init__(self):
        self.firecrawl = get_firecrawl_connector()
        self.http_client = get_hktv_http_client()
        self.hktv_api = get_hktv_api_client()
        self.agent_browser = get_agent_browser_connector()

    def build_search_url(self, query: str) -> str:
        """構建搜索 URL"""
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        return self.SEARCH_URL.format(query=encoded_query)

    async def search_via_api(self, keyword: str, limit: int = 20) -> List[HKTVProduct]:
        """
        用 HKTVmall Product API 搜索（第一層）

        返回帶價格的結構化商品數據。
        當結果不足 API_MIN_RESULTS 時返回空列表，由調用方降級。
        """
        try:
            products = await self.hktv_api.search_products(keyword, page_size=limit)
            if len(products) >= self.API_MIN_RESULTS:
                logger.info(f"hktv-api 搜索成功: keyword='{keyword}' → {len(products)} 商品")
                return products
            logger.info(
                f"hktv-api 結果不足({len(products)}<{self.API_MIN_RESULTS})，降級: keyword='{keyword}'"
            )
            return []
        except Exception as e:
            logger.warning(f"hktv-api 異常: keyword='{keyword}' - {e}")
            return []

    async def extract_product_urls_from_search(self, search_url: str, limit: int = 10) -> List[str]:
        """
        從搜索結果頁面提取商品 URL（第二/三層）

        策略：Playwright（主路線） → Firecrawl（備用）
        Playwright 能穩定處理 SPA 的 JS 渲染與 lazy load
        """
        settings = get_settings()

        # 第二層：Playwright 瀏覽器搜索
        if settings.agent_browser_enabled:
            try:
                urls = await self.agent_browser.discover_hktv_products(
                    search_url, max_products=limit
                )
                logger.info(f"playwright 完成: {len(urls)} URLs from {search_url}")
                return urls
            except Exception as e:
                logger.warning(
                    f"playwright 異常，降級到 Firecrawl: {search_url} - {e}"
                )

        # 第三層：Firecrawl（Playwright 異常 或 被禁用時使用）
        try:
            urls = self.firecrawl.discover_hktv_products(search_url, max_products=limit)
            return urls
        except Exception:
            logger.error(
                f"從搜索結果提取商品 URL 失敗: {search_url}",
                exc_info=True,
            )
            return []

    async def validate_and_filter_urls(self, urls: List[str]) -> List[str]:
        """
        用 HTTP HEAD 請求驗證 URL 有效性（0 credits）

        過濾掉 404/無效的 URL，避免浪費 Firecrawl credits
        """
        if not urls:
            return []

        valid_flags = await self.http_client.batch_validate_urls(urls)
        return [url for url, valid in zip(urls, valid_flags) if valid]


# =============================================
# Claude Matcher
# =============================================

class ClaudeMatcher:
    """使用 Claude 進行商品匹配判斷"""
    
    def __init__(self):
        self.claude = get_claude_connector()
    
    def build_match_prompt(
        self,
        our_product: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> str:
        """構建匹配判斷 Prompt"""
        return f"""
你是一位專業的日本海鮮/食材專家。請判斷以下兩個商品是否為「同級商品」。

「同級商品」定義：
- 同類型產品（如：都是鮪魚/吞拿魚）
- 相似規格（如：重量差異不超過 50%）
- 相似等級（如：都是 A5 級/都是野生/都是養殖）

---

我方商品（GogoJap）:
- 中文名: {our_product.get('name_zh', 'N/A')}
- 日文名: {our_product.get('name_ja', 'N/A')}
- 英文名/規格: {our_product.get('name_en', 'N/A')}
- 分類: {our_product.get('category_main', '')} > {our_product.get('category_sub', '')}
- 單位: {our_product.get('unit', 'N/A')}

---

對手商品:
- 名稱: {candidate.get('name', 'N/A')}
- 價格: {candidate.get('price', 'N/A')}
- 描述: {candidate.get('description', 'N/A')[:500] if candidate.get('description') else 'N/A'}

---

請以 JSON 格式回答：
{{
  "is_match": true/false,
  "confidence": 0.0-1.0,
  "reason": "判斷理由（簡短說明）",
  "key_differences": ["差異1", "差異2"] // 如果不匹配，列出主要差異
}}

只輸出 JSON，不要其他內容。
"""
    
    def judge_match(
        self,
        our_product: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> MatchResult:
        """判斷兩個商品是否匹配"""
        prompt = self.build_match_prompt(our_product, candidate)
        
        try:
            if not self.claude.client:
                # 無 API Key，使用啟發式匹配
                return self._heuristic_match(our_product, candidate)
            
            max_tok = 4000 if "thinking" in self.claude.model else 500
            message = self.claude.client.messages.create(
                model=self.claude.model,
                max_tokens=max_tok,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # thinking 模型返回多個 block，取最後一個 text block
            response_text = ""
            for block in message.content:
                if getattr(block, "type", None) == "text":
                    response_text = block.text
            if not response_text:
                response_text = message.content[0].text if message.content else "{}"
            
            # 解析 JSON 響應
            # 嘗試提取 JSON 部分
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {}
            
            return MatchResult(
                product_id=str(our_product.get('id', '')),
                product_name=our_product.get('name_zh', ''),
                candidate_url=candidate.get('url', ''),
                candidate_name=candidate.get('name', ''),
                match_confidence=float(result.get('confidence', 0.0)),
                match_reason=result.get('reason', ''),
                is_match=result.get('is_match', False)
            )
            
        except Exception as e:
            logger.error(
                f"Claude 匹配判斷失敗: {str(e)}",
                exc_info=True,
                extra={
                    "our_product": our_product.get('name_zh', ''),
                    "candidate": candidate.get('name', ''),
                }
            )
            return self._heuristic_match(our_product, candidate)
    
    # =============================================
    # 批量匹配（N 個候選 → 1 次 API 呼叫）
    # =============================================

    def batch_judge_match(
        self,
        our_product: Dict[str, Any],
        candidates: List[Dict[str, Any]],
    ) -> List[MatchResult]:
        """
        批量匹配：N 個候選商品 → 1 次 Claude API 呼叫

        之前：10 個候選 × 1-3s/次 = 10-30s
        現在：1 次呼叫 ≈ 2-4s
        """
        if not candidates:
            return []

        if not self.claude.client:
            logger.info("Claude API Key 未配置，使用啟發式批量匹配")
            return [self._heuristic_match(our_product, c) for c in candidates]

        # 單個候選 → 直接用單次匹配（更簡潔、更省 token）
        if len(candidates) == 1:
            return [self.judge_match(our_product, candidates[0])]

        prompt = self._build_batch_prompt(our_product, candidates)

        try:
            # thinking 模型需要更大的 max_tokens（thinking 本身消耗 token）
            max_tok = 8000 if "thinking" in self.claude.model else 2000
            message = self.claude.client.messages.create(
                model=self.claude.model,
                max_tokens=max_tok,
                messages=[{"role": "user", "content": prompt}]
            )

            # thinking 模型返回 [thinking_block, text_block]，取最後一個 text
            response_text = ""
            for block in message.content:
                if getattr(block, "type", None) == "text":
                    response_text = block.text
            if not response_text:
                response_text = message.content[0].text if message.content else "[]"

            # 解析 JSON 數組
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if not json_match:
                logger.warning("Claude 批量匹配返回格式異常，降級到啟發式")
                return [self._heuristic_match(our_product, c) for c in candidates]

            try:
                results_array = json.loads(json_match.group())
                if not isinstance(results_array, list):
                    logger.warning(f"Claude 批量匹配返回非數組: {type(results_array)}")
                    return [self._heuristic_match(our_product, c) for c in candidates]
            except json.JSONDecodeError as e:
                logger.error(
                    f"Claude 批量匹配 JSON 解析失敗: {e}\n"
                    f"原始響應: {response_text[:500]}"
                )
                return [self._heuristic_match(our_product, c) for c in candidates]

            # 映射回 MatchResult（index 是 1-based）
            product_id = str(our_product.get('id', ''))
            product_name = our_product.get('name_zh', '')
            match_results = []

            for item in results_array:
                idx = item.get("index", 0) - 1
                if not (0 <= idx < len(candidates)):
                    logger.warning(
                        f"Claude 返回無效 index={item.get('index')} "
                        f"(candidates={len(candidates)})"
                    )
                    continue

                c = candidates[idx]
                match_results.append(MatchResult(
                    product_id=product_id,
                    product_name=product_name,
                    candidate_url=c.get('url', ''),
                    candidate_name=c.get('name', ''),
                    match_confidence=float(item.get('confidence', 0.0)),
                    match_reason=item.get('reason', ''),
                    is_match=item.get('is_match', False),
                ))

            if len(match_results) < len(candidates):
                logger.info(
                    f"Claude 批量匹配: {len(match_results)}/{len(candidates)} 項有結果"
                )

            return match_results

        except Exception as e:
            logger.error(f"Claude 批量匹配失敗: {e}", exc_info=True)
            return [self._heuristic_match(our_product, c) for c in candidates]

    def _build_batch_prompt(
        self,
        our_product: Dict[str, Any],
        candidates: List[Dict[str, Any]],
    ) -> str:
        """構建批量匹配 Prompt"""
        lines = []
        for i, c in enumerate(candidates, 1):
            name = c.get('name', 'N/A')
            price = c.get('price', 'N/A')
            desc = c.get('description', '')
            desc_part = f" | 描述: {desc[:100]}" if desc else ""
            lines.append(f"#{i} {name} | 價格: {price}{desc_part}")

        candidates_text = "\n".join(lines)

        return f"""你是一位專業的日本海鮮/食材專家。請判斷以下每個對手商品是否與我方商品為「同級商品」。

「同級商品」定義：
- 同類型產品（如：都是鮪魚/吞拿魚）
- 相似規格（如：重量差異不超過 50%）
- 相似等級（如：都是 A5 級/都是野生/都是養殖）

---

我方商品（GogoJap）:
- 中文名: {our_product.get('name_zh', 'N/A')}
- 日文名: {our_product.get('name_ja', 'N/A')}
- 英文名/規格: {our_product.get('name_en', 'N/A')}
- 分類: {our_product.get('category_main', '')} > {our_product.get('category_sub', '')}
- 單位: {our_product.get('unit', 'N/A')}

---

對手商品清單：

{candidates_text}

---

請以 JSON 數組格式回答（每個對手商品一項）：
[
  {{"index": 1, "is_match": true, "confidence": 0.85, "reason": "判斷理由"}},
  {{"index": 2, "is_match": false, "confidence": 0.2, "reason": "判斷理由"}}
]

只輸出 JSON 數組，不要其他內容。"""

    def _heuristic_match(
        self,
        our_product: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> MatchResult:
        """啟發式匹配（無 API Key 時使用）"""
        candidate_name = (candidate.get('name') or '').lower()

        # 關鍵字收集：保留產地和等級等核心特徵詞
        keywords = []

        # 從中文名提取關鍵字（只去括號和數量，保留產地/等級）
        zh_name = our_product.get('name_zh') or ''
        if zh_name:
            core = re.sub(r'(\(.*?\)|（.*?）|\d+\w*)', '', zh_name).strip()
            if core and len(core) >= 2:
                keywords.append(core.lower())

        # 日文名
        ja_name = our_product.get('name_ja') or ''
        if ja_name:
            keywords.append(ja_name.lower())

        # 英文名
        en_name = our_product.get('name_en') or ''
        if en_name:
            en_words = re.findall(r'\b[a-zA-Z]{3,}\b', en_name.lower())
            keywords.extend(en_words[:3])

        # 計算匹配分數
        matches = sum(1 for kw in keywords if kw in candidate_name)
        confidence = matches / max(len(keywords), 1)

        is_match = confidence >= 0.4

        return MatchResult(
            product_id=str(our_product.get('id', '')),
            product_name=our_product.get('name_zh', ''),
            candidate_url=candidate.get('url', ''),
            candidate_name=candidate.get('name', ''),
            match_confidence=confidence,
            match_reason=f"啟發式匹配: {matches}/{len(keywords)} 關鍵字匹配",
            is_match=is_match
        )


# =============================================
# Main Service
# =============================================

class CompetitorMatcherService:
    """對手匹配服務（優化版：三層抓取架構）"""

    def __init__(self):
        self.firecrawl = get_firecrawl_connector()
        self.hktv_strategy = HKTVMallSearchStrategy()
        self.matcher = ClaudeMatcher()
        self.http_client = get_hktv_http_client()
        self.hktv_scraper = get_hktv_scraper()

    def generate_search_queries(self, product: Product) -> List[str]:
        """
        為商品生成搜索關鍵字（v3：保留產品特徵詞）

        核心原則：
        - 產地名（宮崎、北海道、挪威）對食品來說是核心特徵，不刪除
        - 只移除純噪音（括號備註、物流描述）
        - 完整中文名優先（搜索引擎自帶模糊匹配）
        - 輕度清潔版本作為備用
        """
        queries = []

        # ==================== 輕度清潔（只去噪音，保留特徵）====================

        # 需要移除的純噪音（不影響搜索精度的修飾詞）
        noise_patterns = [
            r'\(.*?\)', r'\[.*?\]', r'（.*?）',    # 括號內容
            r'\d+g\b', r'\d+kg\b', r'\d+ml\b',     # 重量/容量
            r'\d+片', r'\d+條', r'\d+包', r'\d+盒', # 數量
            r'直送', r'空運',                        # 物流描述
        ]

        def light_clean(text: str) -> str:
            """輕度清潔：只去噪音，保留產地、等級、核心特徵"""
            if not text:
                return ""
            for pattern in noise_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            return re.sub(r'\s+', ' ', text).strip()

        # ==================== 生成搜索關鍵詞 ====================

        # 策略 1: 完整中文名（最精確，搜索引擎自帶模糊匹配）
        if product.name_zh:
            cleaned_zh = light_clean(product.name_zh)
            if cleaned_zh and len(cleaned_zh) >= 2:
                queries.append(cleaned_zh)

        # 策略 2: 分類子類（覆蓋面廣的備用查詢）
        category_sub = getattr(product, 'category_sub', None)
        if category_sub:
            queries.append(category_sub)

        # 策略 3: 英文名核心詞彙
        if product.name_en:
            cleaned_en = light_clean(product.name_en)
            words = cleaned_en.split()[:3]
            if words:
                queries.append(' '.join(words))

        # 策略 4: 日文名
        if product.name_ja:
            cleaned_ja = light_clean(product.name_ja)
            if cleaned_ja:
                queries.append(cleaned_ja)

        # 策略 5: 完整原始名稱兜底
        if not queries:
            if product.name_zh:
                queries.append(product.name_zh)
            elif product.name_en:
                queries.append(product.name_en)
            elif product.name_ja:
                queries.append(product.name_ja)

        # 去重並保留順序
        seen = set()
        unique_queries = []
        for q in queries:
            if q and q not in seen:
                seen.add(q)
                unique_queries.append(q)

        return unique_queries

    async def _check_price_freshness(
        self,
        db: AsyncSession,
        url: str
    ) -> bool:
        """
        檢查該商品是否在緩存有效期內已有價格數據

        Returns:
            True = 數據新鮮，不需要重新抓取
        """
        settings = get_settings()
        ttl_seconds = settings.hktv_price_cache_ttl

        # 查找該 URL 對應的 CompetitorProduct
        stmt = select(CompetitorProduct).where(CompetitorProduct.url == url)
        result = await db.execute(stmt)
        cp = result.scalar_one_or_none()

        if not cp:
            return False

        # 查找最近的 PriceSnapshot
        from sqlalchemy import desc
        stmt = (
            select(PriceSnapshot)
            .where(PriceSnapshot.competitor_product_id == cp.id)
            .order_by(desc(PriceSnapshot.scraped_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        latest = result.scalar_one_or_none()

        if not latest:
            return False

        # 檢查是否在 TTL 內
        age = (datetime.utcnow() - latest.scraped_at).total_seconds()
        return age < ttl_seconds

    async def find_competitors_for_product(
        self,
        db: AsyncSession,
        product: Product,
        platform: str = "hktvmall",
        max_candidates: int = 5
    ) -> List[MatchResult]:
        """
        為單個商品尋找競品（三層搜索架構）

        搜索策略（按優先級）：
        1. HKTVmall Product API — ~200ms，零成本，直接帶價格
        2. Playwright 瀏覽器搜索 — ~25s，零成本，只有 URL
        3. Firecrawl — 1 credit/次，最後手段

        當 API 返回足夠結果時，可直接跳過 URL 驗證、metadata 取得、價格抓取，
        大幅降低延遲和成本。
        """
        queries = self.generate_search_queries(product)
        if not queries:
            return []

        our_product_dict = {
            "id": str(product.id),
            "name_zh": product.name_zh,
            "name_ja": getattr(product, 'name_ja', ''),
            "name_en": getattr(product, 'name_en', ''),
            "category_main": getattr(product, 'category_main', ''),
            "category_sub": getattr(product, 'category_sub', ''),
            "unit": getattr(product, 'unit', ''),
        }

        # ==================== 嘗試 API 快速路徑 ====================
        api_results = await self._find_via_api(
            queries, our_product_dict, db, max_candidates
        )
        if api_results:
            return api_results

        # ==================== 降級到瀏覽器搜索路徑 ====================
        return await self._find_via_browser(
            queries, our_product_dict, db, platform, max_candidates
        )

    async def _find_via_api(
        self,
        queries: List[str],
        our_product_dict: Dict[str, Any],
        db: AsyncSession,
        max_candidates: int,
    ) -> List[MatchResult]:
        """
        API 快速路徑：用 HKTVmall Product API 搜索 + 匹配

        優勢：~200ms，帶價格，無需額外抓取
        """
        results = []

        # 並行搜索多個關鍵詞（~200ms 完成，而非串行 400ms）
        api_tasks = [
            self.hktv_strategy.search_via_api(query, limit=max_candidates * 2)
            for query in queries[:2]
        ]
        api_results_lists = await asyncio.gather(*api_tasks)
        api_products: List[HKTVProduct] = [
            p for sublist in api_results_lists for p in sublist
        ]

        if not api_products:
            return []

        # 去重（按 SKU）
        seen_skus = set()
        unique_products = []
        for p in api_products:
            if p.sku not in seen_skus:
                seen_skus.add(p.sku)
                unique_products.append(p)

        # Claude 批量匹配（N 個候選 → 1 次 API 呼叫）
        candidate_dicts = [
            {
                "url": p.url,
                "name": p.name,
                "description": "",
                "price": str(p.price) if p.price else "未知",
            }
            for p in unique_products[:max_candidates * 2]
        ]

        all_matches = self.matcher.batch_judge_match(our_product_dict, candidate_dicts)

        # 動態閾值：候選少時降低門檻（精確搜索往往只返回 1-2 個結果）
        n = len(candidate_dicts)
        threshold = 0.3 if n <= 2 else 0.4 if n <= 5 else 0.5
        results = [
            r for r in all_matches
            if r.is_match and r.match_confidence >= threshold
        ]

        if results:
            logger.info(
                f"API 快速路徑成功: {len(results)} 匹配 (threshold={threshold}) "
                f"(product={our_product_dict.get('name_zh', '')})"
            )

        return results

    async def _find_via_browser(
        self,
        queries: List[str],
        our_product_dict: Dict[str, Any],
        db: AsyncSession,
        platform: str,
        max_candidates: int,
    ) -> List[MatchResult]:
        """
        瀏覽器搜索路徑：Playwright/Firecrawl URL 發現 → metadata → Claude 匹配 → 價格抓取
        """
        results = []
        candidate_urls = set()

        for query in queries[:2]:
            if platform == "hktvmall":
                search_url = self.hktv_strategy.build_search_url(query)
                urls = await self.hktv_strategy.extract_product_urls_from_search(
                    search_url, limit=max_candidates
                )
                candidate_urls.update(urls)

        if not candidate_urls:
            return results

        candidate_urls = list(candidate_urls)[:max_candidates * 2]

        # HTTP 驗證 + metadata（0 credits）
        valid_urls = await self.hktv_strategy.validate_and_filter_urls(candidate_urls)
        if not valid_urls:
            return results

        metadata_list = await self.http_client.batch_fetch_metadata(valid_urls)

        # Claude 批量匹配
        candidate_dicts = [
            {
                "url": m.url,
                "name": m.name,
                "description": m.description or "",
                "price": "需要 JS 渲染取得",
            }
            for m in metadata_list
            if m.valid and m.name
        ]

        if candidate_dicts:
            all_matches = self.matcher.batch_judge_match(
                our_product_dict, candidate_dicts
            )
            # 動態閾值：同 _find_via_api 一致
            n = len(candidate_dicts)
            threshold = 0.3 if n <= 2 else 0.4 if n <= 5 else 0.5
            results = [
                r for r in all_matches
                if r.is_match and r.match_confidence >= threshold
            ]

        # 對匹配商品取價格（按需 1 credit）
        for result_item in results:
            url = result_item.candidate_url

            is_fresh = await self._check_price_freshness(db, url)
            if is_fresh:
                logger.info(f"價格數據仍然新鮮，跳過 Firecrawl: {url}")
                continue

            try:
                product_data = await self.hktv_scraper.smart_scrape_product(
                    url, need_price=True
                )
                logger.info(
                    f"取得價格: {product_data.name} = ${product_data.price}"
                )
            except Exception as e:
                logger.warning(f"取得價格失敗: {url} - {e}")

        return results

    # =============================================
    # 持久化：匹配結果寫入數據庫
    # =============================================

    async def save_match_to_db(
        self,
        db: AsyncSession,
        product_id: str,
        match_result: MatchResult,
    ) -> Optional[ProductCompetitorMapping]:
        """
        將匹配結果持久化到數據庫（get-or-create 模式）

        流程：
        1. 驗證參數（product_id → UUID，candidate_url 非空）
        2. URL 標準化
        3. 取得或創建 Competitor（platform='hktvmall'）
        4. 取得或創建 CompetitorProduct（按 normalized URL）
        5. 取得或創建 ProductCompetitorMapping（按 product_id + competitor_product_id）

        只做 flush()，不做 commit()——由 caller 控制事務邊界。
        異常時 rollback() + return None，不中斷 caller 的循環。
        """
        import uuid as _uuid

        try:
            # ==================== 1. 驗證 ====================
            try:
                pid = _uuid.UUID(product_id)
            except (ValueError, AttributeError):
                logger.warning(f"save_match_to_db: 無效 product_id={product_id}")
                return None

            if not match_result.candidate_url:
                logger.warning("save_match_to_db: candidate_url 為空")
                return None

            # ==================== 2. URL 標準化 ====================
            normalized_url = HKTVUrlParser.normalize_url(match_result.candidate_url)

            # ==================== 3. Competitor（get-or-create）====================
            stmt = select(Competitor).where(Competitor.platform == "hktvmall").limit(1)
            result = await db.execute(stmt)
            competitor = result.scalar_one_or_none()

            if not competitor:
                competitor = Competitor(
                    name="HKTVmall",
                    platform="hktvmall",
                    base_url="https://www.hktvmall.com",
                    is_active=True,
                )
                db.add(competitor)
                await db.flush()
                logger.info(f"創建 Competitor: platform=hktvmall id={competitor.id}")

            # ==================== 4. CompetitorProduct（get-or-create）====================
            stmt = select(CompetitorProduct).where(
                CompetitorProduct.url == normalized_url
            )
            result = await db.execute(stmt)
            comp_product = result.scalar_one_or_none()

            if not comp_product:
                sku = HKTVUrlParser.extract_sku(normalized_url)
                comp_product = CompetitorProduct(
                    competitor_id=competitor.id,
                    name=match_result.candidate_name or "Unknown",
                    url=normalized_url,
                    sku=sku,
                    is_active=True,
                )
                db.add(comp_product)
                try:
                    await db.flush()
                except IntegrityError:
                    # UNIQUE 衝突：其他並行請求已創建
                    await db.rollback()
                    stmt = select(CompetitorProduct).where(
                        CompetitorProduct.url == normalized_url
                    )
                    result = await db.execute(stmt)
                    comp_product = result.scalar_one_or_none()
                    if not comp_product:
                        logger.error(
                            f"save_match_to_db: CompetitorProduct UNIQUE 衝突後仍找不到: "
                            f"{normalized_url}"
                        )
                        return None

                logger.info(
                    f"創建 CompetitorProduct: url={normalized_url} sku={comp_product.sku}"
                )

            # ==================== 5. ProductCompetitorMapping（get-or-create）====================
            stmt = select(ProductCompetitorMapping).where(
                and_(
                    ProductCompetitorMapping.product_id == pid,
                    ProductCompetitorMapping.competitor_product_id == comp_product.id,
                )
            )
            result = await db.execute(stmt)
            mapping = result.scalar_one_or_none()

            new_confidence = Decimal(str(round(match_result.match_confidence, 2)))

            if mapping:
                # 已存在：只在信心度更高時更新
                if mapping.match_confidence is None or new_confidence > mapping.match_confidence:
                    mapping.match_confidence = new_confidence
                    mapping.notes = match_result.match_reason
                    await db.flush()
                    logger.info(
                        f"更新 mapping: product={product_id} → {normalized_url} "
                        f"confidence={new_confidence}"
                    )
            else:
                mapping = ProductCompetitorMapping(
                    product_id=pid,
                    competitor_product_id=comp_product.id,
                    match_confidence=new_confidence,
                    is_verified=False,
                    notes=match_result.match_reason,
                )
                db.add(mapping)
                try:
                    await db.flush()
                except IntegrityError:
                    # uq_product_competitor 衝突：並行寫入
                    await db.rollback()
                    stmt = select(ProductCompetitorMapping).where(
                        and_(
                            ProductCompetitorMapping.product_id == pid,
                            ProductCompetitorMapping.competitor_product_id == comp_product.id,
                        )
                    )
                    result = await db.execute(stmt)
                    mapping = result.scalar_one_or_none()
                    if not mapping:
                        logger.error(
                            f"save_match_to_db: mapping UNIQUE 衝突後仍找不到: "
                            f"product={product_id} comp={comp_product.id}"
                        )
                        return None

                logger.info(
                    f"創建 mapping: product={product_id} → {normalized_url} "
                    f"confidence={new_confidence}"
                )

            return mapping

        except Exception as e:
            logger.error(
                f"save_match_to_db 異常: product={product_id} "
                f"url={match_result.candidate_url} - {e}",
                exc_info=True,
            )
            try:
                await db.rollback()
            except Exception:
                pass
            return None
