# =============================================
# Claude AI 連接器
# =============================================

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import anthropic

from app.config import get_settings


@dataclass
class GeneratedContent:
    """生成的內容"""
    title: Optional[str] = None
    selling_points: Optional[List[str]] = None
    description: Optional[str] = None
    full_copy: Optional[str] = None
    tokens_used: int = 0
    model: str = ""


class ClaudeConnector:
    """Claude AI 連接器"""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.anthropic_api_key
        self.model = settings.ai_model
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key and self.api_key.startswith("sk-ant-") else None

    def generate_content(
        self,
        product_info: Dict[str, Any],
        content_type: str = "full_copy",
        style: str = "professional",
        language: str = "zh-HK",
    ) -> GeneratedContent:
        """
        生成商品文案

        Args:
            product_info: 商品資訊字典
            content_type: 內容類型 (title, description, selling_points, full_copy)
            style: 風格 (formal, casual, playful, professional)
            language: 語言 (zh-HK, zh-TW, en)

        Returns:
            GeneratedContent 對象
        """
        if not self.client:
            # 返回模擬數據
            return self._generate_mock_content(product_info, content_type, style, language)

        # 構建提示
        prompt = self._build_prompt(product_info, content_type, style, language)

        # 調用 Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # 解析響應
        response_text = message.content[0].text if message.content else ""
        tokens_used = message.usage.input_tokens + message.usage.output_tokens

        return self._parse_response(response_text, content_type, tokens_used)

    def _build_prompt(
        self,
        product_info: Dict[str, Any],
        content_type: str,
        style: str,
        language: str,
    ) -> str:
        """構建生成提示"""
        language_map = {
            "zh-HK": "繁體中文（香港）",
            "zh-TW": "繁體中文（台灣）",
            "en": "English",
        }
        lang = language_map.get(language, "繁體中文（香港）")

        style_map = {
            "formal": "正式、專業",
            "casual": "輕鬆、親和",
            "playful": "活潑、有趣",
            "professional": "專業、可信賴",
        }
        style_desc = style_map.get(style, "專業、可信賴")

        product_name = product_info.get("name", "商品")
        brand = product_info.get("brand", "")
        features = product_info.get("features", [])
        target_audience = product_info.get("target_audience", "")
        price = product_info.get("price", "")
        category = product_info.get("category", "")

        base_prompt = f"""
你是一位專業的電商文案撰寫專家。請為以下商品生成{lang}的銷售文案。

商品資訊：
- 名稱：{product_name}
- 品牌：{brand}
- 類別：{category}
- 特點：{', '.join(features) if features else '無'}
- 目標客群：{target_audience}
- 價格：{price}

風格要求：{style_desc}
"""

        if content_type == "title":
            return base_prompt + """
請生成一個吸引人的商品標題（20-50字），包含品牌名和主要賣點。
只輸出標題，不要其他內容。
"""
        elif content_type == "description":
            return base_prompt + """
請生成一段商品描述（100-200字），突出商品優勢和使用場景。
只輸出描述，不要其他內容。
"""
        elif content_type == "selling_points":
            return base_prompt + """
請生成3-5個賣點（每個15-30字），突出商品的核心優勢。
格式：每行一個賣點，以 "- " 開頭。
"""
        else:  # full_copy
            return base_prompt + """
請生成完整的商品文案，包含：
1. 標題（20-50字）
2. 3-5個賣點
3. 詳細描述（100-200字）

格式：
【標題】
（標題內容）

【賣點】
- 賣點1
- 賣點2
- 賣點3

【描述】
（描述內容）
"""

    def _parse_response(
        self,
        response_text: str,
        content_type: str,
        tokens_used: int,
    ) -> GeneratedContent:
        """解析 Claude 響應"""
        result = GeneratedContent(
            tokens_used=tokens_used,
            model=self.model,
        )

        if content_type == "title":
            result.title = response_text.strip()
        elif content_type == "description":
            result.description = response_text.strip()
        elif content_type == "selling_points":
            points = [
                line.strip().lstrip("- ").lstrip("•").strip()
                for line in response_text.split("\n")
                if line.strip() and (line.strip().startswith("-") or line.strip().startswith("•"))
            ]
            result.selling_points = points
        else:  # full_copy
            result.full_copy = response_text.strip()
            # 嘗試解析結構化內容
            self._parse_full_copy(response_text, result)

        return result

    def _parse_full_copy(self, text: str, result: GeneratedContent):
        """從完整文案中解析結構化內容"""
        import re

        # 提取標題
        title_match = re.search(r"【標題】\s*(.+?)(?=【|$)", text, re.DOTALL)
        if title_match:
            result.title = title_match.group(1).strip()

        # 提取賣點
        points_match = re.search(r"【賣點】\s*(.+?)(?=【|$)", text, re.DOTALL)
        if points_match:
            points_text = points_match.group(1)
            points = [
                line.strip().lstrip("- ").lstrip("•").strip()
                for line in points_text.split("\n")
                if line.strip() and (line.strip().startswith("-") or line.strip().startswith("•"))
            ]
            result.selling_points = points

        # 提取描述
        desc_match = re.search(r"【描述】\s*(.+?)(?=【|$)", text, re.DOTALL)
        if desc_match:
            result.description = desc_match.group(1).strip()

    def _generate_mock_content(
        self,
        product_info: Dict[str, Any],
        content_type: str,
        style: str,
        language: str,
    ) -> GeneratedContent:
        """生成模擬內容（API Key 未設定時使用）"""
        product_name = product_info.get("name", "商品")
        brand = product_info.get("brand", "")

        title = f"【{brand}】{product_name}" if brand else f"【優質推薦】{product_name}"

        return GeneratedContent(
            title=title,
            selling_points=[
                "高品質保證，信心之選",
                "快速出貨，準時送達",
                "專業客服，售後無憂",
            ],
            description=f"這是 {product_name} 的示例描述。實際內容將由 Claude AI 生成。請確保已正確設定 ANTHROPIC_API_KEY 環境變數。",
            full_copy=f"【標題】\n{title}\n\n【賣點】\n- 高品質保證\n- 快速出貨\n- 專業客服\n\n【描述】\n{product_name} 示例描述。",
            tokens_used=0,
            model="mock",
        )


# 單例
_connector: Optional[ClaudeConnector] = None


def get_claude_connector() -> ClaudeConnector:
    """獲取 Claude 連接器單例"""
    global _connector
    if _connector is None:
        _connector = ClaudeConnector()
    return _connector
