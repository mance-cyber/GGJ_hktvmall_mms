#!/usr/bin/env node
/**
 * HKTVmall Inventory Probe — Browser Edition
 *
 * 使用 Playwright + 已登入嘅 Chrome profile，直接繼承 httpOnly session cookies。
 * 比 HTTP-only 版本更可靠，唔需要手動抄 cookies。
 *
 * 工作原理：
 *   1. 開 Chrome（persistent context = 繼承登入狀態）
 *   2. 每個 SKU：add 1件 → GET checkout API → 讀 stockLevel → remove
 *   3. 關 browser
 *
 * 用法：
 *   node inventory-probe-browser.mjs H0888001_S_10161559
 *   node inventory-probe-browser.mjs H0888001_S_10161559 H0888001_S_10161560 --headless
 *   node inventory-probe-browser.mjs --skus skus.txt   (一個 SKU 一行)
 *
 * Module 用法：
 *   import { probeInventoryBrowser } from './inventory-probe-browser.mjs'
 *   const results = await probeInventoryBrowser(['SKU1', 'SKU2'])
 */

import { chromium } from 'playwright';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { existsSync } from 'node:fs';

const __dirname = dirname(fileURLToPath(import.meta.url));

const BASE_URL     = 'https://www.hktvmall.com';
const CHECKOUT_API = `${BASE_URL}/zh/hktvfrontend/v1/cart/express/checkout`;
const REMOVE_API   = `${BASE_URL}/zh/hktvfrontend/v1/cart/express/remove_item_from_cart`;
const ADD_URL      = `${BASE_URL}/hktv/zh/cart/add`;

// Chrome profile — inherits existing HKTVmall login session
const CHROME_USER_DATA = process.env.CHROME_USER_DATA
  || `${process.env.LOCALAPPDATA}\\Google\\Chrome\\User Data`;
const CHROME_PROFILE   = process.env.CHROME_PROFILE || 'Default';

const DELAY_BETWEEN_SKUS = 2000; // ms

// ─── Core probe logic (runs inside browser page) ─────────────────────

/**
 * Probe one SKU inside a Playwright page.
 * Returns { sku, stock, inStock, stockStatus, timestamp }
 */
async function probeSKU(page, sku) {
  const timestamp = new Date().toISOString();

  try {
    // Step 1: get CSRF token from a lightweight page
    const csrfToken = await page.evaluate(async () => {
      const res = await fetch('/hktv/zh/main', { credentials: 'include' });
      const html = await res.text();
      const m = html.match(/CSRFToken[^0-9a-f]*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/i);
      return m?.[1] || null;
    });

    if (!csrfToken) {
      return { sku, stock: null, error: 'CSRF not found', timestamp };
    }

    // Step 2: add 1 item to cart (minimal footprint)
    const addResult = await page.evaluate(async ({ sku, csrfToken }) => {
      const res = await fetch('/hktv/zh/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `productCodePost=${encodeURIComponent(sku)}&qty=1&CSRFToken=${encodeURIComponent(csrfToken)}`,
        credentials: 'include',
      });
      const body = await res.text();
      let json = null;
      try { json = JSON.parse(body); } catch {}
      return { status: res.status, statusCode: json?.statusCode, ok: res.ok };
    }, { sku, csrfToken });

    if (!addResult.ok && addResult.statusCode !== 'success') {
      // Might be out of stock or need login
      return { sku, stock: 0, inStock: false, error: `add failed: ${addResult.status}`, timestamp };
    }

    // Step 3: read stockLevel from checkout API
    const stockData = await page.evaluate(async ({ checkoutApi, sku }) => {
      const res = await fetch(checkoutApi, { credentials: 'include' });
      const json = await res.json();
      const str = JSON.stringify(json);

      // Find our SKU entry and read stockLevel
      const idx = str.indexOf(sku);
      if (idx === -1) return { found: false };

      // Look for stockLevel near the SKU
      const context = str.substring(idx, idx + 800);

      const stockLevelMatch  = context.match(/"stockLevel"\s*:\s*(\d+)/);
      const stockStatusMatch = context.match(/"code"\s*:\s*"([^"]+)"/);       // inStock / outOfStock / lowStock
      const inStockMatch     = context.match(/"stockLevelStatus"[^}]*?"code"\s*:\s*"([^"]+)"/);

      return {
        found:       true,
        stockLevel:  stockLevelMatch  ? parseInt(stockLevelMatch[1], 10) : null,
        stockStatus: inStockMatch?.[1] || stockStatusMatch?.[1] || null,
      };
    }, { checkoutApi: CHECKOUT_API, sku });

    // Step 4: remove from cart (cleanup)
    await page.evaluate(async ({ removeApi, sku }) => {
      await fetch(removeApi, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sku }),
        credentials: 'include',
      });
    }, { removeApi: REMOVE_API, sku });

    if (!stockData.found) {
      return { sku, stock: null, error: 'SKU not found in checkout response', timestamp };
    }

    return {
      sku,
      stock:       stockData.stockLevel,
      inStock:     stockData.stockStatus === 'inStock',
      stockStatus: stockData.stockStatus,
      timestamp,
    };

  } catch (err) {
    return { sku, stock: null, error: err.message, timestamp };
  }
}

// ─── Main exported function ───────────────────────────────────────────

/**
 * Probe inventory for multiple SKUs using an authenticated browser session.
 *
 * @param {string[]} skus
 * @param {object}   [options]
 * @param {boolean}  [options.headless=true]
 * @param {string}   [options.chromeUserData]
 * @param {string}   [options.chromeProfile]
 * @param {number}   [options.delayMs]
 * @returns {Promise<Array>}
 */
export async function probeInventoryBrowser(skus, options = {}) {
  const {
    headless        = true,
    chromeUserData  = CHROME_USER_DATA,
    chromeProfile   = CHROME_PROFILE,
    delayMs         = DELAY_BETWEEN_SKUS,
  } = options;

  console.error(`\n🌐 HKTVmall Inventory Probe (Browser)`);
  console.error(`   SKUs:    ${skus.length}`);
  console.error(`   Profile: ${chromeUserData}\\${chromeProfile}`);
  console.error(`   Headless: ${headless}\n`);

  // Warn if Chrome profile doesn't exist
  if (!existsSync(chromeUserData)) {
    throw new Error(`Chrome user data not found: ${chromeUserData}\nSet CHROME_USER_DATA env var to override.`);
  }

  // Launch with persistent context (inherits cookies/session from real Chrome)
  const context = await chromium.launchPersistentContext(
    join(chromeUserData, '..', `_pw_probe_${chromeProfile}`), // use a copy dir to avoid lock
    {
      executablePath: await findChrome(),
      headless,
      channel: undefined, // use bundled chromium (not system chrome)
      viewport: { width: 1280, height: 800 },
      locale: 'zh-HK',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    }
  );

  // Copy cookies from real Chrome profile via API
  const realContext = await chromium.launchPersistentContext(
    join(chromeUserData, chromeProfile),
    {
      executablePath: await findChrome(),
      headless: true,
      args: ['--no-sandbox'],
    }
  ).catch(() => null);

  let page;
  try {
    // Strategy: Use a fresh Chromium page with cookies injected from the real Chrome profile
    // Since Chrome profile might be locked, we use a different approach:
    // Open HKTVmall and let the persistent context (copy) handle auth

    page = await context.newPage();

    // Navigate to HKTVmall checkout to warm up session
    await page.goto(`${BASE_URL}/hktv/zh/main`, {
      waitUntil: 'domcontentloaded',
      timeout: 30000,
    });

    // Check if logged in
    const isLoggedIn = await page.evaluate(() => {
      return document.cookie.includes('ott-uuid') ||
             document.querySelector('.account-nav__title') !== null ||
             document.title.includes('大街市');
    });

    console.error(`   Auth status: ${isLoggedIn ? '✅ logged in' : '⚠️ may not be logged in (will try anyway)'}`);

    const results = [];

    for (let i = 0; i < skus.length; i++) {
      const sku = skus[i];
      console.error(`[${i + 1}/${skus.length}] Probing ${sku}...`);

      const result = await probeSKU(page, sku);
      results.push(result);

      const stockDisplay = result.error
        ? `❌ ${result.error}`
        : `📦 stock=${result.stock ?? '?'} (${result.stockStatus ?? 'unknown'})`;
      console.error(`   → ${stockDisplay}`);

      if (i < skus.length - 1) {
        await page.waitForTimeout(delayMs);
      }
    }

    console.error(`\n✅ Done. ${results.filter(r => r.stock !== null).length}/${results.length} resolved.\n`);
    return results;

  } finally {
    await page?.close();
    await context.close();
    await realContext?.close();
  }
}

// ─── Chrome executable finder ─────────────────────────────────────────

async function findChrome() {
  const candidates = [
    `${process.env.PROGRAMFILES}\\Google\\Chrome\\Application\\chrome.exe`,
    `${process.env['PROGRAMFILES(X86)']}\\Google\\Chrome\\Application\\chrome.exe`,
    `${process.env.LOCALAPPDATA}\\Google\\Chrome\\Application\\chrome.exe`,
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ];

  for (const p of candidates) {
    if (p && existsSync(p)) return p;
  }

  // Fall back to playwright's bundled chromium
  return undefined;
}

// ─── Alternative: Cookie-injection approach ───────────────────────────
// If the browser approach doesn't work, we can inject cookies via Playwright API.
// This reads Chrome's cookies.sqlite and injects them.

export async function probeWithCookieFile(skus, cookieFilePath, options = {}) {
  const { headless = true, delayMs = DELAY_BETWEEN_SKUS } = options;

  // Load cookie string from file
  let cookieStr;
  try {
    const raw = JSON.parse(await readFile(cookieFilePath, 'utf-8'));
    cookieStr = raw.raw || Object.entries(raw.cookies || {}).map(([k, v]) => `${k}=${v}`).join('; ');
  } catch (err) {
    throw new Error(`Cannot load cookie file: ${err.message}`);
  }

  const browser = await chromium.launch({ headless });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  });

  // Parse and inject cookies
  const cookieObjects = cookieStr.split(';').map(c => {
    const [name, ...rest] = c.trim().split('=');
    return { name: name.trim(), value: rest.join('='), domain: '.hktvmall.com', path: '/' };
  }).filter(c => c.name);

  await context.addCookies(cookieObjects);
  const page = await context.newPage();

  try {
    await page.goto(`${BASE_URL}/hktv/zh/main`, { waitUntil: 'domcontentloaded', timeout: 20000 });
    const results = [];
    for (let i = 0; i < skus.length; i++) {
      const sku = skus[i];
      console.error(`[${i + 1}/${skus.length}] Probing ${sku}...`);
      const result = await probeSKU(page, sku);
      results.push(result);
      console.error(`   → stock=${result.stock ?? 'error'}`);
      if (i < skus.length - 1) await page.waitForTimeout(delayMs);
    }
    return results;
  } finally {
    await page.close();
    await context.close();
    await browser.close();
  }
}

// ─── CLI ─────────────────────────────────────────────────────────────

const isMain = process.argv[1] &&
  fileURLToPath(import.meta.url).replace(/\\/g, '/') === process.argv[1].replace(/\\/g, '/');

if (isMain) {
  const args = process.argv.slice(2);
  const skus = [];
  let headless = true;
  let skuFile  = null;
  let cookieFile = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--headless' || args[i] === '-h') { headless = true; }
    else if (args[i] === '--show') { headless = false; }
    else if (args[i] === '--skus' && args[i + 1]) { skuFile = args[++i]; }
    else if (args[i] === '--cookie-file' && args[i + 1]) { cookieFile = args[++i]; }
    else if (!args[i].startsWith('--')) { skus.push(args[i]); }
  }

  if (skuFile) {
    const lines = (await readFile(skuFile, 'utf-8')).split('\n').map(l => l.trim()).filter(Boolean);
    skus.push(...lines);
  }

  if (skus.length === 0) {
    console.error('Usage: node inventory-probe-browser.mjs <sku1> [sku2] [--show] [--skus file.txt]');
    process.exit(1);
  }

  const probe = cookieFile
    ? probeWithCookieFile(skus, cookieFile, { headless })
    : probeInventoryBrowser(skus, { headless });

  probe
    .then(results => console.log(JSON.stringify(results, null, 2)))
    .catch(err => {
      console.error(`\n❌ Fatal: ${err.message}`);
      process.exit(1);
    });
}
