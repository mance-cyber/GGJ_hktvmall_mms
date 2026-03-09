#!/usr/bin/env node
/**
 * HKTVmall Inventory Probe v3
 *
 * Uses CDP (Chrome DevTools Protocol) to run fetch() inside an authenticated
 * browser session, bypassing WAF/bot detection.
 *
 * Requires: OpenClaw browser with an HKTVmall tab open and logged in.
 *
 * Flow:
 *   1. Connect to browser via CDP WebSocket
 *   2. Inject JS: add items to cart → read checkout API stockLevel → cleanup
 *   3. Return results as JSON
 *
 * Usage:
 *   node inventory-probe.mjs H0888001_S_10161559
 *   node inventory-probe.mjs H0888001_S_10161559 H0888001_S_10161560
 *   node inventory-probe.mjs --file skus.txt
 *   node inventory-probe.mjs --cdp-port 18792         # custom CDP port
 *   node inventory-probe.mjs --target-id <pageId>      # specific tab
 *
 * Module:
 *   import { probeInventory } from './inventory-probe.mjs'
 */

import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
import WebSocket from 'ws';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_CDP_PORT = 18792;
const HKTVMALL_ORIGIN = 'https://www.hktvmall.com';

const log = (...a) => console.error(...a);

// ─── CDP Client ──────────────────────────────────────────────────────

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.id = 0;
    this.pending = new Map();
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.on('open', resolve);
      this.ws.on('error', reject);
      this.ws.on('message', (data) => {
        const msg = JSON.parse(data);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message));
          else resolve(msg.result);
        }
      });
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this.id;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
      setTimeout(() => {
        if (this.pending.has(id)) {
          this.pending.delete(id);
          reject(new Error(`CDP timeout: ${method}`));
        }
      }, 30000);
    });
  }

  /** Run JS in page context and return the result */
  async evaluate(expression) {
    const result = await this.send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (result.exceptionDetails) {
      throw new Error(`JS Error: ${result.exceptionDetails.text || JSON.stringify(result.exceptionDetails)}`);
    }
    return result.result?.value;
  }

  close() {
    this.ws?.close();
  }
}

// ─── Browser Discovery ──────────────────────────────────────────────

/**
 * Find an HKTVmall tab in the browser, or any tab we can use.
 */
async function findTarget(cdpPort, preferredTargetId) {
  const listUrl = `http://127.0.0.1:${cdpPort}/json`;
  const res = await fetch(listUrl);
  const tabs = await res.json();

  if (preferredTargetId) {
    const tab = tabs.find(t => t.id === preferredTargetId);
    if (tab) return tab;
    log(`  ⚠ Target ${preferredTargetId} not found, searching...`);
  }

  // Prefer HKTVmall tab
  const hktvTab = tabs.find(t =>
    t.type === 'page' &&
    t.url?.includes('hktvmall.com') &&
    t.webSocketDebuggerUrl
  );
  if (hktvTab) return hktvTab;

  // Any page tab
  const anyTab = tabs.find(t => t.type === 'page' && t.webSocketDebuggerUrl);
  return anyTab || null;
}

// ─── Probe Script Builder ────────────────────────────────────────────

/**
 * Build the JS code that runs inside the browser page.
 * Does: get CSRF → add SKUs → read checkout → cleanup → return results
 */
function buildProbeScript(skus) {
  return `
(async () => {
  const skus = ${JSON.stringify(skus)};
  const delay = ms => new Promise(r => setTimeout(r, ms));
  const results = [];

  // 1. Get CSRF token
  const mainRes = await fetch('/hktv/zh/main', { credentials: 'include' });
  const mainHtml = await mainRes.text();
  const csrfMatch = mainHtml.match(/CSRFToken[^0-9a-f]*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/i);
  if (!csrfMatch) return JSON.stringify({ error: 'CSRF not found — not logged in?' });
  const csrf = csrfMatch[1];

  // 2. Add all SKUs to cart
  const addResults = {};
  for (const sku of skus) {
    await delay(400);
    try {
      const res = await fetch('/hktv/zh/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'productCodePost=' + encodeURIComponent(sku) + '&qty=1&CSRFToken=' + encodeURIComponent(csrf),
        credentials: 'include',
      });
      const text = await res.text();
      let json; try { json = JSON.parse(text.trim()); } catch {}
      addResults[sku] = json?.statusCode === 'success';
    } catch (e) {
      addResults[sku] = false;
    }
  }

  // 3. Read checkout API (one call gets all stock levels)
  await delay(500);
  const chkRes = await fetch('/zh/hktvfrontend/v1/cart/express/checkout', { credentials: 'include' });
  const chkJson = await chkRes.json();
  const data = chkJson.data || chkJson;
  const groups = data.deliveryGroups || [];

  // Extract stockLevel for each SKU
  const stockMap = {};
  for (const g of groups) {
    for (const e of (g.orderEntries || [])) {
      const p = e.product;
      if (!p?.code) continue;
      stockMap[p.code] = {
        stockLevel: p.stock?.stockLevel ?? null,
        stockStatus: p.stock?.stockLevelStatus?.code || null,
        name: p.name || '',
        price: e.basePrice?.value ? parseFloat(e.basePrice.value) : null,
        warehouseCode: p.stock?.warehouseCode || null,
        cartQty: e.quantity,
      };
    }
  }

  // 4. Build results
  const ts = new Date().toISOString();
  for (const sku of skus) {
    const info = stockMap[sku];
    if (info) {
      results.push({ sku, ...info, timestamp: ts });
    } else {
      results.push({
        sku,
        stockLevel: null,
        stockStatus: addResults[sku] ? 'not_in_checkout' : 'add_failed',
        name: null, price: null,
        error: addResults[sku] ? 'Added but not in checkout' : 'Failed to add — discontinued or auth issue',
        timestamp: ts,
      });
    }
  }

  // 5. Cleanup — remove all from cart
  for (const sku of skus) {
    await delay(300);
    try {
      await fetch('/zh/hktvfrontend/v1/cart/express/remove_item_from_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sku }),
        credentials: 'include',
      });
    } catch {}
  }

  return JSON.stringify(results);
})()
`;
}

// ─── Public API ──────────────────────────────────────────────────────

/**
 * Probe inventory for multiple SKUs via CDP.
 * @param {string[]} skus
 * @param {{ cdpPort?: number, targetId?: string }} options
 * @returns {Promise<Array<{sku, stockLevel, stockStatus, name, price, ...}>>}
 */
export async function probeInventory(skus, options = {}) {
  const { cdpPort = DEFAULT_CDP_PORT, targetId } = options;

  log(`\n🔍 HKTVmall Inventory Probe v3 (CDP)`);
  log(`   SKUs: ${skus.length}`);
  log(`   CDP: 127.0.0.1:${cdpPort}\n`);

  // 1. Find browser tab
  log(`[1/3] Finding browser tab...`);
  const target = await findTarget(cdpPort, targetId);
  if (!target) {
    throw new Error('No browser tab found. Open HKTVmall in OpenClaw browser first.');
  }
  log(`  ✓ ${target.title || target.url?.slice(0, 60)}`);

  // If tab isn't on HKTVmall, navigate there
  const cdp = new CDPClient(target.webSocketDebuggerUrl);
  await cdp.connect();

  if (!target.url?.includes('hktvmall.com')) {
    log(`  → Navigating to HKTVmall...`);
    await cdp.send('Page.navigate', { url: HKTVMALL_ORIGIN + '/hktv/zh/main' });
    await new Promise(r => setTimeout(r, 3000));
  }

  // 2. Run probe script in browser
  log(`[2/3] Probing ${skus.length} SKU(s) via browser...`);
  const script = buildProbeScript(skus);
  const rawResult = await cdp.evaluate(script);

  let results;
  try {
    results = JSON.parse(rawResult);
  } catch {
    cdp.close();
    throw new Error(`Unexpected response: ${String(rawResult).slice(0, 200)}`);
  }

  if (results.error) {
    cdp.close();
    throw new Error(results.error);
  }

  // 3. Report
  log(`[3/3] Results:`);
  for (const r of results) {
    const icon = r.stockLevel !== null ? '✓' : '✗';
    log(`  ${icon} ${r.sku}: ${r.stockLevel ?? r.error} ${r.name ? '(' + r.name.slice(0, 30) + ')' : ''}`);
  }

  log(`\n✅ Done. ${results.filter(r => r.stockLevel !== null).length}/${results.length} resolved.\n`);

  cdp.close();
  return results;
}

// ─── CLI ─────────────────────────────────────────────────────────────

const isMain = process.argv[1] &&
  fileURLToPath(import.meta.url).replace(/\\/g, '/') === process.argv[1].replace(/\\/g, '/');

if (isMain) {
  const args = process.argv.slice(2);
  const skus = [];
  let cdpPort = DEFAULT_CDP_PORT;
  let targetId = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--cdp-port' && args[i + 1]) cdpPort = parseInt(args[++i], 10);
    else if (args[i] === '--target-id' && args[i + 1]) targetId = args[++i];
    else if (args[i] === '--file' && args[i + 1]) {
      const lines = (await readFile(args[++i], 'utf-8')).split('\n').map(l => l.trim()).filter(Boolean);
      skus.push(...lines);
    }
    else if (!args[i].startsWith('--')) skus.push(args[i]);
  }

  if (!skus.length) {
    log('Usage: node inventory-probe.mjs <sku1> [sku2] ...');
    log('       node inventory-probe.mjs --file skus.txt');
    log('       node inventory-probe.mjs --cdp-port 18792 --target-id <id> <sku>');
    log('\nRequires OpenClaw browser with HKTVmall logged in.');
    process.exit(1);
  }

  probeInventory(skus, { cdpPort, targetId })
    .then(r => console.log(JSON.stringify(r, null, 2)))
    .catch(e => { log(`\n❌ ${e.message}`); process.exit(1); });
}
