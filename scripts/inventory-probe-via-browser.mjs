#!/usr/bin/env node
/**
 * HKTVmall Inventory Probe — Via OpenClaw Browser
 *
 * 使用 OpenClaw 嘅 browser tool（已登入 HKTVmall session）做庫存探測。
 * 喺 browser page context 入面執行 fetch，完全繞過 httpOnly cookie 問題。
 *
 * 工作原理：
 *   1. 接收 SKU 列表
 *   2. 生成一個 probe script（injected JS）
 *   3. 由 OpenClaw 喺 HKTVmall 已登入頁面執行
 *   4. 返回 stockLevel 數組
 *   5. 存入 GoGoJap inventory_probes DB table
 *
 * 用法（由 Eve 透過 browser tool 執行）：
 *   1. Eve 用 browser(action=act, kind=evaluate) 喺 hktvmall.com 入面 call probeFn
 *   2. 結果 JSON 傳返俾 Node script 存 DB
 *
 * 直接 JS 函數（貼入 browser evaluate）：
 *   見下方 buildBrowserProbeScript()
 */

import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DB_PATH = join(__dirname, '..', 'data', 'inventory.json');

// ─── Browser-side probe function ──────────────────────────────────────
// This function runs INSIDE the browser page context (HKTVmall)

export function buildBrowserProbeScript(skus, options = {}) {
  const { delayMs = 1500 } = options;

  return `
(async () => {
  const skus = ${JSON.stringify(skus)};
  const delayMs = ${delayMs};
  const CHECKOUT = '/zh/hktvfrontend/v1/cart/express/checkout';
  const REMOVE   = '/zh/hktvfrontend/v1/cart/express/remove_item_from_cart';
  const ADD      = '/hktv/zh/cart/add';

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const results = [];

  // Get CSRF once
  let csrf = null;
  const pageHtml = await fetch('/hktv/zh/main', { credentials: 'include' }).then(r => r.text());
  const m = pageHtml.match(/CSRFToken[^0-9a-f]*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/i);
  csrf = m?.[1];
  if (!csrf) return { error: 'CSRF not found' };

  for (const sku of skus) {
    const ts = new Date().toISOString();
    try {
      // Add 1 to cart
      await fetch(ADD, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'productCodePost=' + encodeURIComponent(sku) + '&qty=1&CSRFToken=' + encodeURIComponent(csrf),
        credentials: 'include',
      });

      await sleep(500);

      // Read checkout JSON for stockLevel
      const j = await fetch(CHECKOUT, { credentials: 'include' }).then(r => r.json());
      const str = JSON.stringify(j);
      const idx = str.indexOf(sku);

      let stock = null, stockStatus = null, inStock = null;
      if (idx !== -1) {
        const ctx = str.substring(idx, idx + 800);
        const sl = ctx.match(/"stockLevel"\\s*:\\s*(\\d+)/);
        const ss = ctx.match(/"stockLevelStatus"[^}]*?"code"\\s*:\\s*"([^"]+)"/);
        stock = sl ? parseInt(sl[1]) : null;
        stockStatus = ss?.[1] || null;
        inStock = stockStatus === 'inStock';
      }

      // Remove from cart
      await fetch(REMOVE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sku }),
        credentials: 'include',
      });

      results.push({ sku, stock, inStock, stockStatus, timestamp: ts });
    } catch (e) {
      results.push({ sku, stock: null, error: e.message, timestamp: ts });
    }

    await sleep(delayMs);
  }

  return results;
})();
  `.trim();
}

// ─── CLI: print the probe script for Eve to copy ─────────────────────

const isMain = process.argv[1] &&
  fileURLToPath(import.meta.url).replace(/\\/g, '/') === process.argv[1].replace(/\\/g, '/');

if (isMain) {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node inventory-probe-via-browser.mjs <sku1> [sku2] ...');
    console.error('Output: JS script to run in browser evaluate');
    process.exit(1);
  }

  const skus = args.filter(a => !a.startsWith('--'));
  const script = buildBrowserProbeScript(skus);

  // Output the script to stdout — paste into browser tool evaluate
  console.log(script);
  console.error('\n✅ Script generated. Paste into browser tool evaluate on hktvmall.com\n');
}
