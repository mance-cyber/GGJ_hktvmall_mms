# =============================================
# AI Product Filter — Competitor v2
# 用 Claude Sonnet 判斷商品是否為生鮮/冷凍食材
# =============================================

import json
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# OpenClaw Gateway 本地端口
OPENCLAW_GATEWAY_URL = os.environ.get(
    "OPENCLAW_GATEWAY_URL",
    "http://localhost:18789/v1/chat/completions"
)
OPENCLAW_MODEL = "anthropic/claude-sonnet-4-5"

CLASSIFY_PROMPT_TEMPLATE = """你是 HKTVmall 生鮮食材分類專家。

判斷以下商品是否為「生鮮或冷凍食材」：
✅ 包括：生肉、冷凍肉、海鮮、冷凍海鮮、刺身、急凍魚生
❌ 排除：薯片、零食、便當、湯底、醬汁、調味料、即食品、飲品、日用品、加工食品（魚丸、蝦丸、腸仔）、罐頭、寵物食品

對每件商品只返回 JSON array（不要其他文字、不要 markdown）：
[
  {{
    "sku": "商品SKU",
    "relevant": true,
    "category": "牛",
    "product_type": "fresh",
    "unit_weight_g": 200,
    "reason": null
  }}
]

欄位說明：
- relevant: true=生鮮/冷凍食材, false=排除
- category: 牛/豬/魚/蝦/蟹/貝/蠔/雞/其他（只有 relevant=true 時填）
- product_type: fresh=生鮮, frozen=冷凍（只有 relevant=true 時填）
- unit_weight_g: 從商品名提取重量（克），無法提取則填 null
- reason: 排除原因（只有 relevant=false 時填，其他填 null）

商品列表：
{products_json}"""


class AIProductFilter:
    """
    使用 Claude Sonnet（via OpenClaw Gateway）分類商品是否為生鮮食材。
    
    批次處理：每次最多 50 件，避免超出 context。
    """

    BATCH_SIZE = 50

    def __init__(
        self,
        gateway_url: str = OPENCLAW_GATEWAY_URL,
        model: str = OPENCLAW_MODEL,
        timeout: float = 120.0,
    ):
        self.gateway_url = gateway_url
        self.model = model
        self.timeout = timeout

    async def classify_products(
        self,
        products: list[dict],
    ) -> list[dict]:
        """
        批次分類商品。
        
        Args:
            products: 商品列表，每項需含 name, sku（category, image_url 可選）
            
        Returns:
            分類結果列表，每項含：
            {sku, relevant, category, product_type, unit_weight_g, reason}
        """
        if not products:
            return []

        results = []
        for i in range(0, len(products), self.BATCH_SIZE):
            batch = products[i:i + self.BATCH_SIZE]
            batch_results = await self._classify_batch(batch)
            results.extend(batch_results)
            logger.info(
                f"AI filter batch {i // self.BATCH_SIZE + 1}: "
                f"{len(batch)} 商品 → "
                f"{sum(1 for r in batch_results if r.get('relevant'))} 件相關"
            )

        return results

    async def _classify_batch(self, products: list[dict]) -> list[dict]:
        """分類單個批次（最多 50 件）"""
        # 只傳 AI 需要的字段
        slim = [
            {"sku": p.get("sku", ""), "name": p.get("name", p.get("nameZh", ""))}
            for p in products
        ]
        products_json = json.dumps(slim, ensure_ascii=False, indent=2)
        prompt = CLASSIFY_PROMPT_TEMPLATE.format(products_json=products_json)

        try:
            raw = await self._call_gateway(prompt)
            return self._parse_response(raw, products)
        except Exception as e:
            logger.error(f"AI filter batch failed (attempt 1): {e}")
            # Retry once
            try:
                import asyncio
                await asyncio.sleep(2)
                raw = await self._call_gateway(prompt)
                return self._parse_response(raw, products)
            except Exception as e2:
                logger.error(f"AI filter batch failed (attempt 2): {e2}")
            # Fallback: mark all as unknown (relevant=False to be safe)
            return [
                {
                    "sku": p.get("sku", ""),
                    "relevant": False,
                    "category": None,
                    "product_type": None,
                    "unit_weight_g": None,
                    "reason": f"AI filter error: {e}",
                }
                for p in products
            ]

    async def _call_gateway(self, prompt: str) -> str:
        """調用 OpenClaw Gateway"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                self.gateway_url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
                headers={"Authorization": f"Bearer {os.environ.get('OPENCLAW_GATEWAY_TOKEN', '329f0d69593409c4cc6cf4c420a34d5d2b734af71ed71d35')}"},
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    def _parse_response(self, raw: str, original: list[dict]) -> list[dict]:
        """解析 AI 回應，容錯處理"""
        try:
            # 移除可能的 markdown 代碼塊
            text = raw.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
            
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            logger.warning(f"AI 回應 JSON 解析失敗，嘗試提取 JSON array...")
            try:
                start = raw.index("[")
                end = raw.rindex("]") + 1
                parsed = json.loads(raw[start:end])
                if isinstance(parsed, list):
                    return parsed
            except (ValueError, json.JSONDecodeError):
                pass

        logger.error(f"無法解析 AI 回應，raw={raw[:200]}")
        # 全部 fallback
        return [
            {
                "sku": p.get("sku", ""),
                "relevant": False,
                "category": None,
                "product_type": None,
                "unit_weight_g": None,
                "reason": "AI response parse error",
            }
            for p in original
        ]


# 全局單例
_filter: Optional[AIProductFilter] = None


def get_ai_filter() -> AIProductFilter:
    global _filter
    if _filter is None:
        _filter = AIProductFilter()
    return _filter
