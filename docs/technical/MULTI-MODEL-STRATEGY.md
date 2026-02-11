# 多模型分級策略配置指南

## 概述

GoGoJap 系統支持**多模型分級策略**，根據任務複雜度自動選擇最適合的 AI 模型，以優化成本和性能。

---

## 🎯 模型分配策略

### 任務分類

| 任務類型 | 複雜度 | 推薦模型 | Token 消耗 | 月調用次數 |
|---------|-------|---------|-----------|-----------|
| **簡單任務** | SIMPLE | Haiku 4.5 Thinking | ~2000 | ~100 |
| **中等任務** | MEDIUM | Opus 4.6 Thinking | ~3000 | ~80 |
| **複雜任務** | COMPLEX | Opus 4.6 Thinking | ~5000 | ~30 |

### 任務映射

#### 簡單任務（SIMPLE）→ Haiku 4.5 Thinking
- ✅ 競品 URL 映射
- ✅ SEO 關鍵詞提取
- ✅ 基礎數據分析
- ✅ 分類標籤建議

**特點**：
- 快速響應（< 2 秒）
- 成本最低（¥1.8/M input, ¥9/M output）
- 適合高頻調用

#### 中等任務（MEDIUM）→ Opus 4.6 Thinking
- ✅ 商品文案生成
- ✅ 定價分析與建議
- ✅ SEO 內容優化
- ✅ 競品數據解讀

**特點**：
- 平衡性能和成本
- 深度思考能力
- 適合日常業務

#### 複雜任務（COMPLEX）→ Opus 4.6 Thinking
- ✅ 市場趨勢分析
- ✅ 戰略決策建議
- ✅ 深度競品研究
- ✅ 全面 SEO 審計

**特點**：
- 最強推理能力
- 長文本生成
- 適合低頻高價值任務

---

## 🛠️ 環境變數配置

### 在 Zeabur Backend 設定

```bash
# ==================== 中轉 API 配置 ====================

# API 端點（替換為你的中轉 API 地址）
AI_BASE_URL=https://your-relay-api.com/v1

# API Key（中轉 API 的 Key）
AI_API_KEY=sk-xxxxxxxxxxxxxxxx

# ==================== 模型分級配置 ====================

# 簡單任務模型（經濟型）
AI_MODEL_SIMPLE=claude-haiku-4-5-20251001-thinking

# 中等任務模型（平衡型）
AI_MODEL_MEDIUM=claude-opus-4-6-thinking

# 複雜任務模型（最強型）
AI_MODEL_COMPLEX=claude-opus-4-6-thinking

# ==================== 向後兼容（可選）====================

# 預設模型（如果任務沒有指定複雜度）
AI_MODEL=claude-opus-4-6-thinking
```

---

## 📊 成本估算

### 使用模型分級策略

假設月度使用：
- 簡單任務：100 次 × 2000 tokens = 200k tokens
- 中等任務：80 次 × 3000 tokens = 240k tokens
- 複雜任務：30 次 × 5000 tokens = 150k tokens

**總計**：~590k tokens/月

#### 方案 A：全用 Opus 4.6（無分級）
```
Input (60%): 0.354M × ¥105 = ¥37.17
Output (40%): 0.236M × ¥525 = ¥123.90
總成本: ~¥161/月
```

#### 方案 B：使用分級策略（推薦）
```
簡單任務（Haiku 4.5）:
  Input: 0.12M × ¥1.8 = ¥0.22
  Output: 0.08M × ¥9 = ¥0.72

中等任務（Opus 4.6）:
  Input: 0.144M × ¥105 = ¥15.12
  Output: 0.096M × ¥525 = ¥50.40

複雜任務（Opus 4.6）:
  Input: 0.09M × ¥105 = ¥9.45
  Output: 0.06M × ¥525 = ¥31.50

總成本: ~¥107/月
```

**節省**：¥161 - ¥107 = **¥54/月（33.5%）** ✅

#### 方案 C：使用中轉 API（¥4/¥20）
```
簡單任務（Haiku）:
  Input: 0.12M × ¥4 = ¥0.48
  Output: 0.08M × ¥20 = ¥1.60

中等任務（Opus）:
  Input: 0.144M × ¥4 = ¥0.58
  Output: 0.096M × ¥20 = ¥1.92

複雜任務（Opus）:
  Input: 0.09M × ¥4 = ¥0.36
  Output: 0.06M × ¥20 = ¥1.20

總成本: ~¥6/月
```

**節省**：¥161 - ¥6 = **¥155/月（96.3%）** 🎉

---

## 🔧 代碼實現示例

### 在服務中使用多模型

```python
from app.services.ai_service import AISettingsService, TaskComplexity

async def generate_content(db: AsyncSession, product_id: str):
    # 獲取 AI 配置
    config = await AISettingsService.get_config(db)

    # 根據任務選擇模型
    # 簡單任務：競品映射
    simple_model = config.get_model_by_complexity(TaskComplexity.SIMPLE)

    # 中等任務：文案生成
    medium_model = config.get_model_by_complexity(TaskComplexity.MEDIUM)

    # 複雜任務：市場分析
    complex_model = config.get_model_by_complexity(TaskComplexity.COMPLEX)

    # 使用對應模型
    from app.connectors.claude import ClaudeConnector

    # 創建不同複雜度的連接器
    simple_connector = ClaudeConnector(model=simple_model)
    medium_connector = ClaudeConnector(model=medium_model)
    complex_connector = ClaudeConnector(model=complex_model)
```

---

## 📋 任務複雜度映射表

### Scout Agent（偵察兵）
| 方法 | 複雜度 | 模型 |
|------|-------|------|
| `match_competitor()` | SIMPLE | Haiku |
| `analyze_price_changes()` | MEDIUM | Opus |
| `generate_insights()` | COMPLEX | Opus |

### Pricer Agent（定價師）
| 方法 | 複雜度 | 模型 |
|------|-------|------|
| `calculate_optimal_price()` | MEDIUM | Opus |
| `generate_proposal()` | MEDIUM | Opus |
| `analyze_profit_margin()` | SIMPLE | Haiku |

### Writer Agent（文案官）
| 方法 | 複雜度 | 模型 |
|------|-------|------|
| `generate_title()` | MEDIUM | Opus |
| `generate_description()` | MEDIUM | Opus |
| `extract_keywords()` | SIMPLE | Haiku |
| `generate_full_content()` | COMPLEX | Opus |

### Strategist Agent（軍師）
| 方法 | 複雜度 | 模型 |
|------|-------|------|
| `generate_daily_briefing()` | COMPLEX | Opus |
| `analyze_market_trends()` | COMPLEX | Opus |
| `identify_opportunities()` | MEDIUM | Opus |

---

## 🚀 部署步驟

### 1. 更新代碼

```bash
cd backend
git pull origin main
```

### 2. 設定環境變數（Zeabur）

1. 登入 Zeabur Dashboard
2. 選擇 GoGoJap Backend 服務
3. Settings → Environment Variables
4. 添加以下變數：

```bash
AI_BASE_URL=https://your-relay-api.com/v1
AI_API_KEY=sk-xxxxxxxxxxxxxxxx
AI_MODEL_SIMPLE=claude-haiku-4-5-20251001-thinking
AI_MODEL_MEDIUM=claude-opus-4-6-thinking
AI_MODEL_COMPLEX=claude-opus-4-6-thinking
```

### 3. 重啟服務

Zeabur 會自動重新部署。

### 4. 驗證配置

```bash
# 測試 API 連接
curl -X POST https://ggj-back.zeabur.app/api/v1/ai/test \
  -H "Authorization: Bearer <your-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"complexity": "simple"}'

# 應返回使用的模型名稱
{
  "model": "claude-haiku-4-5-20251001-thinking",
  "complexity": "simple",
  "status": "ok"
}
```

---

## 📈 監控與優化

### 成本監控

建議添加日誌記錄每次 AI 調用：
- 使用的模型
- 消耗的 tokens
- 任務類型
- 執行時間

### 優化建議

1. **定期審查任務分類**
   - 檢查是否有任務被過度分級
   - 調整複雜度閾值

2. **A/B 測試**
   - 對比不同模型的輸出質量
   - 找出性價比最高的配置

3. **批次處理**
   - 合併多個簡單任務
   - 減少 API 調用次數

---

## 🔍 故障排除

### 模型不存在錯誤

**症狀**：
```
Error: Model 'claude-haiku-4-5-20251001-thinking' not found
```

**解決**：
1. 確認中轉 API 支持該模型
2. 檢查模型 ID 是否正確
3. 聯繫中轉 API 提供商

### Base URL 無效

**症狀**：
```
Error: Connection refused to https://your-relay-api.com/v1
```

**解決**：
1. 確認 Base URL 格式正確（需包含 `/v1`）
2. 測試 API 端點是否可訪問
3. 檢查防火牆設置

### API Key 無效

**症狀**：
```
Error: 401 Unauthorized
```

**解決**：
1. 確認 API Key 正確複製
2. 檢查 Key 是否過期
3. 聯繫中轉 API 提供商重新生成

---

## 🎯 總結

### 推薦配置

**小規模（< 300 SKU）**：
- 全部使用 Haiku（最經濟）
- 月成本：~¥3/月

**中規模（300-1000 SKU）**：
- 使用本文的分級策略
- 月成本：~¥6-15/月

**大規模（> 1000 SKU）**：
- 分級策略 + Prompt Caching
- 月成本：~¥20-50/月

### 下一步

1. ✅ 設定環境變數
2. ✅ 部署並測試
3. 📊 監控成本和性能
4. 🔧 根據實際情況調整

---

## 📚 參考資料

- [Claude API 官方文檔](https://docs.anthropic.com/claude/reference)
- [中轉 API 使用指南](./CLAUDE-OAUTH-SETUP.md)
- [成本優化最佳實踐](./COST-OPTIMIZATION.md)
