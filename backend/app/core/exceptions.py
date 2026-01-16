# =============================================
# 標準化異常處理
# =============================================

from typing import Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


# =============================================
# 標準錯誤響應 Schema
# =============================================

class ErrorDetail(BaseModel):
    """錯誤詳情"""
    field: Optional[str] = None
    message: str


class StandardErrorResponse(BaseModel):
    """
    標準化 API 錯誤響應格式

    所有 API 錯誤都應遵循此格式，確保前端可統一處理。
    """
    error: str  # 錯誤類型標識符 (如 "NOT_FOUND", "VALIDATION_ERROR")
    message: str  # 人類可讀的錯誤訊息
    details: Optional[list[ErrorDetail]] = None  # 詳細錯誤信息（用於驗證錯誤）
    request_id: Optional[str] = None  # 請求追蹤 ID（未來擴展）


# =============================================
# 自定義異常類
# =============================================

class AppException(HTTPException):
    """應用程式基礎異常"""

    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        details: Optional[list[dict]] = None,
    ):
        self.error = error
        self.message = message
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class NotFoundError(AppException):
    """資源不存在"""

    def __init__(self, resource: str = "資源", message: Optional[str] = None):
        super().__init__(
            status_code=404,
            error="NOT_FOUND",
            message=message or f"{resource}不存在",
        )


class ValidationError(AppException):
    """驗證錯誤"""

    def __init__(self, message: str, details: Optional[list[dict]] = None):
        super().__init__(
            status_code=400,
            error="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class DuplicateError(AppException):
    """重複資源錯誤"""

    def __init__(self, resource: str = "資源", field: str = ""):
        message = f"{resource}已存在" if not field else f"{field} 已被使用"
        super().__init__(
            status_code=409,
            error="DUPLICATE_RESOURCE",
            message=message,
        )


class UnauthorizedError(AppException):
    """未授權"""

    def __init__(self, message: str = "請先登入"):
        super().__init__(
            status_code=401,
            error="UNAUTHORIZED",
            message=message,
        )


class ForbiddenError(AppException):
    """無權限"""

    def __init__(self, message: str = "沒有權限執行此操作"):
        super().__init__(
            status_code=403,
            error="FORBIDDEN",
            message=message,
        )


class ServiceUnavailableError(AppException):
    """服務不可用"""

    def __init__(self, service: str = "服務", message: Optional[str] = None):
        super().__init__(
            status_code=503,
            error="SERVICE_UNAVAILABLE",
            message=message or f"{service}暫時不可用，請稍後再試",
        )


class RateLimitError(AppException):
    """請求頻率限制"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=429,
            error="RATE_LIMIT_EXCEEDED",
            message=f"請求過於頻繁，請 {retry_after} 秒後再試",
        )


class InternalError(AppException):
    """內部錯誤"""

    def __init__(self, message: str = "內部服務錯誤"):
        super().__init__(
            status_code=500,
            error="INTERNAL_ERROR",
            message=message,
        )


# =============================================
# 異常處理器
# =============================================

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    處理應用程式自定義異常

    返回標準化的錯誤響應格式。
    """
    details = None
    if exc.details:
        details = [ErrorDetail(**d) for d in exc.details]

    response = StandardErrorResponse(
        error=exc.error,
        message=exc.message,
        details=details,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(exclude_none=True),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    處理標準 HTTPException

    將 FastAPI 標準 HTTPException 轉換為標準化格式。
    """
    # 根據狀態碼映射錯誤類型
    error_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT",
    }

    error = error_map.get(exc.status_code, "ERROR")
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)

    response = StandardErrorResponse(
        error=error,
        message=message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(exclude_none=True),
    )


async def validation_exception_handler(request: Request, exc: Any) -> JSONResponse:
    """
    處理 Pydantic 驗證錯誤

    將 RequestValidationError 轉換為標準化格式。
    """
    from fastapi.exceptions import RequestValidationError

    if isinstance(exc, RequestValidationError):
        details = []
        for error in exc.errors():
            loc = error.get("loc", [])
            field = ".".join(str(l) for l in loc[1:]) if len(loc) > 1 else str(loc[0]) if loc else "unknown"
            details.append(ErrorDetail(
                field=field,
                message=error.get("msg", "驗證錯誤"),
            ))

        response = StandardErrorResponse(
            error="VALIDATION_ERROR",
            message="請求數據驗證失敗",
            details=details,
        )

        return JSONResponse(
            status_code=422,
            content=response.model_dump(exclude_none=True),
        )

    # Fallback
    return JSONResponse(
        status_code=500,
        content=StandardErrorResponse(
            error="INTERNAL_ERROR",
            message="驗證處理錯誤",
        ).model_dump(exclude_none=True),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    處理未捕獲的異常

    記錄錯誤並返回通用錯誤響應。
    """
    logger.error(
        f"未處理的異常: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method},
    )

    response = StandardErrorResponse(
        error="INTERNAL_ERROR",
        message="服務器內部錯誤",
    )

    return JSONResponse(
        status_code=500,
        content=response.model_dump(exclude_none=True),
    )


def register_exception_handlers(app):
    """
    註冊所有異常處理器到 FastAPI 應用

    在 main.py 的 create_app() 中調用此函數。
    """
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
