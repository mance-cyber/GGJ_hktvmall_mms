# =============================================
# SEO 服務 - SEO 內容生成與分析
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
from app.models.seo import SEOContent, KeywordResearch, ContentAudit
from app.services.ai_service import AIAnalysisService, AIConfig, AISettingsService


@dataclass
class SEOGenerationResult:
    """SEO 生成結果"""
    success: bool
    content_id: Optional[uuid.UUID] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    primary_keyword: Optional[str] = None
    secondary_keywords: Optional[List[str]] = None
    long_tail_keywords: Optional[List[str]] = None
    seo_score: Optional[int] = None
    score_breakdown: Optional[Dict[str, int]] = None
    improvement_suggestions: Optional[List[str]] = None
    localized_seo: Optional[Dict[str, Any]] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    error: Optional[str] = None


class SEOService:
    """SEO 內容生成與分析服務"""

    def __init__(self, db: AsyncSession, ai_service: AIAnalysisService):
        self.db = db
        self.ai_service = ai_service

    @classmethod
    async def create(cls, db: AsyncSession) -> "SEOService":
        """工廠方法：創建 SEOService 實例"""
        config = await AISettingsService.get_config(db)
        ai_service = AIAnalysisService(config)
        return cls(db, ai_service)

    # =============================================
    # SEO 內容生成
    # =============================================

    async def generate_seo_content(
        self,
        product_id: Optional[uuid.UUID] = None,
        product_info: Optional[Dict[str, Any]] = None,
        target_keywords: Optional[List[str]] = None,
        target_languages: List[str] = None,
        include_og: bool = True,
    ) -> SEOGenerationResult:
        """
        生成 SEO 優化內容

        Args:
            product_id: 產品 ID（從數據庫獲取產品信息）
            product_info: 產品信息字典（手動提供）
            target_keywords: 目標關鍵詞列表（可選，AI 自動提取）
            target_languages: 目標語言列表
            include_og: 是否生成 Open Graph 標籤
        """
        if target_languages is None:
            target_languages = ["zh-HK"]

        # 獲取產品信息
        if product_id:
            product = await self.db.get(Product, product_id)
            if not product:
                return SEOGenerationResult(success=False, error="產品不存在")
            product_data = self._product_to_dict(product)
        elif product_info:
            product_data = product_info
            product = None
        else:
            return SEOGenerationResult(success=False, error="必須提供 product_id 或 product_info")

        # 如果沒有提供關鍵詞，先提取關鍵詞
        if not target_keywords:
            keywords_result = await self._extract_keywords(product_data)
            if keywords_result.get("error"):
                return SEOGenerationResult(success=False, error=keywords_result["error"])
            target_keywords = keywords_result.get("keywords", [])

        # 生成 SEO 內容
        seo_result = await self._generate_seo_with_ai(
            product_data,
            target_keywords,
            target_languages,
            include_og
        )

        if seo_result.get("error"):
            return SEOGenerationResult(success=False, error=seo_result["error"])

        # 計算 SEO 評分
        score_data = self._calculate_seo_score(seo_result)

        # 保存到數據庫
        seo_content = SEOContent(
            product_id=product_id,
            meta_title=seo_result["meta_title"],
            meta_description=seo_result["meta_description"],
            primary_keyword=target_keywords[0] if target_keywords else "",
            secondary_keywords=target_keywords[1:5] if len(target_keywords) > 1 else [],
            long_tail_keywords=seo_result.get("long_tail_keywords", []),
            seo_score=score_data["total_score"],
            score_breakdown=score_data,
            improvement_suggestions=seo_result.get("improvement_suggestions", []),
            language=target_languages[0] if target_languages else "zh-HK",
            localized_seo=seo_result.get("localized", {}),
            og_title=seo_result.get("og_title"),
            og_description=seo_result.get("og_description"),
            generation_metadata={
                "model": self.ai_service.config.insights_model,
                "generated_at": datetime.utcnow().isoformat(),
            },
            input_data=product_data,
        )

        self.db.add(seo_content)
        await self.db.flush()

        return SEOGenerationResult(
            success=True,
            content_id=seo_content.id,
            meta_title=seo_result["meta_title"],
            meta_description=seo_result["meta_description"],
            primary_keyword=target_keywords[0] if target_keywords else "",
            secondary_keywords=target_keywords[1:5] if len(target_keywords) > 1 else [],
            long_tail_keywords=seo_result.get("long_tail_keywords", []),
            seo_score=score_data["total_score"],
            score_breakdown=score_data,
            improvement_suggestions=seo_result.get("improvement_suggestions", []),
            localized_seo=seo_result.get("localized", {}),
            og_title=seo_result.get("og_title"),
            og_description=seo_result.get("og_description"),
        )

    async def _generate_seo_with_ai(
        self,
        product_data: Dict[str, Any],
        keywords: List[str],
        languages: List[str],
        include_og: bool,
    ) -> Dict[str, Any]:
        """使用 AI 生成 SEO 內容"""
        primary_keyword = keywords[0] if keywords else ""
        secondary_keywords = keywords[1:5] if len(keywords) > 1 else []

        prompt = f"""你是一位專業的 SEO 專家，專門為香港電商平台優化商品頁面。
請為以下產品生成高質量的 SEO 內容。

## 產品信息
- 名稱：{product_data.get('name', '')}
- 品牌：{product_data.get('brand', '未知')}
- 分類：{product_data.get('category', '未知')}
- 描述：{product_data.get('description', '無描述')}
- 特點：{', '.join(product_data.get('features', []))}
- 價格：{product_data.get('price', '未定')}

## 目標關鍵詞
- 主關鍵詞：{primary_keyword}
- 次要關鍵詞：{', '.join(secondary_keywords)}

## 目標語言
{', '.join(languages)}

## 生成要求

請返回以下 JSON 格式的 SEO 內容：

```json
{{
    "meta_title": "SEO 優化標題（50-60 字符，必須包含主關鍵詞）",
    "meta_description": "SEO 描述（120-155 字符，包含關鍵詞和行動呼籲）",
    "long_tail_keywords": ["長尾關鍵詞1", "長尾關鍵詞2", "長尾關鍵詞3"],
    "improvement_suggestions": ["改進建議1", "改進建議2"],
    {'"og_title": "Open Graph 標題",' + chr(10) + '    "og_description": "Open Graph 描述",' if include_og else ''}
    "localized": {{
        "zh-HK": {{
            "meta_title": "繁體中文標題",
            "meta_description": "繁體中文描述"
        }}
    }}
}}
```

## SEO 最佳實踐
1. 標題應該吸引點擊，包含主關鍵詞
2. 描述要有價值主張和行動呼籲（如「立即選購」「限時優惠」）
3. 適合香港市場的用語習慣
4. 長尾關鍵詞要具體且有搜索意圖

請只返回 JSON，不要其他內容。"""

        response = await self.ai_service.call_ai(prompt, max_tokens=2048)

        if not response.success:
            return {"error": response.error}

        try:
            # 清理 AI 返回的內容，提取 JSON
            content = response.content.strip()
            # 移除可能的 markdown 代碼塊標記
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\s*', '', content)
                content = re.sub(r'\s*```$', '', content)

            result = json.loads(content)
            return result

        except json.JSONDecodeError as e:
            return {"error": f"JSON 解析失敗: {str(e)}"}

    # =============================================
    # 關鍵詞提取
    # =============================================

    async def extract_keywords(
        self,
        product_id: Optional[uuid.UUID] = None,
        product_info: Optional[Dict[str, Any]] = None,
        max_keywords: int = 10,
        include_long_tail: bool = True,
    ) -> Dict[str, Any]:
        """
        從產品信息中提取 SEO 關鍵詞

        Returns:
            {
                "primary_keyword": "主關鍵詞",
                "secondary_keywords": ["次要1", "次要2"],
                "long_tail_keywords": ["長尾1", "長尾2"],
                "all_keywords": [{"keyword": "...", "intent": "..."}]
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

        return await self._extract_keywords(product_data, max_keywords, include_long_tail)

    async def _extract_keywords(
        self,
        product_data: Dict[str, Any],
        max_keywords: int = 10,
        include_long_tail: bool = True,
    ) -> Dict[str, Any]:
        """使用 AI 提取關鍵詞"""
        prompt = f"""你是一位 SEO 關鍵詞研究專家，專注於香港電商市場。
請為以下產品提取最相關的 SEO 關鍵詞。

## 產品信息
- 名稱：{product_data.get('name', '')}
- 品牌：{product_data.get('brand', '未知')}
- 分類：{product_data.get('category', '未知')}
- 描述：{product_data.get('description', '無描述')}

## 提取要求
- 提取最多 {max_keywords} 個關鍵詞
- 關鍵詞要符合香港用戶的搜索習慣
- 包含產品核心特徵和購買意圖詞
{"- 包含長尾關鍵詞（3-5 個詞組合）" if include_long_tail else ""}

## 返回格式
請返回以下 JSON 格式：

```json
{{
    "primary_keyword": "最重要的單一關鍵詞",
    "secondary_keywords": ["關鍵詞2", "關鍵詞3", "關鍵詞4"],
    "long_tail_keywords": ["長尾關鍵詞1", "長尾關鍵詞2"],
    "keywords": ["完整關鍵詞列表"],
    "keyword_analysis": [
        {{"keyword": "關鍵詞", "intent": "transactional/informational/navigational"}}
    ]
}}
```

請只返回 JSON，不要其他內容。"""

        response = await self.ai_service.call_ai(prompt, max_tokens=1024)

        if not response.success:
            return {"error": response.error}

        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\s*', '', content)
                content = re.sub(r'\s*```$', '', content)

            result = json.loads(content)
            return result

        except json.JSONDecodeError:
            # 如果 JSON 解析失敗，嘗試從產品名稱提取基本關鍵詞
            name = product_data.get('name', '')
            brand = product_data.get('brand', '')
            category = product_data.get('category', '')

            keywords = []
            if name:
                keywords.append(name)
            if brand:
                keywords.append(brand)
            if category:
                keywords.append(category)

            return {
                "primary_keyword": keywords[0] if keywords else "",
                "secondary_keywords": keywords[1:] if len(keywords) > 1 else [],
                "long_tail_keywords": [],
                "keywords": keywords,
            }

    # =============================================
    # SEO 評分
    # =============================================

    def _calculate_seo_score(self, seo_data: Dict[str, Any]) -> Dict[str, int]:
        """計算 SEO 評分"""
        scores = {
            "title_score": self._score_title(seo_data.get("meta_title", "")),
            "description_score": self._score_description(seo_data.get("meta_description", "")),
            "keyword_score": self._score_keyword_usage(seo_data),
            "readability_score": self._score_readability(seo_data),
        }
        scores["total_score"] = sum(scores.values()) // len(scores)
        return scores

    def _score_title(self, title: str) -> int:
        """評分標題 SEO 質量"""
        if not title:
            return 0

        score = 50  # 基礎分

        # 長度檢查（50-60 字符最佳）
        length = len(title)
        if 50 <= length <= 60:
            score += 25
        elif 40 <= length < 50 or 60 < length <= 70:
            score += 15
        elif length < 40:
            score += 5

        # 是否包含分隔符（|, -, 等）- 結構化標題
        if any(sep in title for sep in ['|', '-', '–', '·']):
            score += 15

        # 是否以品牌結尾（常見模式）
        if '|' in title or '-' in title:
            score += 10

        return min(score, 100)

    def _score_description(self, description: str) -> int:
        """評分描述 SEO 質量"""
        if not description:
            return 0

        score = 50  # 基礎分

        # 長度檢查（120-155 字符最佳）
        length = len(description)
        if 120 <= length <= 155:
            score += 25
        elif 100 <= length < 120 or 155 < length <= 170:
            score += 15
        elif length < 100:
            score += 5

        # 是否包含行動呼籲詞
        cta_words = ['立即', '選購', '了解更多', '限時', '優惠', '免費', '查看', '訂購']
        if any(cta in description for cta in cta_words):
            score += 15

        # 是否有數字（增加可信度）
        if re.search(r'\d+', description):
            score += 10

        return min(score, 100)

    def _score_keyword_usage(self, seo_data: Dict[str, Any]) -> int:
        """評分關鍵詞使用"""
        score = 50  # 基礎分

        title = seo_data.get("meta_title", "")
        description = seo_data.get("meta_description", "")
        long_tail = seo_data.get("long_tail_keywords", [])

        # 有長尾關鍵詞
        if long_tail:
            score += min(len(long_tail) * 5, 20)

        # 標題和描述都存在
        if title and description:
            score += 15

        # 有本地化版本
        if seo_data.get("localized"):
            score += 15

        return min(score, 100)

    def _score_readability(self, seo_data: Dict[str, Any]) -> int:
        """評分可讀性"""
        score = 60  # 基礎分

        title = seo_data.get("meta_title", "")
        description = seo_data.get("meta_description", "")

        # 標題不要太長
        if title and len(title) <= 60:
            score += 20

        # 描述不要太長
        if description and len(description) <= 160:
            score += 20

        return min(score, 100)

    async def get_seo_score(self, product_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """獲取產品的 SEO 評分"""
        result = await self.db.execute(
            select(SEOContent)
            .where(SEOContent.product_id == product_id)
            .order_by(SEOContent.created_at.desc())
            .limit(1)
        )
        seo_content = result.scalar_one_or_none()

        if not seo_content:
            return None

        return {
            "product_id": product_id,
            "seo_score": seo_content.seo_score,
            "score_breakdown": seo_content.score_breakdown,
            "improvement_suggestions": seo_content.improvement_suggestions or [],
            "analyzed_at": seo_content.created_at,
        }

    # =============================================
    # 內容審計
    # =============================================

    async def audit_content(
        self,
        product_id: Optional[uuid.UUID] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        audit_type: str = "full",
    ) -> Dict[str, Any]:
        """審計內容的 SEO 質量"""
        issues = []
        recommendations = []
        scores = {}

        # 標題審計
        if title or audit_type in ["full", "title_only"]:
            title_score = self._score_title(title or "")
            scores["title"] = title_score

            if not title:
                issues.append({
                    "type": "missing_title",
                    "severity": "critical",
                    "message": "缺少 SEO 標題",
                    "field": "title"
                })
            elif len(title) < 30:
                issues.append({
                    "type": "short_title",
                    "severity": "medium",
                    "message": f"標題太短（{len(title)} 字符），建議 50-60 字符",
                    "field": "title"
                })
            elif len(title) > 70:
                issues.append({
                    "type": "long_title",
                    "severity": "medium",
                    "message": f"標題太長（{len(title)} 字符），可能被截斷",
                    "field": "title"
                })

        # 描述審計
        if description or audit_type in ["full", "description_only"]:
            desc_score = self._score_description(description or "")
            scores["description"] = desc_score

            if not description:
                issues.append({
                    "type": "missing_description",
                    "severity": "critical",
                    "message": "缺少 SEO 描述",
                    "field": "description"
                })
            elif len(description) < 70:
                issues.append({
                    "type": "short_description",
                    "severity": "medium",
                    "message": f"描述太短（{len(description)} 字符），建議 120-155 字符",
                    "field": "description"
                })
            elif len(description) > 160:
                issues.append({
                    "type": "long_description",
                    "severity": "low",
                    "message": f"描述太長（{len(description)} 字符），可能被截斷",
                    "field": "description"
                })

        # 關鍵詞審計
        if keywords or audit_type in ["full", "keywords"]:
            if not keywords:
                issues.append({
                    "type": "missing_keywords",
                    "severity": "medium",
                    "message": "沒有設定目標關鍵詞",
                    "field": "keywords"
                })
                scores["keywords"] = 0
            else:
                scores["keywords"] = min(len(keywords) * 10, 100)

        # 計算總分
        overall_score = sum(scores.values()) // len(scores) if scores else 0

        # 生成建議
        if overall_score < 50:
            recommendations.append({
                "priority": 1,
                "action": "重新生成 SEO 內容",
                "expected_impact": "預計可提升 30-50% 的搜索可見度"
            })
        if "title" in scores and scores["title"] < 60:
            recommendations.append({
                "priority": 2,
                "action": "優化標題，加入關鍵詞和品牌名",
                "expected_impact": "預計可提升點擊率 10-20%"
            })
        if "description" in scores and scores["description"] < 60:
            recommendations.append({
                "priority": 3,
                "action": "優化描述，加入行動呼籲",
                "expected_impact": "預計可提升轉化率 5-15%"
            })

        # 保存審計記錄
        audit = ContentAudit(
            product_id=product_id,
            audit_type=audit_type,
            overall_score=overall_score,
            scores=scores,
            issues=issues,
            recommendations=recommendations,
        )
        self.db.add(audit)
        await self.db.flush()

        return {
            "id": audit.id,
            "product_id": product_id,
            "audit_type": audit_type,
            "overall_score": overall_score,
            "scores": scores,
            "issues": issues,
            "recommendations": recommendations,
            "audited_at": audit.audited_at,
        }

    # =============================================
    # 關鍵詞建議
    # =============================================

    async def get_keyword_suggestions(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """獲取關鍵詞建議"""
        # 從數據庫查詢相關關鍵詞
        stmt = select(KeywordResearch).where(
            KeywordResearch.keyword.ilike(f"%{query}%")
        )
        if category:
            stmt = stmt.where(KeywordResearch.category == category)
        stmt = stmt.order_by(KeywordResearch.search_volume.desc().nulls_last()).limit(limit)

        result = await self.db.execute(stmt)
        keywords = result.scalars().all()

        # 如果數據庫中沒有足夠的結果，使用 AI 生成
        if len(keywords) < 5:
            ai_suggestions = await self._generate_keyword_suggestions(query, category)
            return {
                "query": query,
                "suggestions": ai_suggestions,
                "source": "ai_generated",
            }

        return {
            "query": query,
            "suggestions": [
                {
                    "keyword": k.keyword,
                    "search_volume": k.search_volume,
                    "difficulty": k.difficulty,
                    "intent": k.intent,
                }
                for k in keywords
            ],
            "source": "database",
        }

    async def _generate_keyword_suggestions(
        self,
        query: str,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """使用 AI 生成關鍵詞建議"""
        prompt = f"""你是一位 SEO 關鍵詞研究專家，專注於香港電商市場。
請為以下查詢提供關鍵詞建議。

## 查詢
{query}
{"## 分類\n" + category if category else ""}

## 要求
請返回 10 個相關的 SEO 關鍵詞，包括：
- 核心關鍵詞
- 長尾關鍵詞
- 購買意圖關鍵詞

## 返回格式
```json
[
    {{"keyword": "關鍵詞", "intent": "transactional", "relevance": "high"}},
    ...
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
            "features": product.attributes.get("features", []) if product.attributes else [],
            "origin": product.attributes.get("origin") if product.attributes else None,
        }

    async def get_seo_content(self, content_id: uuid.UUID) -> Optional[SEOContent]:
        """獲取 SEO 內容"""
        return await self.db.get(SEOContent, content_id)

    async def list_seo_contents(
        self,
        product_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """列出 SEO 內容"""
        stmt = select(SEOContent)
        if product_id:
            stmt = stmt.where(SEOContent.product_id == product_id)
        if status:
            stmt = stmt.where(SEOContent.status == status)
        stmt = stmt.order_by(SEOContent.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        contents = result.scalars().all()

        # 計算總數
        count_stmt = select(SEOContent)
        if product_id:
            count_stmt = count_stmt.where(SEOContent.product_id == product_id)
        if status:
            count_stmt = count_stmt.where(SEOContent.status == status)
        count_result = await self.db.execute(count_stmt)
        total = len(count_result.scalars().all())

        return {
            "data": contents,
            "total": total,
        }
