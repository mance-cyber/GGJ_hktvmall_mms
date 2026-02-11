# 批量競品匹配指南

## 概述

為所有 GoGoJap 商品批量搜索 HKTVmall 競品，建立競爭對手監測體系。

---

## 🎯 功能

- ✅ 自動搜索 HKTVmall 上的競爭商品
- ✅ AI 智能判斷是否為同級商品
- ✅ 自動建立商品-競品映射關係
- ✅ 支持按分類篩選處理
- ✅ 支持測試模式（dry-run）

---

## 🚀 執行方法

### 方法 1: 本地執行腳本（推薦）

```bash
cd backend

# 1. 先查看統計信息
python scripts/batch_match_competitors.py --stats

# 2. 測試模式（不實際執行）
python scripts/batch_match_competitors.py --limit 10 --dry-run

# 3. 正式執行（小批量測試）
python scripts/batch_match_competitors.py --limit 10

# 4. 批量處理
python scripts/batch_match_competitors.py --limit 50

# 5. 按分類處理
python scripts/batch_match_competitors.py --limit 20 --category-main "鮮魚"
```

---

### 方法 2: 在 Zeabur 上執行

#### Step 1: SSH 進入容器

```bash
# 在 Zeabur Dashboard 找到 Backend 服務的 SSH 按鈕
# 或使用 Zeabur CLI
zeabur service connect <service-id>
```

#### Step 2: 執行腳本

```bash
cd /app

# 查看統計
python scripts/batch_match_competitors.py --stats

# 執行批量匹配
python scripts/batch_match_competitors.py --limit 50
```

---

### 方法 3: 通過 Celery 任務

```python
# 在 Python shell 中
from app.tasks.agent_tasks import batch_find_competitors

# 執行任務
result = batch_find_competitors.delay(limit=50)

# 查看結果
print(result.get())
```

---

## 📊 參數說明

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `--limit` | int | 50 | 一次處理多少個商品（最多 100） |
| `--category-main` | str | 無 | 篩選大分類（例如：鮮魚、貝類） |
| `--category-sub` | str | 無 | 篩選小分類 |
| `--dry-run` | flag | False | 測試模式（只顯示待處理商品，不實際執行） |
| `--stats` | flag | False | 顯示統計信息 |

---

## 💰 成本估算

### API 消耗

每個商品的處理流程：

1. **搜索階段**
   - Firecrawl 搜索 HKTVmall: 1 次
   - 提取搜索結果中的商品 URL

2. **抓取階段**
   - Firecrawl 抓取候選商品: 3-5 次
   - 獲取商品詳細信息

3. **匹配階段**
   - Claude API 判斷是否匹配: 3-5 次
   - 每次約 500-1000 tokens

### 估算成本（50 個商品）

**Firecrawl**:
- 50 次搜索 + 150-250 次抓取 = 200-300 次調用
- 成本取決於 Firecrawl 定價方案

**Claude API**（使用中轉 API ¥4/¥20）:
- 150-250 次判斷 × 750 tokens = 112k-187k tokens
- Input: 67k-112k × ¥4/M = ¥0.27-0.45
- Output: 45k-75k × ¥20/M = ¥0.90-1.50
- **總計: 約 ¥1.2-2.0**

### 月度成本（300 商品）

- Firecrawl: 1200-1800 次調用
- Claude: 約 ¥7-12/月
- **總計: 取決於 Firecrawl 方案 + ¥7-12**

---

## 🎯 執行策略

### 分批執行（推薦）

```bash
# Day 1: 測試 10 個商品
python scripts/batch_match_competitors.py --limit 10

# 檢查結果，確認無誤

# Day 2-5: 每天處理 50 個
python scripts/batch_match_competitors.py --limit 50

# 重複執行，直到所有商品處理完成
```

### 按分類逐步處理

```bash
# 先處理高價值分類
python scripts/batch_match_competitors.py --limit 30 --category-main "鮮魚"
python scripts/batch_match_competitors.py --limit 30 --category-main "貝類"
python scripts/batch_match_competitors.py --limit 30 --category-main "蟹類"

# 再處理其他分類
python scripts/batch_match_competitors.py --limit 50
```

---

## 📈 監控進度

### 查看統計信息

```bash
python scripts/batch_match_competitors.py --stats
```

**輸出範例**：
```
====================================
📊 競品匹配統計
====================================
總商品數: 300
已匹配: 50 (16.7%)
待處理: 250 (83.3%)
====================================
```

### 查看數據庫

```sql
-- 查看已匹配的商品數
SELECT COUNT(DISTINCT product_id) FROM product_competitor_mappings;

-- 查看競品總數
SELECT COUNT(*) FROM competitor_products;

-- 查看各分類的匹配情況
SELECT
    p.category_main,
    COUNT(DISTINCT p.id) as total_products,
    COUNT(DISTINCT pcm.product_id) as matched_products
FROM products p
LEFT JOIN product_competitor_mappings pcm ON p.id = pcm.product_id
WHERE p.source = 'gogojap_csv'
GROUP BY p.category_main;
```

---

## 🔧 故障排除

### 問題 1: Firecrawl API 額度不足

**症狀**：
```
Error: Firecrawl API quota exceeded
```

**解決**：
1. 檢查 Firecrawl 帳戶餘額
2. 升級 Firecrawl 方案
3. 減少 `--limit` 參數，分多次執行

---

### 問題 2: Claude API 連接失敗

**症狀**：
```
Error: Unable to connect to Claude API
```

**解決**：
1. 確認環境變數 `AI_BASE_URL` 和 `AI_API_KEY` 設置正確
2. 測試 API 連接：
   ```bash
   curl https://ggj-back.zeabur.app/api/v1/ai/test-env-config
   ```
3. 如果 AI API 不可用，系統會使用啟發式匹配（基於名稱相似度）

---

### 問題 3: 沒有找到待處理商品

**症狀**：
```
❌ 沒有待處理的商品
```

**原因**：
- 所有商品都已有競品映射
- 或者篩選條件太嚴格

**解決**：
1. 執行 `--stats` 查看統計
2. 移除 `--category-main` 和 `--category-sub` 篩選
3. 如果需要重新匹配，先刪除舊的映射：
   ```sql
   DELETE FROM product_competitor_mappings WHERE product_id = '<product_id>';
   ```

---

### 問題 4: 執行超時

**症狀**：
```
Error: Task timeout after 5 minutes
```

**解決**：
1. 減少 `--limit` 參數（例如從 50 降到 20）
2. 分多次執行
3. 檢查網絡連接速度

---

## 🔄 自動化維護

### Agent Team 自動化

啟用 **Scout Agent** 後，系統會自動：

1. ✅ 新商品上架時自動搜索競品
2. ✅ 每日定時分析競品動態
3. ✅ 競品降價時自動告警

**啟用方法**：
```bash
curl -X POST https://ggj-back.zeabur.app/api/v1/agent-team/scout/enable
```

### 定期批量掃描

建議每週執行一次批量掃描：

```bash
# 每週日執行
python scripts/batch_match_competitors.py --limit 50
```

---

## 📋 執行清單

初次設置完整流程：

- [ ] 1. 查看統計信息 (`--stats`)
- [ ] 2. 測試模式執行 10 個商品 (`--limit 10 --dry-run`)
- [ ] 3. 正式執行 10 個商品 (`--limit 10`)
- [ ] 4. 檢查結果和成本
- [ ] 5. 批量處理 50 個商品 (`--limit 50`)
- [ ] 6. 按分類逐步處理剩餘商品
- [ ] 7. 啟用 Scout Agent 自動維護
- [ ] 8. 設置每週定期掃描

---

## 🎯 最佳實踐

### 1. 優先處理高價值商品

```bash
# 先處理主力商品分類
python scripts/batch_match_competitors.py --limit 30 --category-main "鮮魚"
```

### 2. 定期檢查覆蓋率

```bash
# 每週檢查一次
python scripts/batch_match_competitors.py --stats
```

### 3. 持續優化匹配規則

- 檢查匹配結果的準確性
- 調整 AI 判斷的信心度閾值（目前是 0.6）
- 優化搜索關鍵詞策略

### 4. 監控 API 成本

- 記錄每次執行的成本
- 評估 ROI（投資回報率）
- 根據預算調整執行頻率

---

## 🔗 相關文檔

- [GPT-Best API 配置](./GPT-BEST-CONFIG.md)
- [多模型分級策略](./MULTI-MODEL-STRATEGY.md)
- [Agent Team 架構](./AGENT-TEAM-ARCHITECTURE.md)
- [競品監測系統](./COMPETITOR-MONITORING.md)

---

## 📞 技術支持

遇到問題？

1. 查看 Zeabur 日誌
2. 檢查 API 配置
3. 參考故障排除章節
4. 聯繫技術支持
