# Clawdbot 抓取邏輯完整解析

> 詳細說明我們實現的 Clawdbot 連接器的工作原理與數據流程

---

## 📊 完整數據流程圖

```
用戶請求
    ↓
[1] API 路由 (/api/v1/scrape)
    ↓
[2] UnifiedScraper (環境切換)
    ↓
[3] ClawdbotConnector.scrapeHKTVProduct()
    ↓
[4] 生成任務配置
    {
      id: "task_xxx",
      type: "product",
      url: "https://www.hktvmall.com/...",
      config: {
        waitForSelector: ".product-details",
        actions: [...],
        extractors: [...]
      }
    }
    ↓
[5] ClawdbotConnector.scrape()
    ├─ 檢查速率限制
    ├─ 確保 WebSocket 連接
    └─ 創建 Promise + 超時定時器
    ↓
[6] 發送 WebSocket 消息
    ws.send({
      type: "scrape_task",
      task: { ... }
    })
    ↓
[7] 等待 Clawdbot 響應
    ├─ 超時 60 秒 → ❌ 拋出錯誤
    └─ 收到響應 → 繼續
    ↓
[8] handleMessage() 處理響應
    {
      type: "task_result",
      taskId: "task_xxx",
      result: { ... }
    }
    ↓
[9] 從任務隊列找到 resolver
    ↓
[10] 返回結果給用戶
```

---

## 🔍 各步驟詳細說明

### 步驟 1-2: API 路由與環境切換

**文件**: `frontend/src/app/api/v1/scrape/route.ts`

```typescript
// 用戶請求
POST /api/v1/scrape
{
  action: "scrape_product",
  params: { url: "..." }
}

// UnifiedScraper 根據環境自動選擇
const scraper = getUnifiedScraper();
// development → ClawdbotConnector
// production → FirecrawlConnector
```

---

### 步驟 3-4: 生成任務配置

**文件**: `lib/connectors/clawdbot-connector.ts:220-253`

```typescript
async scrapeHKTVProduct(productUrl: string) {
  // 生成唯一任務 ID
  const taskId = this.generateTaskId();
  // → "task_1738001234567_abc123def"

  // 構建任務配置
  const task = {
    id: taskId,
    type: 'product',
    url: productUrl,
    config: {
      // 等待這個選擇器出現
      waitForSelector: '.product-details',

      // 執行的動作序列
      actions: [
        { type: 'wait', delay: 2000 },           // 等待 2 秒
        { type: 'scroll', value: 500 },          // 向下滾動 500px
        { type: 'click', selector: '.show-more-btn' }  // 點擊按鈕
      ],

      // 數據提取規則
      extractors: [
        { field: 'name', selector: '.product-title' },
        { field: 'price', selector: '.current-price' },
        // ... 12 個提取器
      ],

      screenshot: true  // 是否截圖
    }
  };

  return this.scrape(task);
}
```

**關鍵點**:
- ✅ 為每個請求生成唯一 ID
- ✅ 配置了等待選擇器（`.product-details`）
- ✅ 定義了提取規則
- ⚠️ **假設 HKTVmall 使用這些 CSS 選擇器**

---

### 步驟 5: 核心抓取邏輯

**文件**: `lib/connectors/clawdbot-connector.ts:187-213`

```typescript
async scrape(task: ScrapeTask): Promise<ScrapeResult> {
  // 5.1 檢查速率限制
  await this.checkRateLimit();
  // → 每分鐘最多 30 個請求

  // 5.2 確保 WebSocket 連接
  if (!this.connected) {
    await this.connect();
  }

  // 5.3 創建 Promise 等待結果
  return new Promise((resolve, reject) => {

    // 5.4 設置超時定時器（60 秒）
    const timeout = setTimeout(() => {
      this.taskQueue.delete(task.id);
      reject(new Error('抓取任務超時'));  // ← 你看到的錯誤！
    }, this.config.timeout);  // 60000ms

    // 5.5 將 resolver 存入任務隊列
    this.taskQueue.set(task.id, (result: ScrapeResult) => {
      clearTimeout(timeout);
      resolve(result);
    });

    // 5.6 發送任務到 Clawdbot
    const message = JSON.stringify({
      type: 'scrape_task',
      task,
    });

    this.ws?.send(message);
    // ← 消息已發送，等待響應...
  });
}
```

**流程**:
1. ✅ 檢查速率限制
2. ✅ 確保連接存在
3. ✅ 創建超時定時器（60秒）
4. ✅ 保存回調函數到隊列
5. ✅ 發送 WebSocket 消息
6. ⏳ **等待 Clawdbot 響應**

---

### 步驟 6: WebSocket 消息格式

**發送到 Clawdbot**:
```json
{
  "type": "scrape_task",
  "task": {
    "id": "task_1738001234567_abc123def",
    "type": "product",
    "url": "https://www.hktvmall.com/...",
    "config": {
      "waitForSelector": ".product-details",
      "actions": [...],
      "extractors": [...]
    }
  }
}
```

**期望從 Clawdbot 收到**:
```json
{
  "type": "task_result",
  "taskId": "task_1738001234567_abc123def",
  "result": {
    "success": true,
    "taskId": "task_xxx",
    "url": "https://...",
    "data": { "name": "...", "price": "..." },
    "durationMs": 15000,
    "scrapedAt": "2026-01-27T..."
  }
}
```

---

### 步驟 7-8: 響應處理

**文件**: `lib/connectors/clawdbot-connector.ts:139-153`

```typescript
private handleMessage(message: string): void {
  try {
    const response = JSON.parse(message);

    // 檢查消息類型
    if (response.type === 'task_result') {
      // 從隊列中找到對應的 resolver
      const resolver = this.taskQueue.get(response.taskId);

      if (resolver) {
        resolver(response.result);  // 調用 resolve()
        this.taskQueue.delete(response.taskId);
      }
    }
  } catch (error) {
    console.error('解析 Clawdbot 消息失敗:', error);
  }
}
```

**流程**:
1. 收到 WebSocket 消息
2. 解析 JSON
3. 檢查 `type === 'task_result'`
4. 根據 `taskId` 找到對應的 resolver
5. 調用 resolver 返回結果
6. 從隊列刪除任務

---

## 🔴 問題診斷：為什麼超時？

### 可能原因 1: Clawdbot 沒有響應

**症狀**: 60秒後超時錯誤

**原因**:
```
我們發送: { type: "scrape_task", task: {...} }
             ↓
         ws://127.0.0.1:18789
             ↓
         [黑洞？沒有響應]
             ↓
         60 秒後超時
```

**為什麼沒響應？**
- ❌ Clawdbot 不認識 `type: "scrape_task"` 消息格式
- ❌ Clawdbot 沒有實際運行（只是 WebSocket 監聽）
- ❌ Clawdbot 的瀏覽器池未初始化
- ❌ 消息格式與 Clawdbot 期望的不匹配

---

### 可能原因 2: 消息格式不匹配

**我們的假設**:
```json
{
  "type": "scrape_task",
  "task": { ... }
}
```

**Clawdbot 實際期望的格式可能是**:
```json
{
  "action": "browser.navigate",
  "params": {
    "url": "...",
    "waitFor": "..."
  }
}
```

或者其他完全不同的格式。

**問題**: 我們沒有查看 Clawdbot 的實際 API 文檔！

---

### 可能原因 3: Clawdbot 未完全啟動

**WebSocket 監聽** ≠ **服務完全啟動**

```
端口 18789 監聽中 ✅
    ↓
但內部組件未初始化:
    - 瀏覽器池 ❌
    - 消息路由器 ❌
    - Agent 系統 ❌
```

**驗證方法**:
```bash
cd clawdbot
pnpm start

# 看啟動日誌，確認：
# ✅ Browser pool initialized
# ✅ Agent system ready
# ✅ Gateway listening
```

---

## 🎯 根本問題

### 我們的實現是**猜測**的

```
我們假設:
  Clawdbot 接受 { type: "scrape_task" } 格式

實際情況:
  Clawdbot 可能使用完全不同的協議
```

**證據**:
1. ✅ WebSocket 連接成功（健康檢查通過）
2. ✅ 消息發送成功（無錯誤）
3. ❌ **永遠沒有響應**（60秒超時）

**結論**:
- Clawdbot 收到了消息
- 但不知道如何處理
- 所以沒有響應

---

## ✅ 解決方案

### 方案 A: 查看 Clawdbot 實際 API

**正確做法**:
```bash
cd clawdbot
# 查看文檔
cat README.md
cat docs/gateway-api.md

# 或查看源碼
cat src/gateway/message-handler.ts
```

**找出**:
1. Clawdbot 期望的消息格式
2. 如何發起抓取任務
3. 響應格式是什麼

---

### 方案 B: 使用 Clawdbot 的官方客戶端

Clawdbot 可能提供了官方的客戶端庫。

**檢查**:
```bash
cd clawdbot
cat package.json | grep "exports"
# 是否有導出的客戶端？
```

---

### 方案 C: 切換到 Firecrawl（推薦）

**原因**:
- ✅ Firecrawl 有明確的 API 文檔
- ✅ 消息格式已知
- ✅ 雲端服務，無需本地配置

**實現**:
```typescript
// Firecrawl 的實現是明確的
await fetch('https://api.firecrawl.dev/v1/scrape', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: targetUrl,
    formats: ['html', 'markdown']
  })
});
```

---

## 📋 總結

### 當前實現的邏輯

```
1. 用戶請求 → API 路由
2. 環境切換 → ClawdbotConnector
3. 生成任務配置（CSS 選擇器）
4. 發送 WebSocket 消息: { type: "scrape_task" }
5. 等待響應（60秒超時）
6. 收到響應 → 解析並返回
```

### 超時的根本原因

```
消息格式不匹配
    ↓
Clawdbot 不處理
    ↓
沒有響應
    ↓
60 秒超時
```

### 修復建議

**優先順序**:
1. 🥇 **切換到 Firecrawl**（5分鐘內可用）
2. 🥈 **查看 Clawdbot 文檔**（找到正確的 API）
3. 🥉 **直接用 Playwright**（跳過 Clawdbot）

---

## 🤔 下一步行動

你想要：
1. **查看 Clawdbot 源碼**找出正確的消息格式？
2. **切換到 Firecrawl** 先完成測試？
3. **用 Playwright** 直接實現抓取？

告訴我你的選擇，我會立即協助！
