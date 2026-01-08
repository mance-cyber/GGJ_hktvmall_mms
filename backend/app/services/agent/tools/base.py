# =============================================
# 工具基類
# =============================================

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class ToolResult:
    """工具執行結果"""
    tool_name: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
        }


class BaseTool(ABC):
    """
    工具基類
    
    所有 Agent 工具都繼承此類，實現 execute 方法
    """
    
    # 工具名稱（唯一標識符）
    name: str = "base_tool"
    
    # 工具描述（用於 AI 選擇工具）
    description: str = "Base tool"
    
    # 參數定義
    parameters: Dict[str, Dict[str, Any]] = {}
    
    # 是否需要數據庫連接
    requires_db: bool = True
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        執行工具
        
        Args:
            **kwargs: 工具參數
        
        Returns:
            ToolResult: 執行結果
        """
        pass
    
    def validate_parameters(self, **kwargs) -> List[str]:
        """
        驗證參數
        
        Returns:
            錯誤列表（空列表表示驗證通過）
        """
        errors = []
        
        for param_name, param_def in self.parameters.items():
            if param_def.get("required", False) and param_name not in kwargs:
                errors.append(f"缺少必填參數: {param_name}")
            
            if param_name in kwargs:
                value = kwargs[param_name]
                expected_type = param_def.get("type")
                
                if expected_type == "list" and not isinstance(value, list):
                    errors.append(f"參數 {param_name} 應為列表")
                elif expected_type == "str" and not isinstance(value, str):
                    errors.append(f"參數 {param_name} 應為字符串")
                elif expected_type == "int" and not isinstance(value, int):
                    errors.append(f"參數 {param_name} 應為整數")
        
        return errors
    
    async def safe_execute(self, **kwargs) -> ToolResult:
        """
        安全執行（帶錯誤處理和計時）
        """
        start_time = datetime.now()
        
        # 驗證參數
        errors = self.validate_parameters(**kwargs)
        if errors:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error="; ".join(errors)
            )
        
        try:
            result = await self.execute(**kwargs)
            result.execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            return result
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                error=str(e),
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """
        獲取工具 Schema（用於 AI Function Calling）
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    name: {
                        "type": def_.get("type", "string"),
                        "description": def_.get("description", ""),
                    }
                    for name, def_ in self.parameters.items()
                },
                "required": [
                    name for name, def_ in self.parameters.items()
                    if def_.get("required", False)
                ]
            }
        }
