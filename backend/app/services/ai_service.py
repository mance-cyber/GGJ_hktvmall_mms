# =============================================
# AI 服務 - 支持中轉站 (自定義 Base URL)
# =============================================

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import httpx
import json
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.system import SystemSetting
from app.config import get_settings


# =============================================
# 任務複雜度枚舉
# =============================================

class TaskComplexity(str, Enum):
    """任務複雜度等級"""
    SIMPLE = "simple"      # 簡單任務：競品映射、SEO 關鍵詞、基礎分析
    MEDIUM = "medium"      # 中等任務：文案生成、定價分析、內容優化
    COMPLEX = "complex"    # 複雜任務：市場簡報、戰略建議、深度分析


# 常用模型列表
AVAILABLE_MODELS = [
    # Claude 4.x 系列（最新）
    {"id": "claude-opus-4-6-thinking", "name": "Claude Opus 4.6 Thinking", "description": "最強思考模型（中轉 API）"},
    {"id": "claude-haiku-4-5-20251001-thinking", "name": "Claude Haiku 4.5 Thinking", "description": "經濟思考模型（中轉 API）"},
    {"id": "claude-opus-4-6-20250229", "name": "Claude Opus 4.6", "description": "最新最強大模型"},
    {"id": "claude-sonnet-4-5-20250929", "name": "Claude Sonnet 4.5", "description": "最新平衡模型"},
    {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4", "description": "平衡模型"},
    {"id": "claude-opus-4-20250514", "name": "Claude Opus 4", "description": "強大模型"},
    # Claude 3.x 系列
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


def _get_default_base_url() -> str:
    """獲取預設 Base URL（從配置讀取）"""
    return get_settings().openai_base_url


def _get_default_model() -> str:
    """獲取預設模型（從配置讀取）"""
    return get_settings().openai_default_model


@dataclass
class AIConfig:
    """AI 配置（支持多模型分級）"""
    api_key: str = ""
    base_url: str = field(default_factory=_get_default_base_url)  # API 端點

    # 單模型配置（向後兼容）
    insights_model: str = field(default_factory=_get_default_model)  # 數據摘要
    strategy_model: str = field(default_factory=_get_default_model)  # 策略建議

    # 多模型分級配置（新增）
    simple_model: str = "claude-haiku-4-5-20251001-thinking"    # 簡單任務
    medium_model: str = "claude-opus-4-6-thinking"               # 中等任務
    complex_model: str = "claude-opus-4-6-thinking"              # 複雜任務

    def get_model_by_complexity(self, complexity: TaskComplexity) -> str:
        """根據任務複雜度返回對應模型"""
        if complexity == TaskComplexity.SIMPLE:
            return self.simple_model
        elif complexity == TaskComplexity.MEDIUM:
            return self.medium_model
        else:  # COMPLEX
            return self.complex_model


@dataclass
class AIResponse:
    """AI 響應"""
    content: str
    model: str
    tokens_used: int = 0
    success: bool = True
    error: Optional[str] = None


class AISettingsService:
    """AI 設定服務 - 管理 API Key、Base URL 和模型選擇（支持多模型分級）"""

    # 設定鍵名
    KEY_API_KEY = "ai_api_key"
    KEY_BASE_URL = "ai_base_url"
    KEY_INSIGHTS_MODEL = "ai_insights_model"
    KEY_STRATEGY_MODEL = "ai_strategy_model"

    # 多模型分級設定（新增）
    KEY_SIMPLE_MODEL = "ai_simple_model"
    KEY_MEDIUM_MODEL = "ai_medium_model"
    KEY_COMPLEX_MODEL = "ai_complex_model"

    @classmethod
    async def get_config(cls, db: AsyncSession) -> AIConfig:
        """獲取 AI 配置（支持多模型分級）"""
        settings_obj = get_settings()
        config = AIConfig()

        # 優先從環境變數讀取
        if settings_obj.ai_api_key or settings_obj.anthropic_api_key:
            config.api_key = settings_obj.ai_api_key or settings_obj.anthropic_api_key
        if settings_obj.ai_base_url:
            config.base_url = settings_obj.ai_base_url

        # 多模型分級配置（優先從環境變數）
        config.simple_model = settings_obj.ai_model_simple
        config.medium_model = settings_obj.ai_model_medium
        config.complex_model = settings_obj.ai_model_complex

        # 讀取數據庫設定（可覆蓋環境變數）
        result = await db.execute(
            select(SystemSetting).where(
                SystemSetting.key.in_([
                    cls.KEY_API_KEY,
                    cls.KEY_BASE_URL,
                    cls.KEY_INSIGHTS_MODEL,
                    cls.KEY_STRATEGY_MODEL,
                    cls.KEY_SIMPLE_MODEL,
                    cls.KEY_MEDIUM_MODEL,
                    cls.KEY_COMPLEX_MODEL,
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

        # 多模型配置（數據庫優先）
        if cls.KEY_SIMPLE_MODEL in settings:
            config.simple_model = settings[cls.KEY_SIMPLE_MODEL]
        if cls.KEY_MEDIUM_MODEL in settings:
            config.medium_model = settings[cls.KEY_MEDIUM_MODEL]
        if cls.KEY_COMPLEX_MODEL in settings:
            config.complex_model = settings[cls.KEY_COMPLEX_MODEL]

        return config

    @classmethod
    async def save_config(
        cls,
        db: AsyncSession,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        insights_model: Optional[str] = None,
        strategy_model: Optional[str] = None,
        simple_model: Optional[str] = None,
        medium_model: Optional[str] = None,
        complex_model: Optional[str] = None,
    ) -> AIConfig:
        """保存 AI 配置（支持多模型分級）"""
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

        # 多模型配置
        if simple_model is not None:
            updates[cls.KEY_SIMPLE_MODEL] = simple_model
        if medium_model is not None:
            updates[cls.KEY_MEDIUM_MODEL] = medium_model
        if complex_model is not None:
            updates[cls.KEY_COMPLEX_MODEL] = complex_model

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
        """測試 API 連接是否有效（OpenAI 格式）"""
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
    async def test_claude_connection(
        cls,
        api_key: str,
        base_url: str,
        model: str = "claude-haiku-4-5-20251001-thinking"
    ) -> Dict[str, Any]:
        """
        測試 Claude API 連接（Anthropic 格式）

        用於測試 GPT-Best 等中轉 API 是否能正常調用 Claude 模型
        """
        base_url = base_url.rstrip('/')

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url}/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "max_tokens": 50,
                        "messages": [
                            {"role": "user", "content": "請用一句話回覆：你好"}
                        ]
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data.get("content", [{}])[0].get("text", "")
                    usage = data.get("usage", {})
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)

                    return {
                        "valid": True,
                        "message": "✅ Claude API 連接成功！",
                        "model": model,
                        "response": content,
                        "tokens": {
                            "input": input_tokens,
                            "output": output_tokens,
                            "total": input_tokens + output_tokens
                        }
                    }
                elif response.status_code == 401:
                    return {
                        "valid": False,
                        "error": "❌ API Key 無效或已過期",
                        "status_code": 401
                    }
                elif response.status_code == 404:
                    return {
                        "valid": False,
                        "error": f"❌ 端點不存在: {base_url}/messages\n請確認 Base URL 是否正確",
                        "status_code": 404,
                        "hint": "正確格式例如：https://api.gpt-best.com/v1"
                    }
                elif response.status_code == 400:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("error", {}).get("message", response.text[:200])
                    return {
                        "valid": False,
                        "error": f"❌ 請求錯誤: {error_msg}",
                        "status_code": 400,
                        "hint": f"可能原因：模型 '{model}' 不存在或不可用"
                    }
                else:
                    error_text = response.text[:300] if response.text else "Unknown error"
                    return {
                        "valid": False,
                        "error": f"❌ API 錯誤 ({response.status_code}): {error_text}",
                        "status_code": response.status_code
                    }

        except httpx.ConnectError:
            return {
                "valid": False,
                "error": "❌ 無法連接到服務器",
                "hint": f"請檢查 Base URL: {base_url}"
            }
        except httpx.TimeoutException:
            return {
                "valid": False,
                "error": "❌ 連接超時（60秒）",
                "hint": "請檢查網絡連接或服務器狀態"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"❌ 測試失敗: {str(e)}"
            }

    @classmethod
    async def test_environment_config(cls) -> Dict[str, Any]:
        """
        測試環境變數配置

        不調用 API，只檢查 Zeabur 環境變數是否正確載入
        """
        settings_obj = get_settings()

        # 檢查各項配置
        config_status = {
            "ai_base_url": {
                "value": settings_obj.ai_base_url,
                "set": bool(settings_obj.ai_base_url and settings_obj.ai_base_url != "https://api.anthropic.com"),
                "source": "環境變數 AI_BASE_URL"
            },
            "ai_api_key": {
                "value": f"{settings_obj.ai_api_key[:8]}...{settings_obj.ai_api_key[-4:]}" if settings_obj.ai_api_key and len(settings_obj.ai_api_key) > 12 else "***",
                "set": bool(settings_obj.ai_api_key),
                "source": "環境變數 AI_API_KEY"
            },
            "anthropic_api_key": {
                "value": f"{settings_obj.anthropic_api_key[:8]}...{settings_obj.anthropic_api_key[-4:]}" if settings_obj.anthropic_api_key and len(settings_obj.anthropic_api_key) > 12 else "***",
                "set": bool(settings_obj.anthropic_api_key),
                "source": "環境變數 ANTHROPIC_API_KEY（官方 API）"
            },
            "ai_model_simple": {
                "value": settings_obj.ai_model_simple,
                "set": True,
                "source": "環境變數 AI_MODEL_SIMPLE"
            },
            "ai_model_medium": {
                "value": settings_obj.ai_model_medium,
                "set": True,
                "source": "環境變數 AI_MODEL_MEDIUM"
            },
            "ai_model_complex": {
                "value": settings_obj.ai_model_complex,
                "set": True,
                "source": "環境變數 AI_MODEL_COMPLEX"
            }
        }

        # 判斷整體狀態
        using_relay_api = config_status["ai_base_url"]["set"]
        has_api_key = config_status["ai_api_key"]["set"] or config_status["anthropic_api_key"]["set"]

        # 生成建議
        recommendations = []
        if not using_relay_api:
            recommendations.append("⚠️ AI_BASE_URL 未設置或使用預設值，目前使用 Anthropic 官方 API")
            recommendations.append("💡 若要使用 GPT-Best 中轉 API，請設置：AI_BASE_URL=https://api.gpt-best.com/v1")

        if not config_status["ai_api_key"]["set"] and using_relay_api:
            recommendations.append("⚠️ 使用中轉 API 但 AI_API_KEY 未設置")
            recommendations.append("💡 請在 Zeabur 添加環境變數：AI_API_KEY=<你的 GPT-Best API Key>")

        if not has_api_key:
            recommendations.append("❌ 未設置任何 API Key，AI 功能將無法使用")

        return {
            "status": "ready" if (using_relay_api and config_status["ai_api_key"]["set"]) or (not using_relay_api and config_status["anthropic_api_key"]["set"]) else "incomplete",
            "using_relay_api": using_relay_api,
            "has_api_key": has_api_key,
            "config": config_status,
            "recommendations": recommendations,
            "summary": f"{'✅ 配置完整' if has_api_key else '❌ 配置不完整'} | {'使用中轉 API' if using_relay_api else '使用官方 API'}"
        }

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
        target_languages: Optional[List[str]] = None,
    ) -> AIResponse:
        """
        生成商品文案

        Args:
            product_name: 商品名稱
            product_info: 商品資訊（價格、描述、特點等）
            content_type: 內容類型（product_description, social_post, ad_copy）
            style: 風格（professional, casual, luxury, playful）
            target_languages: 目標語言列表 ["TC", "SC", "EN"]

        Returns:
            AIResponse 包含生成的文案
        """
        if target_languages is None:
            target_languages = ["TC"]

        style_descriptions = {
            "professional": "專業優雅，適量加入輕口語增加親切感",
            "casual": "輕鬆親切，多用口語詞彙如「超正」「好食到喊」",
            "luxury": "高端奢華，強調品質與尊貴感",
            "playful": "活潑有趣，多用感嘆句和網絡流行語",
        }

        language_names = {
            "TC": "繁體中文（香港）",
            "SC": "簡體中文",
            "EN": "英文",
        }

        style_desc = style_descriptions.get(style, style_descriptions["professional"])
        target_lang_str = "、".join([language_names.get(l, l) for l in target_languages])
        is_multilang = len(target_languages) > 1

        # 構建輸出格式模板（避免 f-string 嵌套問題）
        if is_multilang:
            lang_entries = []
            for lang in target_languages:
                lang_name = language_names.get(lang, lang)
                lang_entries.append(f'''"{lang}": {{
        "title": "{lang_name}標題",
        "selling_points": ["賣點1", "賣點2", "賣點3", "賣點4", "賣點5"],
        "description": "{lang_name}完整描述",
        "short_description": "{lang_name}簡短描述"
    }}''')
            multilang_json_example = "{\n    " + ",\n    ".join(lang_entries) + "\n}"
            output_format = f"""**多語言格式**（必須為每種語言生成完整內容）：

```json
{multilang_json_example}
```

**重要**：
- 每種語言都必須有完整內容，不是翻譯而是針對該語言重新創作
- 簡體中文 (SC) 必須使用正確的簡體字
- 英文 (EN) 要自然流暢，符合英語習慣，不是直譯
"""
        else:
            output_format = """```json
{
    "title": "按上述策略創作的吸引人標題（20-30字）",
    "selling_points": [
        "賣點1（必須包含五星酒店/米芝蓮背書）",
        "賣點2（產地/品質/規格優勢）",
        "賣點3（鎖鮮技術/冷鏈優勢）",
        "賣點4（便利性/快速上桌）",
        "賣點5（性價比優勢）"
    ],
    "description": "完整文案（150-250字）：痛點開頭 → 背書建立信任 → 感官描寫 → 性價比收殺",
    "short_description": "簡短描述（50字以內）：一句話抓住核心賣點"
}
```"""

        prompt = f"""你同時扮演三個專業角色來創作文案：

1. **GogoJap 電商文案總監** — 撰寫讓香港人心動下單的產品描述
2. **銷售心理專家** — 以「不買不行」的心理策略設計文案
3. **香港消費者代言人** — 代入貼地客人視角審視文案是否真正打動人心

---

## GogoJap 品牌背景（必須融入文案）

- 香港米芝蓮星級餐廳及五星酒店食材供應商（半島酒店、文華東方、四季酒店、Zuma、Amber、Sushi Shikon）
- 柴灣自有 HACCP 認證加工中心，日處理量達 5,000+ 訂單
- -18°C 全程專業冷鏈，從倉庫到府最快 4 小時送達
- 每週空運/海運直送，產地直採無中間商
- 多位五星酒店鐵板燒/壽司主廚私下指定使用

**品牌承諾**: 「餐廳級食材，屋企價享受」— 米芝蓮同級品質，只需餐廳 1/5 價格

---

## 商品資訊

商品名稱: {product_name}

詳細資訊:
```json
{json.dumps(product_info, ensure_ascii=False, indent=2)}
```

---

## 創作前必須完成的分析（內部思考，不需輸出）

### Step 1: 產品核心價值分析
- 這個產品最獨特的賣點是什麼？
- 與市面同類產品相比有什麼優勢？
- 為什麼消費者應該選擇這個而不是其他？

### Step 2: 目標客戶痛點分析
- 消費者買這類產品最擔心什麼？（品質不穩定？不新鮮？CP值低？）
- 他們有什麼未被滿足的需求？
- 什麼情境會觸發他們的購買慾望？

### Step 3: 心理觸發點設計
- 用什麼「鉤子」能立即抓住注意力？
- 如何建立信任感？（專業背書、數據證明）
- 如何製造緊迫感或稀缺感？

---

## 標題創作策略（最重要！）

標題是決定點擊率的關鍵，必須遵循以下公式：

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
   - 「網購急凍肉擔心不夠新鮮、解凍乾柴？」
   - 「超市貨永遠比不上餐廳級？」

2. **專業背書**：建立信任
   - 「我哋係半島酒店、文華東方指定供應商...」

3. **感官描寫**：觸發慾望
   - 「入口即溶、油花綻放如大理石紋、肉汁爆棚...」

4. **性價比收殺**：促成下單
   - 「平時去米芝蓮餐廳食同級食材動輒 $800-$1,200，而家屋企只需 1/5 價格」

---

## 輸出要求

- **風格**: {style_desc}
- **目標語言**: {target_lang_str}

請以 JSON 格式輸出。

{output_format}

請直接輸出 JSON，不要加其他解釋文字。確保標題真正吸引人，而不是單純拼湊產品資訊！
"""

        return self._call_api(
            prompt=prompt,
            model=self.config.insights_model,
            max_tokens=2000
        )


# 服務工廠函數
async def get_ai_analysis_service(db: AsyncSession) -> AIAnalysisService:
    """獲取 AI 分析服務實例"""
    config = await AISettingsService.get_config(db)
    return AIAnalysisService(config)
