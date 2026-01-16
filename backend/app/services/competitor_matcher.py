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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product, ProductCompetitorMapping
from app.models.competitor import Competitor, CompetitorProduct, PriceSnapshot
from app.connectors.firecrawl import get_firecrawl_connector, ProductInfo
from app.connectors.claude import get_claude_connector


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
    """HKTVmall 搜索策略"""
    
    BASE_URL = "https://www.hktvmall.com"
    SEARCH_URL = "https://www.hktvmall.com/hktv/zh/search?q={query}"
    
    def __init__(self):
        self.firecrawl = get_firecrawl_connector()
    
    def build_search_url(self, query: str) -> str:
        """構建搜索 URL"""
        # URL encode the query
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        return self.SEARCH_URL.format(query=encoded_query)
    
    def extract_product_urls_from_search(self, search_url: str, limit: int = 10) -> List[str]:
        """從搜索結果頁面提取商品 URL"""
        try:
            urls = self.firecrawl.discover_hktv_products(search_url, max_products=limit)
            return urls
        except Exception as e:
            logger.error(
                f"從搜索結果提取商品 URL 失敗: {search_url}",
                exc_info=True,
                extra={"search_url": search_url, "limit": limit}
            )
            return []


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
            
            message = self.claude.client.messages.create(
                model=self.claude.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
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
    
    def _heuristic_match(
        self,
        our_product: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> MatchResult:
        """啟發式匹配（無 API Key 時使用）"""
        our_name = (our_product.get('name_zh', '') + ' ' + 
                   our_product.get('name_ja', '') + ' ' + 
                   our_product.get('name_en', '')).lower()
        
        candidate_name = candidate.get('name', '').lower()
        
        # 簡單關鍵字匹配
        keywords = []
        
        # 從日文名提取關鍵字
        ja_name = our_product.get('name_ja', '')
        if ja_name:
            keywords.append(ja_name.lower())
        
        # 從英文名提取關鍵字
        en_name = our_product.get('name_en', '')
        if en_name:
            # 提取主要詞彙
            en_words = re.findall(r'\b[a-zA-Z]{4,}\b', en_name.lower())
            keywords.extend(en_words[:3])
        
        # 計算匹配分數
        matches = sum(1 for kw in keywords if kw in candidate_name)
        confidence = matches / max(len(keywords), 1)
        
        is_match = confidence >= 0.5
        
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
    """對手匹配服務"""
    
    def __init__(self):
        self.firecrawl = get_firecrawl_connector()
        self.hktv_strategy = HKTVMallSearchStrategy()
        self.matcher = ClaudeMatcher()
    
    def generate_search_queries(self, product: Product) -> List[str]:
        """為商品生成搜索關鍵字"""
        queries = []
        
        # 優先使用日文名（最精準）
        if product.name_ja:
            queries.append(product.name_ja)
        
        # 次要使用英文名的主要部分
        if product.name_en:
            # 提取英文名中的主要詞彙（排除規格數字）
            main_words = re.sub(r'\([^)]*\)', '', product.name_en)  # 移除括號內容
            main_words = re.sub(r'\d+.*$', '', main_words).strip()  # 移除數字及之後內容
            if main_words:
                queries.append(main_words)
        
        # 最後使用中文名
        if product.name_zh:
            queries.append(product.name_zh)
        
        return queries
    
    async def find_competitors_for_product(
        self,
        db: AsyncSession,
        product: Product,
        platform: str = "hktvmall",
        max_candidates: int = 5
    ) -> List[MatchResult]:
        """為單個商品尋找競品"""
        results = []
        
        # 生成搜索關鍵字
        queries = self.generate_search_queries(product)
        
        if not queries:
            return results
        
        # 搜索競品
        candidate_urls = set()
        
        for query in queries[:2]:  # 只使用前兩個最佳關鍵字
            if platfor
