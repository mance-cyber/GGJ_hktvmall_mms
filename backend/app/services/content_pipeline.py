# =============================================
# 統一內容生成流水線 (Content Pipeline)
# =============================================
# 整合 文案生成 → SEO 優化 → GEO 結構化數據
# 一次輸入產品資訊，輸出完整的內容包

import uuid
import json
import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product
from app.models.content import AIContent
from app.models.seo import SEOContent, StructuredData
from app.models.database import utcnow
from app.services.ai_service import AIAnalysisService, AISettingsService


# =============================================
# 流水線階段定義
# =============================================

class PipelineStage(str, Enum):
    """流水線階段"""
    CONTENT = "content"      # 文案生成
    SEO = "seo"              # SEO 優化
    GEO = "geo"              # GEO 結構化數據


# =============================================
# 結果數據結構
# =============================================

@dataclass
class ContentResult:
    """文案生成結果"""
    title: str = ""
    selling_points: List[str] = field(default_factory=list)
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    tone: str = "professional"


@dataclass
class SEOResult:
    """SEO 優化結果"""
    meta_title: str = ""           # max 70 chars
    meta_description: str = ""     # max 160 chars
    primary_keyword: str = ""
    secondary_keywords: List[str] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    seo_score: int = 0
    score_breakdown: Dict[str, int] = field(default_factory=dict)
    og_title: str = ""
    og_description: str = ""


@dataclass
class GEOResult:
    """GEO 結構化數據結果"""
    product_schema: Dict[str, Any] = field(default_factory=dict)
    faq_schema: Optional[Dict[str, Any]] = None
    breadcrumb_schema: Optional[Dict[str, Any]] = None
    ai_summary: str = ""
    ai_facts: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    """流水線完整結果"""
    success: bool = True
    product_info: Dict[str, Any] = field(default_factory=dict)

    # 各階段結果
    content: Optional[ContentResult] = None
    seo: Optional[SEOResult] = None
    geo: Optional[GEOResult] = None

    # 執行的階段
    stages_executed: List[str] = field(default_factory=list)

    # 存儲的記錄 ID
    content_id: Optional[uuid.UUID] = None
    seo_content_id: Optional[uuid.UUID] = None
    structured_data_id: Optional[uuid.UUID] = None

    # 元數據
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

    一次輸入產品資訊，可選擇性執行：
    1. 文案生成 (Content) - 標題、賣點、描述
    2. SEO 優化 - Meta 標籤、關鍵詞、評分
    3. GEO 結構化數據 - Schema.org JSON-LD

    各階段結果會自動傳遞，避免重複輸入
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
        stages: Optional[Set[PipelineStage]] = None,
        language: str = "zh-HK",
        tone: str = "professional",
        include_faq: bool = False,
        save_to_db: bool = True,
    ) -> PipelineResult:
        """
        執行內容生成流水線

        Args:
            product_id: 產品 ID（從數據庫獲取）
            product_info: 產品信息字典（手動提供）
            stages: 要執行的階段，默認全部
            language: 目標語言
            tone: 文案語氣 (professional/casual/luxury)
            include_faq: GEO 階段是否生成 FAQ Schema
            save_to_db: 是否保存到數據庫

        Returns:
            PipelineResult 包含所有生成內容
        """
        start_time = datetime.now()

        # 默認執行所有階段
        if stages is None:
            stages = {PipelineStage.CONTENT, PipelineStage.SEO, PipelineStage.GEO}

        result = PipelineResult()

        # 獲取產品信息
        product_data = await self._get_product_data(product_id, product_info)
        if not product_data:
            result.success = False
            result.error = "必須提供 product_id 或 product_info"
            return result

        result.product_info = product_data

        # Stage 1: 文案生成
        if PipelineStage.CONTENT in stages:
            content_result = await self._stage_content(product_data, language, tone)
            result.content = content_result
            result.stages_executed.append("content")

        # Stage 2: SEO 優化（使用 Stage 1 的關鍵詞）
        if PipelineStage.SEO in stages:
            # 從文案階段獲取關鍵詞
            keywords = result.content.keywords if result.content else []
            description = result.content.description if result.content else None

            seo_result = await self._stage_seo(
                product_data,
                language,
                existing_keywords=keywords,
                existing_description=description
            )
            result.seo = seo_result
            result.stages_executed.append("seo")

        # Stage 3: GEO 結構化數據（使用前面階段的描述和關鍵詞）
        if PipelineStage.GEO in stages:
            description = None
            if result.content:
                description = result.content.description
            elif result.seo:
                description = result.seo.meta_description

            geo_result = await self._stage_geo(
                product_data,
                existing_description=description,
                include_faq=include_faq
            )
            result.geo = geo_result
            result.stages_executed.append("geo")

        # 保存到數據庫
        if save_to_db:
            await self._save_results(result, product_id, language)

        # 計算執行時間
        end_time = datetime.now()
        result.generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
        result.model_used = self.ai_service.config.model if self.ai_service.config else "unknown"

        return result

    # =============================================
    # Stage 1: 文案生成
    # =============================================

    async def _stage_content(
        self,
        product_data: Dict[str, Any],
        language: str,
        tone: str,
    ) -> ContentResult:
        """Stage 1: 生成產品文案"""

        prompt = f"""{GOGOJAP_BRAND_CONTEXT}

## 任務
為以下產品生成電商文案，包括標題、賣點和詳細描述。

## 產品資訊
- 名稱: {product_data.get('name', '')}
- 品牌: {product_data.get('brand', 'GoGoJap')}
- 分類: {product_data.get('category', '')}
- 描述: {product_data.get('description', '')}
- 特點: {', '.join(product_data.get('features', []))}
- 價格: {product_data.get('price', '')}
- 產地: {product_data.get('origin', '')}

## 要求
1. 語言: {language}
2. 語氣: {tone}
3. 標題要吸引眼球，突出核心賣點
4. 賣點用 3-5 個精煉短句
5. 描述要詳細但不冗長，150-300 字
6. 提取 5-8 個 SEO 關鍵詞

## 返回格式 (JSON)
```json
{{
    "title": "產品標題",
    "selling_points": ["賣點1", "賣點2", "賣點3"],
    "description": "詳細描述...",
    "keywords": ["關鍵詞1", "關鍵詞2", ...]
}}
```

請只返回 JSON，不要其他內容。"""

        response = await self.ai_service.call_ai(prompt, max_tokens=1500)

        result = ContentResult(tone=tone)

        if response.success:
            try:
                content = self._parse_json_response(response.content)
                result.title = content.get("title", "")
                result.selling_points = content.get("selling_points", [])
                result.description = content.get("description", "")
                result.keywords = content.get("keywords", [])
            except Exception:
                # 如果解析失敗，嘗試提取文本
                result.title = product_data.get("name", "")
                result.description = response.content[:500]

        return result

    # =============================================
    # Stage 2: SEO 優化
    # =============================================

    async def _stage_seo(
        self,
        product_data: Dict[str, Any],
        language: str,
        existing_keywords: List[str] = None,
        existing_description: str = None,
    ) -> SEOResult:
        """Stage 2: 生成 SEO 優化內容"""

        keywords_hint = ""
        if existing_keywords:
            keywords_hint = f"\n已有關鍵詞參考: {', '.join(existing_keywords[:5])}"

        desc_hint = ""
        if existing_description:
            desc_hint = f"\n已有產品描述參考: {existing_description[:200]}..."

        prompt = f"""## 任務
為以下產品生成 SEO 優化的 Meta 標籤和關鍵詞。

## 產品資訊
- 名稱: {product_data.get('name', '')}
- 品牌: {product_data.get('brand', 'GoGoJap')}
- 分類: {product_data.get('category', '')}
{keywords_hint}
{desc_hint}

## SEO 要求
1. Meta Title: 最多 70 個字符，包含主關鍵詞
2. Meta Description: 最多 160 個字符，包含 CTA
3. 主關鍵詞: 1 個核心搜索詞
4. 次要關鍵詞: 3-5 個相關詞
5. 長尾關鍵詞: 2-3 個精準詞組
6. Open Graph 標題和描述

## 評分標準
- title_score: 標題關鍵詞覆蓋 (0-100)
- description_score: 描述完整性 (0-100)
- keyword_score: 關鍵詞相關性 (0-100)
- readability_score: 可讀性 (0-100)

## 返回格式 (JSON)
```json
{{
    "meta_title": "SEO 標題 (max 70 chars)",
    "meta_description": "SEO 描述 (max 160 chars)",
    "primary_keyword": "主關鍵詞",
    "secondary_keywords": ["次要1", "次要2"],
    "long_tail_keywords": ["長尾1", "長尾2"],
    "seo_score": 85,
    "score_breakdown": {{
        "title_score": 90,
        "description_score": 85,
        "keyword_score": 80,
        "readability_score": 85
    }},
    "og_title": "OG 標題",
    "og_description": "OG 描述"
}}
```

請只返回 JSON，不要其他內容。"""

        response = await self.ai_service.call_ai(prompt, max_tokens=1000)

        result = SEOResult()

        if response.success:
            try:
                content = self._parse_json_response(response.content)
                result.meta_title = content.get("meta_title", "")[:70]
                result.meta_description = content.get("meta_description", "")[:160]
                result.primary_keyword = content.get("primary_keyword", "")
                result.secondary_keywords = content.get("secondary_keywords", [])
                result.long_tail_keywords = content.get("long_tail_keywords", [])
                result.seo_score = content.get("seo_score", 0)
                result.score_breakdown = content.get("score_breakdown", {})
                result.og_title = content.get("og_title", "")
                result.og_description = content.get("og_description", "")
            except Exception:
                pass

        return result

    # =============================================
    # Stage 3: GEO 結構化數據
    # =============================================

    async def _stage_geo(
        self,
        product_data: Dict[str, Any],
        existing_description: str = None,
        include_faq: bool = False,
    ) -> GEOResult:
        """Stage 3: 生成 GEO 結構化數據"""

        result = GEOResult()

        # 生成 Product Schema
        result.product_schema = self._build_product_schema(product_data, existing_description)

        # 生成 FAQ Schema（如果需要）
        if include_faq:
            result.faq_schema = await self._generate_faq_schema(product_data)

        # 生成 AI 摘要（用於 AI 搜索引擎）
        ai_summary_result = await self._generate_ai_summary(product_data, existing_description)
        result.ai_summary = ai_summary_result.get("summary", "")
        result.ai_facts = ai_summary_result.get("facts", [])

        return result

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

    async def _generate_ai_summary(
        self,
        product_data: Dict[str, Any],
        description: str = None,
    ) -> Dict[str, Any]:
        """生成 AI 搜索引擎友好的摘要"""

        prompt = f"""為以下產品生成適合 AI 搜索引擎（如 Perplexity、ChatGPT）的結構化摘要。

產品: {product_data.get('name', '')}
品牌: {product_data.get('brand', 'GoGoJap')}
描述: {description or product_data.get('description', '')}

返回格式 (JSON):
```json
{{
    "summary": "一段 50-100 字的產品摘要，突出核心價值",
    "facts": ["事實1", "事實2", "事實3"]
}}
```

請只返回 JSON。"""

        response = await self.ai_service.call_ai(prompt, max_tokens=500)

        if response.success:
            try:
                return self._parse_json_response(response.content)
            except Exception:
                pass

        return {"summary": "", "facts": []}

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
        language: str,
    ) -> None:
        """保存結果到數據庫"""

        # 保存文案內容
        if result.content:
            ai_content = AIContent(
                id=uuid.uuid4(),
                product_id=product_id,
                title=result.content.title,
                description=result.content.description,
                selling_points=result.content.selling_points,
                keywords=result.content.keywords,
                status="draft",
                generated_at=utcnow(),
            )
            self.db.add(ai_content)
            result.content_id = ai_content.id

        # 保存 SEO 內容
        if result.seo:
            seo_content = SEOContent(
                id=uuid.uuid4(),
                product_id=product_id,
                meta_title=result.seo.meta_title,
                meta_description=result.seo.meta_description,
                primary_keyword=result.seo.primary_keyword,
                secondary_keywords=result.seo.secondary_keywords,
                long_tail_keywords=result.seo.long_tail_keywords,
                seo_score=result.seo.seo_score,
                score_breakdown=result.seo.score_breakdown,
                og_title=result.seo.og_title,
                og_description=result.seo.og_description,
                language=language,
                status="draft",
                created_at=utcnow(),
                updated_at=utcnow(),
            )
            self.db.add(seo_content)
            result.seo_content_id = seo_content.id

        # 保存結構化數據
        if result.geo and result.geo.product_schema:
            structured_data = StructuredData(
                id=uuid.uuid4(),
                product_id=product_id,
                schema_type="Product",
                json_ld=result.geo.product_schema,
                ai_summary=result.geo.ai_summary,
                ai_facts=result.geo.ai_facts,
                is_valid=True,
                created_at=utcnow(),
                updated_at=utcnow(),
            )
            self.db.add(structured_data)
            result.structured_data_id = structured_data.id

        await self.db.commit()


# =============================================
# 工廠函數
# =============================================

async def get_content_pipeline_service(db: AsyncSession) -> ContentPipelineService:
    """獲取內容流水線服務實例"""
    return await ContentPipelineService.create(db)
