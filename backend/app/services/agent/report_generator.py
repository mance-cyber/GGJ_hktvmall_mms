# =============================================
# 報告生成器
# 將工具執行結果轉換為結構化報告
# =============================================

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ChartData:
    """圖表數據"""
    type: str  # line, bar, pie
    title: str
    data: List[Dict[str, Any]]
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TableData:
    """表格數據"""
    title: str
    headers: List[str]
    rows: List[List[Any]]


@dataclass
class Report:
    """報告"""
    title: str
    markdown: str
    charts: List[ChartData] = field(default_factory=list)
    tables: List[TableData] = field(default_factory=list)
    summary: str = ""
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "markdown": self.markdown,
            "charts": [
                {
                    "type": c.type,
                    "title": c.title,
                    "data": c.data,
                    "config": c.config
                }
                for c in self.charts
            ],
            "tables": [
                {
                    "title": t.title,
                    "headers": t.headers,
                    "rows": t.rows
                }
                for t in self.tables
            ],
            "summary": self.summary,
            "generated_at": self.generated_at.isoformat()
        }


class ReportGenerator:
    """
    報告生成器
    
    將工具執行結果轉換為 Markdown 報告和圖表數據
    """
    
    def __init__(self, ai_service=None):
        """
        初始化報告生成器
        
        Args:
            ai_service: AI 服務（可選，用於生成摘要和建議）
        """
        self.ai_service = ai_service
    
    async def generate(
        self,
        products: List[str],
        tool_results: Dict[str, Any],
        include_ai_insights: bool = True
    ) -> Report:
        """
        生成報告
        
        Args:
            products: 產品列表
            tool_results: 工具執行結果
            include_ai_insights: 是否包含 AI 洞察
        
        Returns:
            報告對象
        """
        title = f"{', '.join(products)} 市場分析報告"
        
        sections = []
        charts = []
        tables = []
        
        # 生成標題
        sections.append(f"# {title}")
        sections.append(f"> 分析日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        sections.append("---\n")
        
        # 處理產品概覽
        if "product_overview" in tool_results:
            overview_section, overview_table = self._generate_overview_section(
                tool_results["product_overview"]
            )
            sections.append(overview_section)
            if overview_table:
                tables.append(overview_table)
        
        
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

# 處理價格趨勢
        if "price_trend" in tool_results:
            trend_section, trend_chart = self._generate_trend_section(
                tool_results["price_trend"]
            )
            sections.append(trend_section)
            if trend_chart:
                charts.append(trend_chart)
        
        # 處理熱門產品
        if "top_products" in tool_results:
            top_section, top_tables = self._generate_top_products_section(
                tool_results["top_products"]
            )
            sections.append(top_section)
            tables.extend(top_tables)
        
        # 處理競爭對手比較
        if "competitor_compare" in tool_results:
            comp_section, comp_chart = self._generate_competitor_section(
                tool_results["competitor_compare"]
            )
            sections.append(comp_section)
            if comp_chart:
                charts.append(comp_chart)
        
        # 生成 AI 洞察和建議
        if include_ai_insights and self.ai_service:
            insights_section = await self._generate_ai_insights(
                products, tool_results
            )
            sections.append(insights_section)
        
        markdown = "\n".join(sections)
        
        return Report(
            title=title,
            markdown=markdown,
            charts=charts,
            tables=tables,
            summary=self._generate_summary(tool_results)
        )
    
    def _generate_overview_section(
        self,
        data: Dict[str, Any]
    ) -> tuple:
        """生成產品概覽部分"""
        if not data.get("success", False):
            return "## 📊 產品概覽\n\n⚠️ 無法獲取數據\n", None
        
        results = data.get("data", {}).get("results", [])
        if not results:
            return "## 📊 產品概覽\n\n暫無數據\n", None
        
        lines = ["## 📊 產品概覽\n"]
        
        # 生成表格
        lines.append("| 產品類型 | SKU 數量 | 平均價格 | 價格範圍 | 平均評分 | 總評論 |")
        lines.append("|----------|----------|----------|----------|----------|--------|")
        
        table_rows = []
        for item in results:
            product_type = item.get("product_type", "未知")
            sku_count = item.get("sku_count", 0)
            avg_price = item.get("avg_price", 0)
            min_price = item.get("min_price", 0)
            max_price = item.get("max_price", 0)
            avg_rating = item.get("avg_rating", 0)
            total_reviews = item.get("total_reviews", 0)
            in_stock = item.get("in_stock_count", 0)
            on_sale = item.get("on_sale_count", 0)
            
            price_range = f"${min_price:,.0f} - ${max_price:,.0f}"
            rating_str = f"⭐ {avg_rating:.1f}" if avg_rating else "N/A"
            
            lines.append(
                f"| {product_type} | {sku_count} | ${avg_price:,.0f} | "
                f"{price_range} | {rating_str} | {total_reviews:,} |"
            )
            
            table_rows.append([
                product_type, sku_count, f"${avg_price:,.0f}",
                price_range, rating_str, total_reviews
            ])
        
        lines.append("")
        
        # 添加庫存信息
        for item in results:
            product_type = item.get("product_type", "")
            in_stock = item.get("in_stock_count", 0)
            sku_count = item.get("sku_count", 0)
            on_sale = item.get("on_sale_count", 0)
            
            stock_pct = (in_stock / sku_count * 100) if sku_count > 0 else 0
            lines.append(f"- **{product_type}**：{stock_pct:.0f}% 有貨，{on_sale} 款促銷中")
        
        lines.append("\n")
        
        table = TableData(
            title="產品概覽",
            headers=["產品類型", "SKU 數量", "平均價格", "價格範圍", "平均評分", "總評論"],
            rows=table_rows
        )
        
        return "\n".join(lines), table
    
    def _generate_trend_section(
        self,
        data: Dict[str, Any]
    ) -> tuple:
        """生成價格趨勢部分"""
        if not data.get("success", False):
            return "## 📈 價格趨勢\n\n⚠️ 無法獲取數據\n", None
        
        results = data.get("data", {}).get("results", {})
        if not results:
            return "## 📈 價格趨勢\n\n暫無趨勢數據\n", None
        
        lines = ["## 📈 價格趨勢\n"]
        
        chart_data = []
        
        for product_type, trend_info in results.items():
            if isinstance(trend_info, dict):
                change_pct = trend_info.get("change_pct", 0)
                trend = trend_info.get("trend", "stable")
                trend_data = trend_info.get("data", [])
            else:
                continue
            
            # 趨勢圖標
            if trend == "up":
                icon = "📈"
                change_str = f"+{change_pct:.1f}%"
            elif trend == "down":
                icon = "📉"
                change_str = f"{change_pct:.1f}%"
            else:
                icon = "➡️"
                change_str = "持平"
            
            lines.append(f"### {product_type} {icon}")
            lines.append(f"- 價格變化：**{change_str}**")
            
            if trend_data:
                first_price = trend_data[0].get("avg_price", 0)
                last_price = trend_data[-1].get("avg_price", 0)
                lines.append(f"- 期初平均價：${first_price:,.0f}")
                lines.append(f"- 期末平均價：${last_price:,.0f}")
                
                # 添加圖表數據
                for point in trend_data:
                    chart_data.append({
                        "period": point.get("period", "")[:10],
                        "product": product_type,
                        "price": point.get("avg_price", 0)
                    })
            
            lines.append("")
        
        chart = ChartData(
            type="line",
            title="價格趨勢",
            data=chart_data,
            config={
                "xKey": "period",
                "yKeys": [
                    {"key": "price", "color": "#8884d8", "name": "平均價格"}
                ]
            }
        ) if chart_data else None
        
        return "\n".join(lines), chart
    
    def _generate_top_products_section(
        self,
        data: Dict[str, Any]
    ) -> tuple:
        """生成熱門產品部分"""
        if not data.get("success", False):
            return "## 🏆 熱門產品\n\n⚠️ 無法獲取數據\n", []
        
        results = data.get("data", {}).get("results", {})
        if not results:
            return "## 🏆 熱門產品\n\n暫無數據\n", []
        
        lines = ["## 🏆 熱門產品\n"]
        tables = []
        
        for product_type, products in results.items():
            lines.append(f"### {product_type} TOP 5\n")
            lines.append("| 排名 | 產品 | 價格 | 折扣 | 評分 | 評論 |")
            lines.append("|------|------|------|------|------|------|")
            
            table_rows = []
            for i, product in enumerate(products[:5], 1):
                name = product.get("name", "")[:30]
                price = product.get("price", 0)
                discount = product.get("discount_percent")
                rating = product.get("rating", 0)
                reviews = product.get("review_count", 0)
                
                rank_icon = ["🥇", "🥈", "🥉", "4", "5"][i-1]
                discount_str = f"-{discount:.0f}%" if discount else "-"
                rating_str = f"⭐{rating:.1f}" if rating else "N/A"
                
                lines.append(
                    f"| {rank_icon} | {name} | ${price:,.0f} | "
                    f"{discount_str} | {rating_str} | {reviews:,} |"
                )
                
                table_rows.append([rank_icon, name, f"${price:,.0f}", discount_str, rating_str, reviews])
            
            lines.append("")
            
            tables.append(TableData(
                title=f"{product_type} 熱門產品",
                headers=["排名", "產品", "價格", "折扣", "評分", "評論"],
                rows=table_rows
            ))
        
        return "\n".join(lines), tables
    
    def _generate_competitor_section(
        self,
        data: Dict[str, Any]
    ) -> tuple:
        """生成競爭對手比較部分"""
        if not data.get("success", False):
            return "## ⚔️ 競爭對手比較\n\n⚠️ 無法獲取數據\n", None
        
        result_data = data.get("data", {})
        our_data = result_data.get("our_data", [])
        competitor_data = result_data.get("competitor_data", [])
        comparison = result_data.get("comparison", {})
        
        if not our_data and not competitor_data:
            return "## ⚔️ 競爭對手比較\n\n暫無競爭對手數據\n", None
        
        lines = ["## ⚔️ 競爭對手比較\n"]
        
        # 按產品類型整理
        all_products = set()
        for item in our_data:
            all_products.add(item.get("product_type"))
        for item in competitor_data:
            all_products.add(item.get("product_type"))
        
        chart_data = []
        
        for product_type in all_products:
            if product_type == "其他":
                continue
            
            lines.append(f"### {product_type}\n")
            lines.append("| 平台 | SKU | 平均價 | vs HKTVmall |")
            lines.append("|------|-----|--------|-------------|")
            
            # 找 HKTVmall 數據
            our_price = 0
            for item in our_data:
                if item.get("product_type") == product_type:
                    our_price = item.get("avg_price", 0)
                    lines.append(f"| **HKTVmall** | {item.get('sku_count', 0)} | ${our_price:,.0f} | 基準 |")
                    chart_data.append({
                        "platform": "HKTVmall",
                        "product": product_type,
                        "price": our_price
                    })
                    break
            
            # 競爭對手數據
            for item in competitor_data:
                if item.get("product_type") == product_type:
                    platform = item.get("platform", "")
                    their_price = item.get("avg_price", 0)
                    sku_count = item.get("sku_count", 0)
                    
                    if our_price and their_price:
                        diff = their_price - our_price
                        diff_pct = (diff / our_price) * 100
                        if diff > 0:
                            comparison_str = f"貴 {diff_pct:.1f}%"
                        elif diff < 0:
                            comparison_str = f"平 {abs(diff_pct):.1f}%"
                        else:
                            comparison_str = "相同"
                    else:
                        comparison_str = "-"
                    
                    lines.append(f"| {platform} | {sku_count} | ${their_price:,.0f} | {comparison_str} |")
                    chart_data.append({
                        "platform": platform,
                        "product": product_type,
                        "price": their_price
                    })
            
            lines.append("")
        
        # 結論
        lines.append("### 💡 結論\n")
        we_are_cheaper = 0
        total_comparisons = 0
        
        for platform, products in comparison.items():
            for product, comp_data in products.items():
                total_comparisons += 1
                if comp_data.get("we_are_cheaper"):
                    we_are_cheaper += 1
        
        if total_comparisons > 0:
            cheaper_pct = (we_are_cheaper / total_comparisons) * 100
            if cheaper_pct > 60:
                lines.append(f"✅ HKTVmall 在 {cheaper_pct:.0f}% 的比較中價格更優\n")
            elif cheaper_pct > 40:
                lines.append(f"⚠️ HKTVmall 價格競爭力一般，約 {cheaper_pct:.0f}% 較便宜\n")
            else:
                lines.append(f"❌ HKTVmall 只有 {cheaper_pct:.0f}% 的情況較便宜，需關注定價\n")
        
        chart = ChartData(
            type="bar",
            title="平台價格比較",
            data=chart_data,
            config={
                "xKey": "platform",
                "yKeys": [
                    {"key": "price", "color": "#82ca9d", "name": "平均價格"}
                ]
            }
        ) if chart_data else None
        
        return "\n".join(lines), chart
    
    async def _generate_ai_insights(
        self,
        products: List[str],
        tool_results: Dict[str, Any]
    ) -> str:
        """使用 AI 生成洞察和建議"""
        if not self.ai_service:
            return ""
        
        # 準備數據摘要
        data_summary = json.dumps(tool_results, ensure_ascii=False, default=str)[:3000]
        
        prompt = f"""基於以下市場數據，為 {', '.join(products)} 生成：
1. 3 個關鍵發現
2. 3 個 Marketing 策略建議

數據：
{data_summary}

請用繁體中文回答，格式如下：

## 🎯 關鍵發現

1. **發現一標題**：說明
2. **發現二標題**：說明
3. **發現三標題**：說明

## 💡 Marketing 策略建議

1. **策略一標題**：具體行動
2. **策略二標題**：具體行動
3. **策略三標題**：具體行動
"""
        
        try:
            response = await self.ai_service.call_ai(prompt)
            return "\n---\n\n" + response.content
        except Exception as e:
            return f"\n---\n\n## 🎯 AI 洞察\n\n⚠️ 無法生成 AI 洞察: {str(e)}\n"
    
    def _generate_summary(self, tool_results: Dict[str, Any]) -> str:
        """生成摘要"""
        summary_parts = []
        
        if "product_overview" in tool_results:
            overview = tool_results["product_overview"].get("data", {}).get("results", [])
            total_skus = sum(item.get("sku_count", 0) for item in overview)
            summary_parts.append(f"共分析 {total_skus} 款產品")
        
        if "competitor_compare" in tool_results:
            summary_parts.append("包含競爭對手比較")
        
        if "price_trend" in tool_results:
            summary_parts.append("包含價格趨勢分析")
        
        return "；".join(summary_parts) if summary_parts else "市場分析報告"

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
