# =============================================
# 導航工具 - 引導用戶使用系統功能
# =============================================

from typing import Any, Dict, Optional
from .base import BaseTool, ToolResult


class NavigationGuideTool(BaseTool):
    """
    導航引導工具

    當用戶想進行 CRUD 操作時，引導他們到正確的頁面
    """

    name = "navigation_guide"
    description = "引導用戶到正確的系統功能頁面進行操作"

    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "用戶想執行的操作類型",
                "enum": [
                    "add_competitor",
                    "add_product",
                    "manage_competitors",
                    "manage_products",
                    "view_alerts",
                    "manage_settings",
                    "view_orders",
                    "view_finance"
                ]
            },
            "context": {
                "type": "string",
                "description": "額外上下文信息（如：競爭對手名稱）"
            }
        },
        "required": ["action"]
    }

    # 導航指南映射
    NAVIGATION_GUIDES = {
        "add_competitor": {
            "title": "新增競爭對手",
            "path": "/competitors",
            "steps": [
                "1. 點擊左側選單的「競爭對手」",
                "2. 點擊頁面右上角的「新增對手」按鈕",
                "3. 輸入競爭對手名稱（如：百佳、惠康）",
                "4. 選擇要監控的產品類別",
                "5. 設定價格警報閾值（可選）",
                "6. 點擊「確認」完成新增"
            ],
            "tips": [
                "建議先搜索確認該對手是否已存在",
                "可以同時設定多個監控類別"
            ]
        },
        "add_product": {
            "title": "新增監控產品",
            "path": "/products",
            "steps": [
                "1. 點擊左側選單的「產品管理」",
                "2. 點擊「新增產品」按鈕",
                "3. 輸入產品名稱或 SKU",
                "4. 選擇產品類別",
                "5. 設定監控頻率和警報條件",
                "6. 點擊「儲存」完成新增"
            ],
            "tips": [
                "可以批量導入產品清單",
                "設定合理的價格警報閾值以避免過多通知"
            ]
        },
        "manage_competitors": {
            "title": "管理競爭對手",
            "path": "/competitors",
            "steps": [
                "1. 點擊左側選單的「競爭對手」",
                "2. 查看現有競爭對手列表",
                "3. 點擊對手名稱查看詳情",
                "4. 可進行編輯、刪除或查看分析報告"
            ],
            "tips": []
        },
        "manage_products": {
            "title": "管理產品",
            "path": "/products",
            "steps": [
                "1. 點擊左側選單的「產品管理」",
                "2. 使用搜索或篩選找到目標產品",
                "3. 點擊產品進行編輯或查看詳情"
            ],
            "tips": []
        },
        "view_alerts": {
            "title": "查看警報",
            "path": "/alerts",
            "steps": [
                "1. 點擊左側選單的「警報中心」",
                "2. 查看所有未讀警報",
                "3. 點擊警報查看詳情",
                "4. 可標記為已讀或設定跟進動作"
            ],
            "tips": [
                "可以設定警報推送到 Telegram"
            ]
        },
        "manage_settings": {
            "title": "系統設定",
            "path": "/settings",
            "steps": [
                "1. 點擊左側選單的「設定」",
                "2. 選擇要修改的設定類別",
                "3. 進行相應的設定調整"
            ],
            "tips": []
        },
        "view_orders": {
            "title": "查看訂單",
            "path": "/orders",
            "steps": [
                "1. 點擊左側選單的「訂單管理」",
                "2. 使用篩選器選擇訂單狀態",
                "3. 點擊訂單號查看詳情"
            ],
            "tips": []
        },
        "view_finance": {
            "title": "查看財務",
            "path": "/finance",
            "steps": [
                "1. 點擊左側選單的「財務報表」",
                "2. 選擇時間範圍",
                "3. 查看營收、利潤等數據"
            ],
            "tips": []
        }
    }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """執行導航引導"""
        action = parameters.get("action", "")
        context = parameters.get("context", "")

        guide = self.NAVIGATION_GUIDES.get(action)

        if not guide:
            return ToolResult(
                success=False,
                data=None,
                error=f"未知的操作類型: {action}"
            )

        # 構建回應
        response_parts = [
            f"## {guide['title']}",
            "",
            f"**路徑**: {guide['path']}",
            "",
            "**操作步驟**:",
        ]

        for step in guide["steps"]:
            response_parts.append(step)

        if guide.get("tips"):
            response_parts.append("")
            response_parts.append("**小提示**:")
            for tip in guide["tips"]:
                response_parts.append(f"- {tip}")

        if context:
            response_parts.append("")
            response_parts.append(f"**備註**: 您提到了「{context}」，可以在操作時使用這個資訊。")

        return ToolResult(
            success=True,
            data={
                "title": guide["title"],
                "path": guide["path"],
                "steps": guide["steps"],
                "tips": guide.get("tips", []),
                "formatted_guide": "\n".join(response_parts)
            },
            error=None
        )


class AddCompetitorGuideTool(BaseTool):
    """
    新增競爭對手引導工具

    當用戶想新增競爭對手時，提供詳細引導
    """

    name = "add_competitor_guide"
    description = "引導用戶如何新增競爭對手到監控系統"

    parameters = {
        "type": "object",
        "properties": {
            "competitor_name": {
                "type": "string",
                "description": "競爭對手名稱（如有提及）"
            }
        },
        "required": []
    }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """執行新增競爭對手引導"""
        competitor_name = parameters.get("competitor_name", "")

        guide_text = """## 如何新增競爭對手

目前系統暫時未支援通過 AI 助手直接新增競爭對手，請按以下步驟在網頁介面操作：

**操作步驟**:
1. 點擊左側選單的「競爭對手」
2. 點擊頁面右上角的「+ 新增對手」按鈕
3. 在彈出的表單中填寫：
   - 競爭對手名稱
   - 監控的產品類別
   - 價格變動警報閾值
4. 點擊「確認」完成新增

**小提示**:
- 新增後系統會自動開始監控該對手的價格
- 可以隨時在競爭對手列表中編輯或刪除"""

        if competitor_name:
            guide_text += f"\n\n**備註**: 您提到想監控「{competitor_name}」，請在新增時填入這個名稱。"

        return ToolResult(
            success=True,
            data={
                "guide": guide_text,
                "action": "add_competitor",
                "path": "/competitors",
                "competitor_name": competitor_name
            },
            error=None
        )


class AddProductGuideTool(BaseTool):
    """
    新增產品引導工具
    """

    name = "add_product_guide"
    description = "引導用戶如何新增產品到監控系統"

    parameters = {
        "type": "object",
        "properties": {
            "product_name": {
                "type": "string",
                "description": "產品名稱（如有提及）"
            }
        },
        "required": []
    }

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """執行新增產品引導"""
        product_name = parameters.get("product_name", "")

        guide_text = """## 如何新增監控產品

目前系統暫時未支援通過 AI 助手直接新增產品，請按以下步驟在網頁介面操作：

**操作步驟**:
1. 點擊左側選單的「產品管理」
2. 點擊「+ 新增產品」按鈕
3. 在表單中填寫：
   - 產品名稱或 SKU
   - 選擇產品類別
   - 設定監控頻率
   - 設定價格警報條件（可選）
4. 點擊「儲存」完成新增

**小提示**:
- 支援批量導入產品清單（CSV 格式）
- 可以從 HKTVmall 直接導入現有產品"""

        if product_name:
            guide_text += f"\n\n**備註**: 您提到想新增「{product_name}」，請在新增時填入這個名稱。"

        return ToolResult(
            success=True,
            data={
                "guide": guide_text,
                "action": "add_product",
                "path": "/products",
                "product_name": product_name
            },
            error=None
        )
