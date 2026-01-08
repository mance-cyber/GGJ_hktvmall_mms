# =============================================
# AI 服務 - 支持中轉站 (自定義 Base URL)
# =============================================

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import httpx
import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.system import SystemSetting


# 常用模型列表
AVAILABLE_MODELS = [
    # Claude 系列
    {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "description": "最新平衡模型"},
    {"id": "claude-opus-4-20250514", "name": "Claude Opus 4", "description": "最強大模型"},
    {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "description": "高性價比"},
    {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "description": "快速經濟"},
    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "description": "舊版最強"},
    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "description": "舊版平衡"},
    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "description": "舊版快速"},
    # GPT 系列
    {"id": "gpt-4o", "name": "GPT-4o", "description": "OpenAI 最新"},
    {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "快速經濟"},
    {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "GPT-4 快速版"},
    {"id": "gpt-4", "name": "GPT-4", "description": "強大穩定"},
    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "經濟實惠"},
    # DeepSeek 系列
    {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "DeepSeek 對話"},
    {"id": "deepseek-coder", "name": "DeepSeek Coder", "description": "DeepSeek 代碼"},
    # 其他
    {"id": "custom", "name": "自定義模型", "description": "輸入任意模型名稱"},
]


@dataclass
class AIConfig:
    """AI 配置"""
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"  # 默認 OpenAI，可改為中轉站
    insights_model: str = "gpt-4o"  # 數據摘要用的模型
    strategy_model: str = "gpt-4o"  # Marketing 策略用的模型


@dataclass
class AIResponse:
    """AI 響應"""
    content: str
    model: str
    tokens_used: int = 0
    success: bool = True
    error: Optional[str] = None


class AISettingsService:
    """AI 設定服務 - 管理 API Key、Base URL 和模型選擇"""

    # 設定鍵名
    KEY_API_KEY = "ai_api_key"
    KEY_BASE_URL = "ai_base_url"
    KEY_INSIGHTS_MODEL = "ai_insights_model"
    KEY_STRATEGY_MODEL = "ai_strategy_model"

    @classmethod
    async def get_config(cls, db: AsyncSession) -> AIConfig:
        """獲取 AI 配置"""
        config = AIConfig()

        # 讀取所有設定
        result = await db.execute(
            select(SystemSetting).where(
                SystemSetting.key.in_([
                    cls.KEY_API_KEY,
                    cls.KEY_BASE_URL,
                    cls.KEY_INSIGHTS_MODEL,
                    cls.KEY_STRATEGY_MODEL,
                ])
            )
        )
        settings = {s.key: s.value for s in result.scalars().all()}

        if cls.KEY_API_KEY in settings:
            config.api_key = settings[cls.KEY_API_KEY]
        if cls.KEY_BASE_URL in settings:
            config.base_url = settings[cls.KEY_BASE_URL]
        if cls.KEY_INSIGHTS_MODEL in settings:
            config.insights_model = settings[cls.KEY_INSIGHTS_MODEL]
        if cls.KEY_STRATEGY_MODEL in settings:
            config.strategy_model = settings[cls.KEY_STRATEGY_MODEL]

        return config

    @classmethod
    async def save_config(
        cls,
        db: AsyncSession,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        insights_model: Optional[str] = None,
        strategy_model: Optional[str] = None,
    ) -> AIConfig:
        """保存 AI 配置"""
        updates = {}
        if api_key is not None:
            updates[cls.KEY_API_KEY] = api_key
        if base_url is not None:
            # 確保 URL 格式正確
            base_url = base_url.rstrip('/')
            updates[cls.KEY_BASE_URL] = base_url
        if insights_model is not None:
            updates[cls.KEY_INSIGHTS_MODEL] = insights_model
        if strategy_model is not None:
            updates[cls.KEY_STRATEGY_MODEL] = strategy_model

        for key, value in updates.items():
            existing = await db.execute(
                select(SystemSetting).where(SystemSetting.key == key)
            )
            setting = existing.scalar_one_or_none()

            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSetting(
                    key=key,
                    value=value,
                    description=f"AI 設定: {key}"
                )
                db.add(setting)

        await db.commit()
        return await cls.get_config(db)

    @classmethod
    async def test_connection(cls, api_key: str, base_url: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """測試 API 連接是否有效"""
        base_url = base_url.rstrip('/')
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 10,
                    }
                )
                
                if response.status_code == 200:
                    return {"valid": True, "message": "連接成功！"}
                elif response.status_code == 401:
                    return {"valid": False, "error": "API Key 無效或已過期"}
                elif response.status_code == 404:
                    return {"valid": False, "error": "API 端點不存在，請檢查 Base URL"}
                else:
                    error_text = response.text[:200] if response.text else "Unknown error"
                    return {"valid": False, "error": f"API 錯誤 ({response.status_code}): {error_text}"}
                    
        except httpx.ConnectError:
            return {"valid": False, "error": "無法連接到服務器，請檢查 Base URL"}
        except httpx.TimeoutException:
            return {"valid": False, "error": "連接超時，請檢查網絡或服務器狀態"}
        except Exception as e:
            return {"valid": False, "error": f"測試失敗: {str(e)}"}

    @classmethod
    def get_available_models(cls) -> List[Dict[str, str]]:
        """獲取預設可用模型列表"""
        return AVAILABLE_MODELS

    @classmethod
    async def fetch_models_from_api(
        cls,
        api_key: str,
        base_url: str
    ) -> Dict[str, Any]:
        """
        從 API 動態獲取可用模型列表

        大多數 OpenAI 兼容 API 都支持 /models 端點

        Returns:
            {
                "success": bool,
                "models": [{"id": "...", "name": "...", "owned_by": "..."}],
                "error": str | None
            }
        """
        base_url = base_url.rstrip('/')

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{base_url}/models",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    models_data = data.get("data", [])

                    # 處理模型列表
                    models = []
                    for m in models_data:
                        model_id = m.get("id", "")
                        # 過濾掉非聊天模型（如 embedding、whisper 等）
                        if any(skip in model_id.lower() for skip in [
                            "embedding", "whisper", "tts", "dall-e",
                            "moderation", "search", "similarity"
                        ]):
                            continue

                        models.append({
                            "id": model_id,
                            "name": cls._format_model_name(model_id),
                            "owned_by": m.get("owned_by", "unknown"),
                            "created": m.get("created"),
                        })

                    # 按名稱排序
                    models.sort(key=lambda x: x["name"])

                    return {
                        "success": True,
                        "models": models,
                        "total": len(models)
                    }

                elif response.status_code == 401:
                    return {
                        "success": False,
                        "models": [],
                        "error": "API Key 無效"
                    }
                elif response.status_code == 404:
                    # 某些中轉站可能不支持 /models 端點
                    return {
                        "success": False,
                        "models": [],
                        "error": "此 API 不支持獲取模型列表，請手動選擇模型"
                    }
                else:
                    return {
                        "success": False,
                        "models": [],
                        "error": f"API 錯誤 ({response.status_code})"
                    }

        except httpx.ConnectError:
            return {
                "success": False,
                "models": [],
                "error": "無法連接到服務器"
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "models": [],
                "error": "連接超時"
            }
        except Exception as e:
            return {
                "success": False,
                "models": [],
                "error": f"獲取失敗: {str(e)}"
            }

    @classmethod
    def _format_model_name(cls, model_id: str) -> str:
        """格式化模型名稱，使其更易讀"""
        # 常見模型的友好名稱映射
        friendly_names = {
            "gpt-4o": "GPT-4o",
            "gpt-4o-mini": "GPT-4o Mini",
            "gpt-4-turbo": "GPT-4 Turbo",
            "gpt-4": "GPT-4",
            "gpt-3.5-turbo": "GPT-3.5 Turbo",
            "claude-3-opus": "Claude 3 Opus",
            "claude-3-sonnet": "Claude 3 Sonnet",
            "claude-3-haiku": "Claude 3 Haiku",
            "claude-3-5-sonnet": "Claude 3.5 Sonnet",
            "claude-3-5-haiku": "Claude 3.5 Haiku",
            "claude-sonnet-4": "Claude Sonnet 4",
            "claude-opus-4": "Claude Opus 4",
            "deepseek-chat": "DeepSeek Chat",
            "deepseek-coder": "DeepSeek Coder",
        }

        # 檢查是否有匹配的友好名稱
        for key, name in friendly_names.items():
            if model_id.startswith(key):
                return name

        # 否則返回原始 ID（首字母大寫）
        return model_id.replace("-", " ").title()


class AIAnalysisService:
    """AI 分析服務 - 執行數據摘要和策略生成"""

    def __init__(self, config: AIConfig):
        self.config = config
        self.base_url = config.base_url.rstrip('/')

    def _call_api(self, prompt: str, model: str, max_tokens: int = 2048) -> AIResponse:
        """調用 OpenAI 兼容 API（同步版本）"""
        if not self.config.api_key:
            return AIResponse(
                content="",
                model="",
                success=False,
                error="API Key 未設定"
            )

        try:
            import httpx
            
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                    }
                )

                if response.status_code != 200:
                    error_text = response.text[:300] if response.text else "Unknown error"
                    return AIResponse(
                        content="",
                        model=model,
                        success=False,
                        error=f"API 錯誤 ({response.status_code}): {error_text}"
                    )

                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                tokens = usage.get("total_tokens", 0)

                return AIResponse(
                    content=content,
                    model=model,
                    tokens_used=tokens,
                    success=True
                )

        except httpx.ConnectError:
            return AIResponse(
                content="",
                model=model,
                success=False,
                error="無法連接到 API 服務器"
            )
        except httpx.TimeoutException:
            return AIResponse(
                content="",
                model=model,
                success=False,
                error="API 請求超時"
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=model,
                success=False,
                error=f"API 調用失敗: {str(e)}"
            )

    async def call_ai(self, prompt: str, max_tokens: int = 2048) -> AIResponse:
        """
        調用 AI API（異步版本）

        用於 Agent 服務中的意圖識別和報告生成
        """
        if not self.config.api_key:
            return AIResponse(
                content="",
                model="",
                success=False,
                error="API Key 未設定"
            )

        model = self.config.insights_model

        try:
            # 使用較短的超時時間，避免長時間等待
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                    }
                )

                if response.status_code != 200:
                    error_text = response.text[:300] if response.text else "Unknown error"
                    return AIResponse(
                        content="",
                        model=model,
                        success=False,
                        error=f"API 錯誤 ({response.status_code}): {error_text}"
                    )

                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                tokens = usage.get("total_tokens", 0)

                return AIResponse(
                    content=content,
                    model=model,
                    tokens_used=tokens,
                    success=True
                )

        except httpx.ConnectError:
            return AIResponse(
                content="",
                model=model,
                success=False,
                error="無法連接到 API 服務器"
            )
        except httpx.TimeoutException:
            return AIResponse(
                content="",
                model=model,
                success=False,
                error="API 請求超時（60秒）"
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=model,
                success=False,
                error=f"API 調用失敗: {str(e)}"
            )

    def generate_data_insights(self, data: Dict[str, Any]) -> AIResponse:
        """
        生成數據摘要
        
        AI #1: 分析數據 → 出數據摘要
        """
        prompt = f"""你是一位專業的市場數據分析師。請根據以下數據生成一份簡潔但全面的數據摘要報告。

## 數據輸入

```json
{json.dumps(data, ensure_ascii=False, indent=2)}
```

## 報告要求

請生成繁體中文報告，包含以下部分：

### 1. 核心數據摘要
- 用 3-5 個要點總結最重要的數據發現
- 每個要點包含具體數字

### 2. 趨勢分析
- 識別價格趨勢（上漲/下跌/穩定）
- 識別庫存/供應趨勢
- 競爭對手動態

### 3. 異常標記
- 標記任何需要關注的異常數據
- 價格大幅波動
- 缺貨風險

### 4. 關鍵洞察
- 2-3 個基於數據的關鍵洞察
- 這些洞察應該對業務決策有幫助

請用簡潔專業的語言，避免冗長的解釋。重點突出數據和趨勢。
"""

        return self._call_api(
            prompt=prompt,
            model=self.config.insights_model,
            max_tokens=2048
        )

    def generate_marketing_strategy(self, insights: str, context: Dict[str, Any]) -> AIResponse:
        """
        生成 Marketing 策略

        AI #2: 讀取摘要 → 出 Marketing 策略建議
        """
        prompt = f"""你是一位資深的市場營銷策略專家。根據數據分析摘要和業務背景，制定未來的營銷策略建議。

## 數據分析摘要

{insights}

## 業務背景

```json
{json.dumps(context, ensure_ascii=False, indent=2)}
```

## 策略報告要求

請生成繁體中文的營銷策略報告，包含以下部分：

### 1. 戰略方向摘要
- 用一句話總結核心策略方向

### 2. 短期行動計劃（1-2 週）
針對每個建議，提供：
- **行動**: 具體要做什麼
- **目標**: 預期達成什麼效果
- **優先級**: 高/中/低

### 3. 中期營銷策略（1-3 個月）
- 定價策略建議
- 促銷活動建議
- 庫存管理建議
- 競爭對手應對策略

### 4. 內容營銷建議
- 社交媒體文案方向
- 推薦的營銷角度
- 季節性營銷機會

### 5. 風險提醒
- 需要關注的市場風險
- 建議的應對措施

請提供具體、可執行的建議，而非泛泛而談。每個建議都應該基於數據分析的結果。
"""

        return self._call_api(
            prompt=prompt,
            model=self.config.strategy_model,
            max_tokens=3000
        )

    def generate_product_content(
        self,
        product_name: str,
        product_info: Dict[str, Any],
        content_type: str = "product_description",
        style: str = "professional",
        language: str = "zh-HK"
    ) -> AIResponse:
        """
        生成商品文案

        Args:
            product_name: 商品名稱
            product_info: 商品資訊（價格、描述、特點等）
            content_type: 內容類型（product_description, social_post, ad_copy）
            style: 風格（professional, casual, luxury, playful）
            language: 語言（zh-HK, zh-TW, zh-CN, en）

        Returns:
            AIResponse 包含生成的文案
        """
        # 根據內容類型設定 prompt
        content_type_prompts = {
            "product_description": "詳細的商品描述，適合在電商平台展示",
            "social_post": "適合社交媒體發布的推廣文案，要吸引眼球",
            "ad_copy": "廣告文案，簡短有力，突出賣點",
            "seo_description": "SEO 優化的商品描述，包含關鍵字",
        }

        style_descriptions = {
            "professional": "專業正式的語調",
            "casual": "輕鬆親切的語調",
            "luxury": "高端奢華的語調",
            "playful": "活潑有趣的語調",
        }

        language_names = {
            "zh-HK": "繁體中文（香港）",
            "zh-TW": "繁體中文（台灣）",
            "zh-CN": "簡體中文",
            "en": "英文",
        }

        content_desc = content_type_prompts.get(content_type, content_type_prompts["product_description"])
        style_desc = style_descriptions.get(style, style_descriptions["professional"])
        lang_name = language_names.get(language, language_names["zh-HK"])

        prompt = f"""你是一位專業的電商文案撰寫專家。請根據以下商品資訊，生成高質量的商品文案。

## 商品資訊

商品名稱: {product_name}

詳細資訊:
```json
{json.dumps(product_info, ensure_ascii=False, indent=2)}
```

## 文案要求

- **內容類型**: {content_desc}
- **風格**: {style_desc}
- **語言**: {lang_name}

## 輸出格式

請以 JSON 格式輸出，包含以下欄位：

```json
{{
    "title": "吸引人的標題（20字以內）",
    "selling_points": ["賣點1", "賣點2", "賣點3"],
    "description": "詳細描述（100-200字）",
    "short_description": "簡短描述（50字以內）",
    "hashtags": ["#標籤1", "#標籤2", "#標籤3"]
}}
```

## 注意事項

1. 標題要吸引眼球，突出商品最大賣點
2. 賣點要具體、有說服力，最好包含數字或具體優勢
3. 描述要詳盡但不冗長，突出商品價值
4. 使用符合{lang_name}習慣的表達方式
5. 確保輸出是有效的 JSON 格式

請直接輸出 JSON，不要加其他解釋文字。
"""

        return self._call_api(
            prompt=prompt,
            model=self.config.insights_model,  # 使用 insights 模型
            max_tokens=1500
        )


# 服務工廠函數
async def get_ai_analysis_service(db: AsyncSession) -> AIAnalysisService:
    """獲取 AI 分析服務實例"""
    config = await AISettingsService.get_config(db)
    return AIAnalysisService(config)
