# =============================================
# GEO 服務 - 結構化數據生成 (Schema.org JSON-LD)
# =============================================

import uuid
import json
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product import Product
from app.models.seo import StructuredData, BrandKnowledge
from app.services.ai_service import AIAnalysisService, AIConfig, AISettingsService


@dataclass
class SchemaGenerationResult:
    """Schema 生成結果"""
    success: bool
    schema_id: Optional[uuid.UUID] = None
    schema_type: Optional[str] = None
    json_ld: Optional[Dict[str, Any]] = None
    ai_summary: Optional[str] = None
    ai_facts: Optional[List[str]] = None
    is_valid: bool = True
    validation_errors: Optional[List[str]] = None
    error: Optional[str] = None


class GEOService:
    """GEO (Generative Engine Optimization) 服務 - 結構化數據生成"""

    # Schema.org 模板
    PRODUCT_SCHEMA_TEMPLATE = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "",
        "description": "",
        "brand": {"@type": "Brand", "name": ""},
        "offers": {
            "@type": "Offer",
            "price": "",
            "priceCurrency": "HKD",
            "availability": "https://schema.org/InStock",
            "url": "",
        },
    }

    FAQ_SCHEMA_TEMPLATE = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [],
    }

    BREADCRUMB_SCHEMA_TEMPLATE = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [],
    }

    def __init__(self, db: AsyncSession, ai_service: AIAnalysisService):
        self.db = db
        self.ai_service = ai_service

    @classmethod
    async def create(cls, db: AsyncSession) -> "GEOService":
        """工廠方法：創建 GEOService 實例"""
        config = await AISettingsService.get_config(db)
        ai_service = AIAnalysisService(config)
        return cls(db, ai_service)

    # =============================================
    # Product Schema 生成
    # =============================================

    async def generate_product_schema(
        self,
        product_id: Optional[uuid.UUID] = None,
        product_info: Optional[Dict[str, Any]] = None,
        include_reviews: bool = False,
        include_offers: bool = True,
    ) -> SchemaGenerationResult:
        """
        生成 Product Schema.org JSON-LD

        Args:
            product_id: 產品 ID
            product_info: 產品信息字典
            include_reviews: 是否包含評價信息
            include_offers: 是否包含價格/優惠信息
        """
        # 獲取產品信息
        if product_id:
            product = await self.db.get(Product, product_id)
            if not product:
                return SchemaGenerationResult(success=False, error="產品不存在")
            product_data = self._product_to_dict(product)
        elif product_info:
            product_data = product_info
            product = None
        else:
            return SchemaGenerationResult(success=False, error="必須提供 product_id 或 product_info")

        # 構建 JSON-LD
        json_ld = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "brand": {
                "@type": "Brand",
                "name": product_data.get("brand", "GogoJap")
            },
            "sku": product_data.get("sku", ""),
        }

        # 添加圖片
        if product_data.get("images"):
            images = product_data["images"]
            if isinstance(images, list) and len(images) > 0:
                json_ld["image"] = images

        # 添加分類
        if product_data.get("category"):
            json_ld["category"] = product_data["category"]

        # 添加價格信息
        if include_offers and product_data.get("price"):
            price = product_data["price"]
            json_ld["offers"] = {
                "@type": "Offer",
                "price": str(price),
                "priceCurrency": "HKD",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": (datetime.utcnow().replace(year=datetime.utcnow().year + 1)).strftime("%Y-%m-%d"),
            }

            # 如果有原價，添加折扣信息
            if product_data.get("original_price"):
                json_ld["offers"]["@type"] = "AggregateOffer"

        # 生成 AI 友好摘要
        ai_summary_result = await self._generate_ai_summary(product_data)

        # 驗證 Schema
        validation_errors = self._validate_product_schema(json_ld)

        # 保存到數據庫
        structured_data = StructuredData(
            product_id=product_id,
            schema_type="Product",
            json_ld=json_ld,
            ai_summary=ai_summary_result.get("summary"),
            ai_facts=ai_summary_result.get("facts", []),
            ai_entities=ai_summary_result.get("entities", {}),
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            last_validated_at=datetime.utcnow(),
        )

        self.db.add(structured_data)
        await self.db.flush()

        return SchemaGenerationResult(
            success=True,
            schema_id=structured_data.id,
            schema_type="Product",
            json_ld=json_ld,
            ai_summary=ai_summary_result.get("summary"),
            ai_facts=ai_summary_result.get("facts", []),
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
        )

    # =============================================
    # FAQ Schema 生成
    # =============================================

    async def generate_faq_schema(
        self,
        product_id: Optional[uuid.UUID] = None,
        faqs: Optional[List[Dict[str, str]]] = None,
        max_faqs: int = 5,
    ) -> SchemaGenerationResult:
        """
        生成 FAQ Schema.org JSON-LD

        Args:
            product_id: 產品 ID（用於 AI 生成 FAQ）
            faqs: FAQ 列表 [{"question": "...", "answer": "..."}]
            max_faqs: 最大 FAQ 數量
        """
        # 如果沒有提供 FAQ，使用 AI 生成
        if not faqs and product_id:
            product = await self.db.get(Product, product_id)
            if product:
                faqs = await self._generate_faqs_with_ai(self._product_to_dict(product), max_faqs)
            else:
                return SchemaGenerationResult(success=False, error="產品不存在")
        elif not faqs:
            return SchemaGenerationResult(success=False, error="必須提供 faqs 或 product_id")

        # 構建 JSON-LD
        json_ld = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": faq["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq["answer"]
                    }
                }
                for faq in faqs[:max_faqs]
            ]
        }

        # 驗證 Schema
        validation_errors = self._validate_faq_schema(json_ld)

        # 保存到數據庫
        structured_data = StructuredData(
            product_id=product_id,
            schema_type="FAQPage",
            json_ld=json_ld,
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
            last_validated_at=datetime.utcnow(),
        )

        self.db.add(structured_data)
        await self.db.flush()

        return SchemaGenerationResult(
            success=True,
            schema_id=structured_data.id,
            schema_type="FAQPage",
            json_ld=json_ld,
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors,
        )

    async def _generate_faqs_with_ai(
        self,
        product_data: Dict[str, Any],
        max_faqs: int = 5,
    ) -> List[Dict[str, str]]:
        """使用 AI 生成 FAQ"""
        prompt = f"""你是一位專業的電商客服專家，專門為香港市場編寫 FAQ。
請為以下產品生成 {max_faqs} 個常見問題及答案。

## 產品信息
- 名稱：{product_data.get('name', '')}
- 品牌：{product_data.get('brand', '未知')}
- 分類：{product_data.get('category', '未知')}
- 描述：{product_data.get('description', '無描述')}
- 價格：{product_data.get('price', '未定')}

## 生成要求
1. 問題要符合香港消費者的常見疑問
2. 答案要簡潔、專業、有幫助
3. 包含購買、配送、品質、儲存等方面
4. 適合 AI 搜索引擎引用

## 返回格式
```json
[
    {{"question": "問題1", "answer": "答案1"}},
    {{"question": "問題2", "answer": "答案2"}}
]
```

請只返回 JSON 數組，不要其他內容。"""

        response = await self.ai_service.call_ai(prompt, max_tokens=1024)

        if not response.success:
            return []

        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
            return json.loads(content)
        except json.JSONDecodeError:
            return []

    # =============================================
    # Breadcrumb Schema 生成
    # =============================================

    async def generate_breadcrumb_schema(
        self,
        product_id: Optional[uuid.UUID] = None,
        breadcrumb_path: Optional[List[Dict[str, str]]] = None,
    ) -> SchemaGenerationResult:
        """
        生成 BreadcrumbList Schema

        Args:
            product_id: 產品 ID
            breadcrumb_path: 麵包屑路徑 [{"name": "...", "url": "..."}]
        """
        # 如果沒有提供路徑，從產品分類生成
        if not breadcrumb_path and product_id:
            product = await self.db.get(Product, product_id)
            if product:
                breadcrumb_path = self._generate_breadcrumb_from_product(product)
            else:
                return SchemaGenerationResult(success=False, error="產品不存在")
        elif not breadcrumb_path:
            return SchemaGenerationResult(success=False, error="必須提供 breadcrumb_path 或 product_id")

        # 構建 JSON-LD
        json_ld = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": item["name"],
                    "item": item.get("url", "")
                }
                for i, item in enumerate(breadcrumb_path)
            ]
        }

        # 保存到數據庫
        structured_data = StructuredData(
            product_id=product_id,
            schema_type="BreadcrumbList",
            json_ld=json_ld,
            is_valid=True,
            validation_errors=[],
            last_validated_at=datetime.utcnow(),
        )

        self.db.add(structured_data)
        await self.db.flush()

        return SchemaGenerationResult(
            success=True,
            schema_id=structured_data.id,
            schema_type="BreadcrumbList",
            json_ld=json_ld,
            is_valid=True,
            validation_errors=[],
        )

    def _generate_breadcrumb_from_product(self, product: Product) -> List[Dict[str, str]]:
        """從產品生成麵包屑路徑"""
        breadcrumbs = [
            {"name": "首頁", "url": "https://www.gogojap.com/"}
        ]

        if product.category_main:
            breadcrumbs.append({
                "name": product.category_main,
                "url": f"https://www.gogojap.com/category/{product.category_main}"
            })

        if product.category_sub:
            breadcrumbs.append({
                "name": product.category_sub,
                "url": f"https://www.gogojap.com/category/{product.category_main}/{product.category_sub}"
            })

        breadcrumbs.append({
            "name": product.name,
            "url": f"https://www.gogojap.com/product/{product.sku}"
        })

        return breadcrumbs

    # =============================================
    # AI 摘要生成
    # =============================================

    async def generate_ai_summary(
        self,
        product_id: Optional[uuid.UUID] = None,
        product_info: Optional[Dict[str, Any]] = None,
        max_facts: int = 5,
    ) -> Dict[str, Any]:
        """
        生成 AI 搜索引擎友好摘要

        Returns:
            {
                "summary": "簡短摘要",
                "facts": ["事實1", "事實2"],
                "entities": {"brand": "...", "origin": "..."}
            }
        """
        # 獲取產品信息
        if product_id:
            product = await self.db.get(Product, product_id)
            if not product:
                return {"error": "產品不存在"}
            product_data = self._product_to_dict(product)
        elif product_info:
            product_data = product_info
        else:
            return {"error": "必須提供 product_id 或 product_info"}

        return await self._generate_ai_summary(product_data, max_facts)

    async def _generate_ai_summary(
        self,
        product_data: Dict[str, Any],
        max_facts: int = 5,
    ) -> Dict[str, Any]:
        """使用 AI 生成結構化摘要"""
        prompt = f"""你是一位專業的內容策略師，專門為 AI 搜索引擎（如 ChatGPT、Perplexity、Google AI Overview）優化內容。
請為以下產品生成結構化的 AI 友好信息。

## 產品信息
- 名稱：{product_data.get('name', '')}
- 品牌：{product_data.get('brand', '未知')}
- 分類：{product_data.get('category', '未知')}
- 描述：{product_data.get('description', '無描述')}
- 價格：{product_data.get('price', '未定')}
- 產地：{product_data.get('origin', '未知')}

## 生成要求
1. 摘要要直接回答「這是什麼產品」（100字內）
2. 事實要具體、可驗證、對購買決策有幫助
3. 實體要準確提取品牌、產地、規格等結構化信息
4. 語言簡潔直接，適合 AI 引用

## 返回格式
```json
{{
    "summary": "一段簡潔的產品摘要",
    "facts": [
        "事實1：具體數據或特點",
        "事實2：...",
        "事實3：..."
    ],
    "entities": {{
        "brand": "品牌名",
        "origin": "產地",
        "category": "分類",
        "price_range": "價格範圍",
        "key_features": ["特點1", "特點2"]
    }}
}}
```

請只返回 JSON，不要其他內容。"""

        response = await self.ai_service.call_ai(prompt, max_tokens=1024)

        if not response.success:
            # 返回基本信息作為備選
            return {
                "summary": product_data.get("description", "")[:100] if product_data.get("description") else "",
                "facts": [],
                "entities": {
                    "brand": product_data.get("brand", ""),
                    "category": product_data.get("category", ""),
                }
            }

        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "summary": product_data.get("description", "")[:100] if product_data.get("description") else "",
                "facts": [],
                "entities": {}
            }

    # =============================================
    # Schema 驗證
    # =============================================

    def validate_schema(self, json_ld: Dict[str, Any]) -> Dict[str, Any]:
        """
        驗證 Schema.org JSON-LD

        Returns:
            {
                "is_valid": bool,
                "errors": [...],
                "warnings": [...],
                "suggestions": [...]
            }
        """
        errors = []
        warnings = []
        suggestions = []

        # 基本結構驗證
        if "@context" not in json_ld:
            errors.append("缺少 @context 屬性")
        elif json_ld["@context"] != "https://schema.org":
            warnings.append("@context 應該是 'https://schema.org'")

        if "@type" not in json_ld:
            errors.append("缺少 @type 屬性")

        schema_type = json_ld.get("@type", "")

        # 根據類型進行特定驗證
        if schema_type == "Product":
            errors.extend(self._validate_product_schema(json_ld))
        elif schema_type == "FAQPage":
            errors.extend(self._validate_faq_schema(json_ld))

        # 通用建議
        if schema_type == "Product" and "aggregateRating" not in json_ld:
            suggestions.append("建議添加 aggregateRating 以顯示產品評分")

        if schema_type == "Product" and "review" not in json_ld:
            suggestions.append("建議添加 review 以顯示用戶評價")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions,
        }

    def _validate_product_schema(self, json_ld: Dict[str, Any]) -> List[str]:
        """驗證 Product Schema"""
        errors = []

        required_fields = ["name"]
        for field in required_fields:
            if field not in json_ld or not json_ld[field]:
                errors.append(f"缺少必要欄位: {field}")

        # 驗證 offers
        if "offers" in json_ld:
            offers = json_ld["offers"]
            if "price" not in offers:
                errors.append("offers 中缺少 price")
            if "priceCurrency" not in offers:
                errors.append("offers 中缺少 priceCurrency")

        return errors

    def _validate_faq_schema(self, json_ld: Dict[str, Any]) -> List[str]:
        """驗證 FAQ Schema"""
        errors = []

        if "mainEntity" not in json_ld:
            errors.append("缺少 mainEntity 屬性")
        elif not isinstance(json_ld["mainEntity"], list):
            errors.append("mainEntity 應該是數組")
        elif len(json_ld["mainEntity"]) == 0:
            errors.append("mainEntity 不能為空")

        return errors

    # =============================================
    # 品牌知識管理
    # =============================================

    async def create_brand_knowledge(
        self,
        knowledge_type: str,
        title: str,
        content: str,
        summary: Optional[str] = None,
        related_products: Optional[List[uuid.UUID]] = None,
        related_categories: Optional[List[str]] = None,
        source_type: str = "internal",
        source_reference: Optional[str] = None,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> BrandKnowledge:
        """創建品牌知識條目"""
        knowledge = BrandKnowledge(
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            summary=summary,
            related_products=[str(p) for p in (related_products or [])],
            related_categories=related_categories or [],
            source_type=source_type,
            source_reference=source_reference,
            author=author,
            tags=tags or [],
        )

        self.db.add(knowledge)
        await self.db.flush()
        return knowledge

    async def search_brand_knowledge(
        self,
        query: str,
        knowledge_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[BrandKnowledge]:
        """搜索品牌知識"""
        stmt = select(BrandKnowledge).where(
            BrandKnowledge.is_active == True
        )

        if knowledge_type:
            stmt = stmt.where(BrandKnowledge.knowledge_type == knowledge_type)

        # 簡單的文本搜索（標題或內容包含關鍵詞）
        stmt = stmt.where(
            (BrandKnowledge.title.ilike(f"%{query}%")) |
            (BrandKnowledge.content.ilike(f"%{query}%"))
        )

        stmt = stmt.order_by(BrandKnowledge.is_featured.desc(), BrandKnowledge.created_at.desc()).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_product_knowledge(
        self,
        product_id: uuid.UUID,
    ) -> List[BrandKnowledge]:
        """獲取產品相關的品牌知識"""
        # 轉換為字符串以匹配 JSONB 中的存儲格式
        product_id_str = str(product_id)

        stmt = select(BrandKnowledge).where(
            BrandKnowledge.is_active == True
        )

        result = await self.db.execute(stmt)
        all_knowledge = result.scalars().all()

        # 過濾包含該產品的知識
        return [
            k for k in all_knowledge
            if k.related_products and product_id_str in k.related_products
        ]

    async def generate_expert_content(
        self,
        topic: str,
        product_id: Optional[uuid.UUID] = None,
        knowledge_type: str = "expert_claim",
        tone: str = "professional",
    ) -> BrandKnowledge:
        """AI 生成專家級內容"""
        product_context = ""
        if product_id:
            product = await self.db.get(Product, product_id)
            if product:
                product_context = f"""
## 相關產品
- 名稱：{product.name}
- 品牌：{product.brand}
- 分類：{product.category}
"""

        prompt = f"""你是一位專業的食品/電商領域專家，請針對以下主題撰寫一篇專家級內容。

## 主題
{topic}

{product_context}

## 要求
1. 內容要專業、可信、有價值
2. 語氣：{tone}
3. 包含具體數據或事實支持
4. 適合用於品牌知識庫和 AI 搜索引擎引用
5. 長度：200-400 字

## 返回格式
```json
{{
    "title": "文章標題",
    "content": "正文內容",
    "summary": "一句話摘要（50字內）",
    "tags": ["標籤1", "標籤2", "標籤3"]
}}
```

請只返回 JSON，不要其他內容。"""

        response = await self.ai_service.call_ai(prompt, max_tokens=1024)

        if not response.success:
            raise ValueError(f"AI 生成失敗: {response.error}")

        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
            result = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("AI 返回格式錯誤")

        # 創建知識條目
        knowledge = await self.create_brand_knowledge(
            knowledge_type=knowledge_type,
            title=result["title"],
            content=result["content"],
            summary=result.get("summary"),
            related_products=[product_id] if product_id else [],
            source_type="ai_generated",
            tags=result.get("tags", []),
        )

        return knowledge

    # =============================================
    # 輔助方法
    # =============================================

    def _product_to_dict(self, product: Product) -> Dict[str, Any]:
        """將 Product 模型轉換為字典"""
        return {
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "description": product.description,
            "price": str(product.price) if product.price else None,
            "sku": product.sku,
            "images": product.images or [],
            "features": product.attributes.get("features", []) if product.attributes else [],
            "origin": product.attributes.get("origin") if product.attributes else None,
            "category_main": product.category_main,
            "category_sub": product.category_sub,
        }

    async def get_structured_data(self, data_id: uuid.UUID) -> Optional[StructuredData]:
        """獲取結構化數據"""
        return await self.db.get(StructuredData, data_id)

    async def list_structured_data(
        self,
        product_id: Optional[uuid.UUID] = None,
        schema_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """列出結構化數據"""
        stmt = select(StructuredData)
        if product_id:
            stmt = stmt.where(StructuredData.product_id == product_id)
        if schema_type:
            stmt = stmt.where(StructuredData.schema_type == schema_type)
        stmt = stmt.order_by(StructuredData.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        data_list = result.scalars().all()

        return {
            "data": data_list,
            "total": len(data_list),
        }
