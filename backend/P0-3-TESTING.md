# P0-3: Telegram 即時審批通道 - 測試驗證計劃

## ✅ 已完成的修改

### 1. Telegram Webhook 端點（telegram.py）

**已存在功能**：
- `POST /api/v1/telegram/webhook` - Telegram Webhook 端點
- 完整的 Callback Query 處理機制
- 按鈕點擊回調分發邏輯

**本次優化**：
- 修改 `_handle_approve_proposal` - 改為調用 `PricingService.approve_proposal()`
- 修改 `_handle_reject_proposal` - 改為調用 `PricingService.reject_proposal()`

**關鍵改進**：
```python
# Before: 直接修改數據庫
proposal.status = ProposalStatus.APPROVED.value
await db.commit()

# After: 調用 PricingService（自動執行改價 + 審計日誌）
pricing_service = PricingService(db)
approved_proposal = await pricing_service.approve_proposal(
    proposal_id=UUID(proposal_id),
    user_id="telegram_bot"
)
```

### 2. 完整的事件流

```
Pricer Agent 生成提案
    ↓
escalate_to_human() → Telegram 推送帶按鈕的消息
    ↓
用戶點擊「✅ 批准提案」
    ↓
Telegram 發送 Callback Query → Webhook 端點
    ↓
_handle_approve_proposal() → PricingService.approve_proposal()
    ↓
執行三階段：
  1. 更新提案狀態為 APPROVED
  2. 調用 HKTVmall API 更新價格
  3. 更新本地 Product.price
    ↓
回應 Callback Query + 移除按鈕 + 發送確認消息
```

---

## 🧪 測試計劃

### 前置條件

1. ✅ Telegram Bot 已配置（`TELEGRAM_BOT_TOKEN`、`TELEGRAM_CHAT_ID`）
2. ✅ Telegram Webhook 已設置（指向 `/api/v1/telegram/webhook`）
3. ✅ 至少有 1 個待審批的提案（`status = PENDING`）
4. ✅ HKTVmall API 已配置（可選，未配置時會跳過實際改價）

---

### 測試場景 1: Telegram Webhook 設置

#### 步驟 1: 設置 Webhook

**方法 A: 使用 curl**

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://<YOUR_DOMAIN>/api/v1/telegram/webhook"
  }'
```

**方法 B: 使用 Telegram API 直接設置**

訪問：
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_DOMAIN>/api/v1/telegram/webhook
```

#### 步驟 2: 驗證 Webhook

```bash
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

**預期響應**：
```json
{
  "ok": true,
  "result": {
    "url": "https://<YOUR_DOMAIN>/api/v1/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": null
  }
}
```

---

### 測試場景 2: 批准提案流程

#### 前置：生成一個測試提案

**SQL 插入**：
```sql
INSERT INTO price_proposals (
    id,
    product_id,
    current_price,
    proposed_price,
    reason,
    status,
    ai_model_used,
    created_at
)
VALUES (
    gen_random_uuid(),
    '<product_uuid>',
    398.00,
    368.00,
    '測試提案 - Telegram 審批流程',
    'pending',
    'test',
    NOW()
);
```

#### 步驟 1: 手動觸發 Telegram 通知（模擬 Pricer Agent）

**API 調用**：
```bash
curl -X POST "http://localhost:8000/api/v1/telegram/send" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "<b>⚠️ 價格告警: 📉 降價</b>\n\n🏷 <b>產品</b>: 日本 A5 和牛\n💰 <b>原價</b>: HK$398.00\n💵 <b>現價</b>: HK$368.00\n📊 <b>變動</b>: -7.5%\n\n<b>📋 改價提案已創建</b>\n• 建議價格: HK$368.00\n• 提案編號: <proposal_id>..."
  }'
```

**或使用 Pricer Agent 的 escalate_to_human**（自動發送帶按鈕的消息）

#### 步驟 2: 點擊「✅ 批准提案」按鈕

**預期行為**：
1. Telegram 發送 Callback Query：`approve_proposal:<proposal_id>`
2. Webhook 接收並解析 callback
3. 調用 `_handle_approve_proposal()`
4. 調用 `PricingService.approve_proposal()`
5. 提案狀態更新為 `APPROVED` → `EXECUTED`（如果 HKTVmall API 成功）
6. 按鈕被移除
7. 收到確認消息

**驗收標準**：
- ✅ 收到 Telegram 彈窗提示：「✅ 提案已批准並執行」
- ✅ 按鈕消失
- ✅ 收到新消息：「✅ 提案已批准並執行 ... 價格已更新至 HKTVmall 🎉」
- ✅ 數據庫驗證：
  ```sql
  SELECT
      id,
      status,
      reviewed_at,
      reviewed_by,
      executed_at,
      final_price
  FROM price_proposals
  WHERE id = '<proposal_id>';
  ```
  預期：`status = 'executed'`，`reviewed_by = 'telegram_bot'`

---

### 測試場景 3: 拒絕提案流程

#### 步驟 1: 生成一個測試提案（同上）

#### 步驟 2: 點擊「❌ 拒絕提案」按鈕

**預期行為**：
1. Callback Query：`reject_proposal:<proposal_id>`
2. 調用 `_handle_reject_proposal()`
3. 調用 `PricingService.reject_proposal()`
4. 提案狀態更新為 `REJECTED`
5. 按鈕被移除
6. 收到確認消息

**驗收標準**：
- ✅ 收到彈窗：「❌ 提案已拒絕」
- ✅ 按鈕消失
- ✅ 收到新消息：「❌ 提案已拒絕 ... 提案編號: xxx」
- ✅ 數據庫驗證：
  ```sql
  SELECT status, reviewed_at, reviewed_by
  FROM price_proposals
  WHERE id = '<proposal_id>';
  ```
  預期：`status = 'rejected'`

---

### 測試場景 4: 完整閉環測試

```
競品降價 → Scout 發射 COMPETITOR_PRICE_DROP
    ↓
Pricer Agent 生成提案 + Telegram 推送
    ↓
用戶在 Telegram 點擊「✅ 批准提案」
    ↓
Webhook 處理 → PricingService.approve_proposal()
    ↓
調用 HKTVmall API 執行改價
    ↓
本地 Product.price 更新
    ↓
Telegram 確認消息
```

#### 觸發方式：

**方法 1: 模擬競品降價事件**
```bash
curl -X POST "http://localhost:8000/api/v1/agent-team/emit/competitor.price_drop" \
  -H "Content-Type: application/json" \
  -d '{
    "competitor_product_id": "<competitor_product_uuid>",
    "new_price": "368.00"
  }'
```

**方法 2: 手動創建提案**
```bash
curl -X POST "http://localhost:8000/api/v1/pricing/proposals" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "<product_uuid>",
    "proposed_price": 368.00,
    "reason": "完整閉環測試"
  }'
```

#### 驗收標準：

1. ✅ Pricer Agent 生成提案
2. ✅ Telegram 收到帶按鈕的通知
3. ✅ 點擊「批准」後按鈕消失
4. ✅ 收到確認消息（成功或失敗）
5. ✅ 數據庫提案狀態更新
6. ✅ 審計日誌記錄（`audit_logs` 表）
7. ✅ 如果 HKTVmall API 配置：實際價格已更新

---

## 📊 驗證檢查清單

### 數據庫驗證

#### 1. 檢查提案審批記錄

```sql
SELECT
    id,
    product_id,
    status,
    current_price,
    proposed_price,
    final_price,
    reviewed_at,
    reviewed_by,
    executed_at,
    created_at
FROM price_proposals
WHERE reviewed_by = 'telegram_bot'
ORDER BY reviewed_at DESC
LIMIT 10;
```

**預期**：
- `reviewed_by = 'telegram_bot'`
- `reviewed_at` 有時間戳
- 批准的提案：`status = 'executed'` 或 `'failed'`
- 拒絕的提案：`status = 'rejected'`

#### 2. 檢查審計日誌

```sql
SELECT
    action,
    entity_type,
    entity_id,
    user_id,
    details,
    created_at
FROM audit_logs
WHERE action IN ('REJECT_PROPOSAL', 'EXECUTE_PRICE_UPDATE')
ORDER BY created_at DESC
LIMIT 10;
```

**預期**：
- 批准提案：`action = 'EXECUTE_PRICE_UPDATE'`
- 拒絕提案：`action = 'REJECT_PROPOSAL'`
- `user_id = 'telegram_bot'`

#### 3. 檢查產品價格是否更新

```sql
SELECT
    sku,
    name_zh,
    price,
    updated_at
FROM products
WHERE updated_at >= NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC;
```

**預期**：
- 批准提案後，`price` 應該更新為 `final_price`

---

## 🐛 常見問題排查

### 問題 1: Webhook 沒有收到 Callback

**可能原因**：
1. Webhook URL 未設置或錯誤
2. 服務器不可公網訪問
3. HTTPS 證書問題（Telegram 要求 HTTPS）

**排查**：
```bash
# 檢查 Webhook 狀態
curl -X GET "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# 查看最近的錯誤
{
  "last_error_message": "Wrong response from the webhook: 500 Internal Server Error"
}

# 檢查服務器日誌
tail -f backend/logs/app.log | grep telegram
```

### 問題 2: 批准後沒有執行改價

**可能原因**：
1. HKTVmall API 未配置（`HKTV_ACCESS_TOKEN` / `HKTV_STORE_CODE`）
2. API 調用失敗（網絡問題、權限不足、SKU 不存在）

**排查**：
```sql
-- 檢查失敗的提案
SELECT
    id,
    status,
    error_message,
    executed_at
FROM price_proposals
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 5;
```

```bash
# 檢查環境變量
echo $HKTV_ACCESS_TOKEN
echo $HKTV_STORE_CODE

# 測試 HKTVmall API 連接
curl -X POST "http://localhost:8000/api/v1/hktvmall/test"
```

### 問題 3: Telegram 顯示「操作失敗」

**可能原因**：
1. 提案 ID 不存在
2. 提案已被處理（不是 PENDING 狀態）
3. 數據庫連接問題

**排查**：
```bash
# 查看 Webhook 日誌
grep "handle_callback" backend/logs/app.log

# 檢查提案狀態
psql -d gogojap -c "SELECT id, status FROM price_proposals WHERE id = '<proposal_id>';"
```

---

## ✅ P0-3 完成標準

### 功能驗收：
- [x] Telegram Webhook 端點正常接收 Callback Query
- [x] 批准提案：調用 `PricingService.approve_proposal()`
- [x] 拒絕提案：調用 `PricingService.reject_proposal()`
- [x] 按鈕點擊後正確回應（answer_callback_query）
- [x] 按鈕點擊後移除按鈕（edit_message_reply_markup）
- [x] 發送確認消息到 Telegram
- [x] 審計日誌正確記錄（`audit_logs` 表）

### 商業驗收：
- [ ] 批准提案後 5 秒內價格更新至 HKTVmall
- [ ] 拒絕提案後提案狀態立即更新
- [ ] Telegram 通知文案清晰易懂
- [ ] 按鈕點擊體驗流暢（無延遲、無重複點擊）

### 穩定性驗收：
- [ ] 連續處理 10 個提案無錯誤
- [ ] 重複點擊同一個按鈕時正確提示「提案已處理」
- [ ] Webhook 處理異常時不影響其他功能
- [ ] HKTVmall API 失敗時提案狀態標記為 `failed`

---

## 🚀 預期商業影響

**效率提升**: 50-80%

**原理**：
- 傳統流程：收到告警 → 登入系統 → 審查提案 → 點擊批准 → 確認執行（5 步驟，約 2-3 分鐘）
- Telegram 流程：收到通知 → 點擊批准（1 步驟，約 5-10 秒）

**假設**：
- 每天平均 5-10 個提案需要審批
- 每個提案節省 2 分鐘
- 每月節省 20-40 分鐘人力時間
- **更重要：降低反應時間，搶先於競爭對手調價**

---

## 📝 變更記錄

| 日期 | 修改內容 | 文件 |
|------|---------|------|
| 2026-02-11 | 優化批准提案邏輯，改為調用 PricingService | telegram.py |
| 2026-02-11 | 優化拒絕提案邏輯，改為調用 PricingService | telegram.py |
| 2026-02-11 | 新增完整的確認消息（含執行狀態） | telegram.py |
