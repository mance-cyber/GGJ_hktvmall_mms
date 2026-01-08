import os

file_path = 'backend/app/services/agent/report_generator.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Insert new logic in generate method
insert_marker = '# 處理價格趨勢'
new_logic = """
        # 處理銷售數據 (Finance)
        if "query_sales" in tool_results:
            sales_section = self._generate_sales_section(
                tool_results["query_sales"]
            )
            sections.append(sales_section)

        # 處理熱門產品 (Finance/Sales)
        if "query_top_products" in tool_results:
            top_section, top_chart = self._generate_finance_top_products(
                tool_results["query_top_products"]
            )
            sections.append(top_section)
            if top_chart:
                charts.append(top_chart)

"""

if insert_marker in content:
    # Insert before the marker
    parts = content.split(insert_marker)
    new_content = parts[0] + new_logic + insert_marker + parts[1]
else:
    print("Marker not found!")
    exit(1)

# 2. Append new methods
new_methods = """
    def _generate_sales_section(self, data: Dict[str, Any]) -> str:
        if not data.get("success", False):
            return "## 💰 銷售數據\n\n⚠️ 無法獲取數據\n"
        
        result = data.get("data", {})
        val = result.get("value", 0)
        currency = result.get("currency", "HKD")
        metric = result.get("metric", "revenue")
        period = result.get("period", "")
        
        metric_name = "總營收" if metric == "revenue" else "淨利潤"
        
        return f"## 💰 {metric_name} ({period})\n\n# {currency} ${val:,.2f}\n"

    def _generate_finance_top_products(self, data: Dict[str, Any]) -> tuple:
        if not data.get("success", False):
            return "## 🏆 銷售排行\n\n⚠️ 無法獲取數據\n", None
            
        result = data.get("data", {})
        items = result.get("items", [])
        title = result.get("title", "Top Products")
        
        if not items:
            return "## 🏆 銷售排行\n\n暫無數據\n", None
            
        lines = [f"## 🏆 {title}\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. **{item['name']}**: {item['value']}")
            
        chart = ChartData(
            type="bar",
            title=title,
            data=items,
            config={
                "xKey": "name",
                "yKeys": [{"key": "value", "color": "#8884d8", "name": "數值"}]
            }
        )
        return "\n".join(lines), chart
"""

final_content = new_content + new_methods

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Successfully patched report_generator.py")
