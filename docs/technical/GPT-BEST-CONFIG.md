# GPT-Best 中轉 API 配置指南

## 概述

GPT-Best (https://gpt-best.apifox.cn/) 是一個中轉 API 服務，支持 Claude 模型調用。

---

## 📋 配置信息

### 1. 獲取 API 憑證

1. 訪問：https://gpt-best.apifox.cn/
2. 註冊/登入帳號
3. 進入管理後台 → API KEYS
4. 生成新的 API Key

你會得到：
- **Base URL**：`https://api.gpt-best.com/v1`（或類似地址）
- **API Key**：`sk-xxxxxxxxxxxxxxxx`

### 2. 確認支持的模型

在平台的「模型列表」頁面，確認以下模型是否可用：

**簡單任務**：
- ✅ `claude-haiku-4-5-20251001-thinking`
- 或 `claude-3-5-haiku-20241022`（備選）

**中高階任務**：
- ✅ `claude-opus-4-6-thinking`
- 或 `claude-opus-4-20250514`（備選）

---

## 🛠️ Zeabur 環境變數配置

### 完整配置（推薦）

```bash
# ==================== API 端點配置 ====================
# 替換為你從 GPT-Best 平台獲取的實際 Base URL
AI_BASE_URL=https://api.gpt-best.com/v1

# 替換為你從 GPT-Best 管理後台生成的 API Key
AI_API_KEY=sk-xxxxxxxxxxxxxxxx

# ==================== 模型分級配置 ====================
# 簡單任務：使用 Haiku（快速 + 經濟）
AI_MODEL_SIMPLE=claude-haiku-4-5-20251001-thinking

# 中等任務：使用 Opus（平衡性能）
AI_MODEL_MEDIUM=claude-opus-4-6-thinking

# 複雜任務：使用 Opus（最強推理）
AI_MODEL_COMPLEX=claude-opus-4-6-thinking

# ==================== 向後兼容配置 ====================
# 預設模型（如果任務沒有指定複雜度）
AI_MODEL=claude-opus-4-6-thinking

# Anthropic 官方 API Key（留空，使用中轉 API）
ANTHROPIC_API_KEY=
```

---

## 🔍 模型名稱對照

### GPT-Best 可能使用的模型名稱

中轉 API 的模型名稱可能與官方不同。請在平台查看實際可用的名稱：

| 官方模型 ID | 可能的中轉 API 名稱 | 用途 |
|-----------|-------------------|------|
| claude-3-5-haiku-20241022 | `claude-3-5-haiku` | 簡單任務 |
| claude-3-5-sonnet-20241022 | `claude-3-5-sonnet` | 中等任務 |
| claude-opus-4-20250514 | `claude-opus-4` | 高階任務 |
| - | `claude-haiku-4-5-20251001-thinking` | 簡單任務（Thinking 模式） |
| - | `claude-opus-4-6-thinking` | 高階任務（Thinking 模式） |

**重要**：如果 thinking 模式的模型不可用，使用標準版本作為備選：
```bash
AI_MODEL_SIMPLE=claude-3-5-haiku
AI_MODEL_MEDIUM=claude-3-5-sonnet
AI_MODEL_COMPLEX=claude-opus-4
```

---

## 💰 定價信息（基於你提供的）

| Token 類型 | 價格 | 說明 |
|-----------|------|------|
| Input | ¥4/M tokens | 提示詞輸入 |
| Output | ¥20/M tokens | AI 生成內容 |

### 月度成本估算

**小規模（100 SKU）**：
- Input: 0.24M × ¥4 = ¥0.96
- Output: 0.098M × ¥20 = ¥1.96
- **總計：~¥3/月**

**中規模（300 SKU）**：
- Input: 0.72M × ¥4 = ¥2.88
- Output: 0.29M × ¥20 = ¥5.80
- **總計：~¥9/月**

**大規模（500+ SKU）**：
- Input: 1.2M × ¥4 = ¥4.80
- Output: 0.49M × ¥20 = ¥9.80
- **總計：~¥15/月**

---

## 🚀 部署步驟

### 1. 在 Zeabur 設定環境變數

1. 登入 [Zeabur Dashboard](https://zeabur.com/)
2. 選擇 GoGoJap Backend 服務
3. Settings → Environment Variables
4. 添加上述所有環境變數
5. 點擊 "Save"

### 2. 重啟服務

Zeabur 會自動觸發重新部署（約 2-3 分鐘）。

### 3. 驗證配置

#### 方法 A：查看日誌

在 Zeabur Dashboard → Logs，應該看到：
```
[INFO] Using AI Base URL: https://api.gpt-best.com/v1
[INFO] AI API Key: sk-****（前幾個字符）
[INFO] Model Strategy Loaded:
  - Simple: claude-haiku-4-5-20251001-thinking
  - Medium: claude-opus-4-6-thinking
  - Complex: claude-opus-4-6-thinking
```

#### 方法 B：測試 API 調用

```bash
# 測試簡單任務
curl -X POST https://ggj-back.zeabur.app/api/v1/content/test \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"complexity": "simple", "message": "測試"}'

# 應返回
{
  "model": "claude-haiku-4-5-20251001-thinking",
  "status": "success"
}
```

#### 方法 C：前端測試

1. 訪問：https://ggj-front.zeabur.app
2. 登入系統
3. 進入「商品管理」→「AI 文案生成」
4. 生成一段文案
5. 檢查是否成功生成

---

## 🔧 故障排除

### 問題 1：401 Unauthorized

**症狀**：
```
Error: Authentication failed: 401 Unauthorized
```

**解決**：
1. 確認 API Key 正確複製（包括 `sk-` 前綴）
2. 檢查 API Key 是否過期
3. 確認帳戶餘額充足
4. 重新生成 API Key

### 問題 2：Model not found

**症狀**：
```
Error: Model 'claude-haiku-4-5-20251001-thinking' not found
```

**解決**：
1. 登入 GPT-Best 查看實際可用的模型名稱
2. 更新環境變數為正確的模型名稱
3. 如果 thinking 模式不可用，改用標準模型：
   ```bash
   AI_MODEL_SIMPLE=claude-3-5-haiku
   AI_MODEL_MEDIUM=claude-3-5-sonnet
   AI_MODEL_COMPLEX=claude-opus-4
   ```

### 問題 3：Base URL 無效

**症狀**：
```
Error: Connection refused to https://api.gpt-best.com/v1
```

**解決**：
1. 登入 GPT-Best 管理後台
2. 查找「Base URL」或「API 端點」設定
3. 確認正確的 Base URL（可能是）：
   - `https://api.gpt-best.com/v1`
   - `https://gpt-best.apifox.cn/v1`
   - `https://api.gptbest.com/v1`
4. 更新 `AI_BASE_URL` 環境變數

### 問題 4：Rate Limit Exceeded

**症狀**：
```
Error: 429 Too Many Requests
```

**解決**：
1. 檢查帳戶的 QPM/RPM 限制
2. 考慮升級套餐
3. 實施請求頻率控制

---

## 📊 監控與優化

### 成本監控

建議在代碼中添加日誌記錄：

```python
import logging

logger = logging.getLogger(__name__)

# 記錄每次 AI 調用
logger.info(f"AI Call: model={model}, input_tokens={input_tokens}, "
           f"output_tokens={output_tokens}, cost=¥{cost:.4f}")
```

### 每月報告

創建自動化腳本，每月統計：
- 總調用次數
- Input tokens 總量
- Output tokens 總量
- 總成本
- 各模型使用佔比

---

## 🎯 最佳實踐

### 1. 備用 API 配置

建議配置備用 API（防止主 API 故障）：

```bash
# 主 API
AI_BASE_URL=https://api.gpt-best.com/v1
AI_API_KEY=sk-primary-xxxxxxxx

# 備用 API（可選）
AI_FALLBACK_BASE_URL=https://api.anthropic.com
AI_FALLBACK_API_KEY=sk-ant-xxxxxxxx
```

### 2. 模型快取

啟用 Prompt Caching（如果 GPT-Best 支持）：
- 節省 90% 重複內容的成本
- 特別適合 GoGoJap 品牌背景等固定 prompt

### 3. 批次處理

合併多個簡單任務到一次 API 調用：
```python
# 不好：多次調用
result1 = ai_call("分析商品 A")
result2 = ai_call("分析商品 B")
result3 = ai_call("分析商品 C")

# 好：批次調用
results = ai_call("分析以下商品：A, B, C")
```

---

## 📞 技術支持

如果遇到問題：

1. **GPT-Best 平台**：
   - 文檔：https://gpt-best.apifox.cn/llms.txt
   - 客服：查看平台聯繫方式

2. **GoGoJap 系統**：
   - GitHub Issues：報告 Bug
   - 技術文檔：`docs/technical/`

---

## 🔗 相關文檔

- [多模型分級策略](./MULTI-MODEL-STRATEGY.md)
- [Claude OAuth 設定](./CLAUDE-OAUTH-SETUP.md)
- [成本優化指南](./COST-OPTIMIZATION.md)
