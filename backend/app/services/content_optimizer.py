# =============================================
# AI 文案對話式優化服務
# =============================================
# 整合簡化版 Prompt，支持互動式文案優化

import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from app.config import get_settings
from app.services.ai_service import AIAnalysisService


@dataclass
class OptimizationResult:
    """優化結果"""
    content: Dict[str, Any]  # 優化後的內容 (title, selling_points, description 等)
    suggestions: List[str]   # 後續優化建議
    tokens_used: int = 0
    model: str = ""
    success: bool = True
    error: Optional[str] = None


# =============================================
# GogoJap 品牌背景（內建於 Prompt）
# =============================================

GOGOJAP_BRAND_CONTEXT = """
## GogoJap 品牌背景

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
# 快捷優化建議配置
# =============================================

QUICK_OPTIMIZATION_SUGGESTIONS = {
    "tone_casual": {
        "label": "語氣輕鬆啲",
        "instruction": "請將文案語氣改得更輕鬆親切，加入更多香港地道口語",
    },
    "enhance_selling_points": {
        "label": "加強賣點",
        "instruction": "請加強產品的核心賣點描述，突出米芝蓮/五星酒店背書",
    },
    "shorten": {
        "label": "縮短長度",
        "instruction": "請精簡文案，保留重點，去除冗餘內容",
    },
    "more_local": {
        "label": "更貼地",
        "instruction": "請用更地道的香港口語重寫，讓文案更貼近本地消費者",
    },
    "add_urgency": {
        "label": "加入 urgency",
        "instruction": "請加入限時優惠的緊迫感，如「限時88折」「上週一分鐘售罄」等",
    },
}


class ContentOptimizer:
    """文案對話式優化器"""

    def __init__(self, ai_service: AIAnalysisService):
        self.ai_service = ai_service
        self.settings = get_settings()

    def optimize(
        self,
        current_content: Dict[str, Any],
        instruction: str,
        context: Optional[List[Dict[str, str]]] = None,
        target_languages: Optional[List[str]] = None,
        product_info: Optional[Dict[str, Any]] = None,
    ) -> OptimizationResult:
        """
        優化現有文案

        Args:
            current_content: 當前文案內容 (title, selling_points, description 等)
            instruction: 用戶的優化指令
            context: 對話歷史 [{"role": "user/assistant", "content": "..."}]
            target_languages: 目標語言列表 ["TC", "SC", "EN"]
            product_info: 產品資訊（用於上下文）

        Returns:
            OptimizationResult
        """
        if target_languages is None:
            target_languages = ["TC"]

        # 構建優化 Prompt
        prompt = self._build_optimization_prompt(
            current_content=current_content,
            instruction=instruction,
            context=context,
            target_languages=target_languages,
            product_info=product_info,
        )

        # 調用 AI 服務
        response = self.ai_service._call_api(
            prompt=prompt,
            model=self.ai_service.config.insights_model,
            max_tokens=2048,
        )

        if not response.success:
            return OptimizationResult(
                content=current_content,
                suggestions=[],
                success=False,
                error=response.error,
            )

        # 解析響應
        return self._parse_optimization_response(
            response_text=response.content,
            current_content=current_content,
            tokens_used=response.tokens_used,
            model=response.model,
        )

    def _build_optimization_prompt(
        self,
        current_content: Dict[str, Any],
        instruction: str,
        context: Optional[List[Dict[str, str]]],
        target_languages: List[str],
        product_info: Optional[Dict[str, Any]],
    ) -> str:
        """構建優化 Prompt"""

        # 語言說明
        lang_map = {"TC": "繁體中文", "SC": "簡體中文", "EN": "英文"}
        target_lang_str = "、".join([lang_map.get(l, l) for l in target_languages])

        # 當前內容格式化
        current_content_str = self._format_content_for_prompt(current_content)

        # 對話歷史
        context_str = ""
        if context:
            context_str = "\n## 對話歷史\n"
            for msg in context[-5:]:  # 只保留最近 5 條
                role = "用戶" if msg.get("role") == "user" else "AI"
                context_str += f"**{role}**: {msg.get('content', '')}\n"

        # 產品資訊
        product_str = ""
        if product_info:
            product_str = f"""
## 產品資訊
- 名稱：{product_info.get('name', '未知')}
- 品牌：{product_info.get('brand', '')}
- 產地：{product_info.get('origin', '')}
- 重量：{product_info.get('weight', '')}
- 等級：{product_info.get('grade', '')}
"""

        prompt = f"""你是 GogoJap 電商文案優化專家，具備以下三個專業角色：

1. **GogoJap 電商文案總監** — 撰寫讓香港人心動下單的產品描述
2. **銷售心理專家** — 以「不買不行」的心理策略設計文案
3. **香港消費者代言人** — 代入貼地客人視角審視文案是否真正打動人心

{GOGOJAP_BRAND_CONTEXT}
{product_str}
{context_str}

## 當前文案內容
{current_content_str}

## 優化指令
{instruction}

---

## 標題優化策略（如需優化標題，必須遵循）

**公式**: [痛點/利益/驚嘆 Hook] + 產品名 + [核心賣點]

### 好標題範例：
- ❌ 差：「日本和牛 A5 等級 200g」（純資訊，零吸引力）
- ✅ 好：「米芝蓮主廚私藏｜日本 A5 和牛｜入口即溶油花爆棚」
- ✅ 好：「五星酒店同款食材屋企食｜澳洲 M9 和牛｜餐廳價 1/5」
- ✅ 好：「食一次就返唔到轉頭｜北海道帶子刺身級｜鮮甜到震驚」

### 標題必須包含：
1. **信任背書**：米芝蓮/五星酒店/專業認證
2. **感官誘惑**：入口即溶/油花綻放/鮮甜爆棚
3. **價值主張**：餐廳價1/5/性價比極高/CP值爆燈

---

## 文案核心邏輯

**痛點 → 背書 → 感官 → 性價比**

1. **痛點開頭**：直擊消費者真實煩惱
2. **專業背書**：五星酒店/米芝蓮指定供應商
3. **感官描寫**：入口即溶、油花綻放、鮮甜到震驚
4. **性價比收殺**：餐廳價 1/5，限時優惠

---

## 輸出要求
1. 目標語言：{target_lang_str}
2. 保持 GogoJap 品牌調性
3. 語氣：主要專業優雅，適量輕口語增加親切感
4. 可用口語詞彙：超正、完全無壓力、好食到喊、上癮、穩陣、爽到飛起、絕對值得、性價比極高
5. 禁用：低俗用語、粗口

## 輸出格式
請以 JSON 格式輸出。

如果只有一種目標語言，格式如下：
```json
{{
  "optimized_content": {{
    "title": "優化後的標題",
    "selling_points": ["賣點1", "賣點2", "..."],
    "description": "優化後的描述",
    "short_description": "簡短描述（可選）"
  }},
  "suggestions": ["後續優化建議1", "後續優化建議2", "後續優化建議3"]
}}
```

如果有多種目標語言，格式如下（每種語言都要有完整內容）：
```json
{{
  "optimized_content": {{
    "TC": {{
      "title": "繁體中文標題",
      "selling_points": ["賣點1", "賣點2"],
      "description": "繁體中文描述"
    }},
    "SC": {{
      "title": "简体中文标题",
      "selling_points": ["卖点1", "卖点2"],
      "description": "简体中文描述"
    }},
    "EN": {{
      "title": "English Title",
      "selling_points": ["Point 1", "Point 2"],
      "description": "English description"
    }}
  }},
  "suggestions": ["後續優化建議1", "後續優化建議2", "後續優化建議3"]
}}
```

注意：
- 簡體中文 (SC) 要使用正確的簡體字
- 英文 (EN) 要自然流暢，不是直譯
- 只輸出 JSON，不要其他內容
"""
        return prompt

    def _format_content_for_prompt(self, content: Dict[str, Any]) -> str:
        """格式化內容用於 Prompt"""
        parts = []

        if content.get("title"):
            parts.append(f"**標題**: {content['title']}")

        if content.get("selling_points"):
            points = content["selling_points"]
            if isinstance(points, list):
                points_str = "\n".join([f"  - {p}" for p in points])
                parts.append(f"**賣點**:\n{points_str}")

        if content.get("description"):
            parts.append(f"**描述**: {content['description']}")

        if content.get("short_description"):
            parts.append(f"**簡短描述**: {content['short_description']}")

        return "\n\n".join(parts) if parts else "（無內容）"

    def _parse_optimization_response(
        self,
        response_text: str,
        current_content: Dict[str, Any],
        tokens_used: int,
        model: str,
    ) -> OptimizationResult:
        """解析優化響應"""
        try:
            # 嘗試提取 JSON
            json_str = response_text.strip()

            # 處理 markdown code block
            if "```json" in json_str:
                start = json_str.find("```json") + 7
                end = json_str.find("```", start)
                json_str = json_str[start:end].strip()
            elif "```" in json_str:
                start = json_str.find("```") + 3
                end = json_str.find("```", start)
                json_str = json_str[start:end].strip()

            data = json.loads(json_str)

            optimized = data.get("optimized_content", {})
            suggestions = data.get("suggestions", [])

            # 檢查是否為多語言格式（包含 TC, SC, EN 鍵）
            is_multilang = any(key in optimized for key in ["TC", "SC", "EN"])

            merged_content = {**current_content}

            if is_multilang:
                # 多語言格式：保留所有語言版本
                merged_content["multilang"] = {}
                for lang in ["TC", "SC", "EN"]:
                    if lang in optimized:
                        merged_content["multilang"][lang] = optimized[lang]

                # 使用繁體中文作為主要顯示（如有）
                primary_lang = optimized.get("TC") or optimized.get("SC") or optimized.get("EN", {})
                if primary_lang.get("title"):
                    merged_content["title"] = primary_lang["title"]
                if primary_lang.get("selling_points"):
                    merged_content["selling_points"] = primary_lang["selling_points"]
                if primary_lang.get("description"):
                    merged_content["description"] = primary_lang["description"]
                if primary_lang.get("short_description"):
                    merged_content["short_description"] = primary_lang.get("short_description")
            else:
                # 單語言格式：直接合併
                if optimized.get("title"):
                    merged_content["title"] = optimized["title"]
                if optimized.get("selling_points"):
                    merged_content["selling_points"] = optimized["selling_points"]
                if optimized.get("description"):
                    merged_content["description"] = optimized["description"]
                if optimized.get("short_description"):
                    merged_content["short_description"] = optimized["short_description"]

            # 默認建議
            if not suggestions:
                suggestions = [
                    "可以嘗試加入更多感官描寫",
                    "考慮加入限時優惠訊息",
                    "可以強調米芝蓮餐廳級別品質",
                ]

            return OptimizationResult(
                content=merged_content,
                suggestions=suggestions[:5],  # 最多 5 條建議
                tokens_used=tokens_used,
                model=model,
                success=True,
            )

        except (json.JSONDecodeError, KeyError) as e:
            # 解析失敗，返回原內容
            return OptimizationResult(
                content=current_content,
                suggestions=["AI 響應格式異常，請重試"],
                tokens_used=tokens_used,
                model=model,
                success=False,
                error=f"解析失敗: {str(e)}",
            )

    def get_quick_suggestions(self) -> List[Dict[str, str]]:
        """獲取快捷優化建議列表"""
        return [
            {"key": key, "label": value["label"], "instruction": value["instruction"]}
            for key, value in QUICK_OPTIMIZATION_SUGGESTIONS.items()
        ]


# =============================================
# 工廠函數
# =============================================

async def get_content_optimizer(ai_service: AIAnalysisService) -> ContentOptimizer:
    """獲取文案優化器實例"""
    return ContentOptimizer(ai_service=ai_service)
