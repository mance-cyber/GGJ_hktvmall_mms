# Mock Data Injection Plan for AI Testing

## Objective
Enable user to inject custom mock data via a JSON file to test AI assistant responses, without affecting production systems. The solution must be fully reversible (delete file = restore default behavior).

---

## Current State Analysis

### Existing Infrastructure
- **Mock Connector**: `backend/app/connectors/hktv/mock.py` - Already implements `MockHKTVConnector`
- **Interface**: `backend/app/connectors/hktv/interface.py` - Defines `HKTVProduct` and `HKTVOrder` dataclasses
- **Config Switch**: `backend/app/config.py` line 39: `hktv_connector_type: str = Field(default="mock", ...)`
- **Current Behavior**: Mock connector generates random data on each instantiation

### Problem
Current mock data is randomly generated - user cannot control specific test scenarios.

---

## Implementation Tasks

### Task 1: Create Mock Data JSON Template
**File**: `backend/test_data/mock_data.example.json`

```json
{
  "_meta": {
    "description": "AI 測試用模擬數據 - 刪除此文件即恢復默認行為",
    "version": "1.0",
    "created_at": "2025-01-08"
  },
  "products": [
    {
      "product_id": "PROD-TEST-001",
      "sku": "SKU-TEST-001",
      "name": "日本高級抹茶粉 100g",
      "price": 128.00,
      "stock": 50,
      "status": "active",
      "images": ["https://example.com/matcha.jpg"],
      "attributes": {
        "category": "食品",
        "origin": "日本京都",
        "weight": "100g"
      }
    },
    {
      "product_id": "PROD-TEST-002",
      "sku": "SKU-TEST-002",
      "name": "韓國護膚套裝 (限量版)",
      "price": 388.00,
      "stock": 0,
      "status": "active",
      "images": ["https://example.com/skincare.jpg"],
      "attributes": {
        "category": "美妝",
        "brand": "Innisfree",
        "note": "庫存為零 - 用於測試缺貨提示"
      }
    },
    {
      "product_id": "PROD-TEST-003",
      "sku": "SKU-TEST-003",
      "name": "測試價格異常商品",
      "price": 0.01,
      "stock": 999,
      "status": "active",
      "images": [],
      "attributes": {
        "category": "測試",
        "note": "異常低價 - 用於測試價格警報"
      }
    }
  ],
  "orders": [
    {
      "order_id": "ORD-TEST-000001",
      "order_number": "HK20250108TEST001",
      "status": "pending",
      "total_amount": 516.00,
      "items": [
        {
          "sku": "SKU-TEST-001",
          "name": "日本高級抹茶粉 100g",
          "quantity": 2,
          "unit_price": 128.00
        },
        {
          "sku": "SKU-TEST-002",
          "name": "韓國護膚套裝 (限量版)",
          "quantity": 1,
          "unit_price": 260.00
        }
      ],
      "customer_info": {
        "name": "測試客戶 A",
        "phone": "91234567",
        "email": "test_a@example.com"
      },
      "shipping_info": {
        "address": "香港九龍測試街 1 號",
        "method": "順豐"
      },
      "order_date": "2025-01-08T10:30:00"
    },
    {
      "order_id": "ORD-TEST-000002",
      "order_number": "HK20250107TEST002",
      "status": "shipped",
      "total_amount": 888.00,
      "items": [
        {
          "sku": "SKU-TEST-001",
          "name": "日本高級抹茶粉 100g",
          "quantity": 5,
          "unit_price": 128.00
        }
      ],
      "customer_info": {
        "name": "VIP 客戶",
        "phone": "98765432",
        "email": "vip@example.com"
      },
      "shipping_info": {
        "address": "香港中環金融街 88 號",
        "method": "送貨上門"
      },
      "order_date": "2025-01-07T15:45:00"
    }
  ]
}
```

---

### Task 2: Modify MockHKTVConnector
**File**: `backend/app/connectors/hktv/mock.py`

**Changes Required**:

1. Add imports at top:
```python
import json
from pathlib import Path
```

2. Add helper method to load JSON data:
```python
def _load_mock_data_from_file(self) -> tuple[list, list] | None:
    """嘗試從 JSON 文件加載測試數據"""
    # 優先檢查 backend/test_data/mock_data.json
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "test_data" / "mock_data.json",
        Path(__file__).parent.parent.parent.parent / "mock_data.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                products = [
                    HKTVProduct(**p) for p in data.get("products", [])
                ]
                orders = [
                    HKTVOrder(**o) for o in data.get("orders", [])
                ]
                print(f"[MockHKTVConnector] 已從 {path} 加載測試數據: {len(products)} 商品, {len(orders)} 訂單")
                return products, orders
            except Exception as e:
                print(f"[MockHKTVConnector] 加載測試數據失敗: {e}")
    
    return None
```

3. Modify `__init__` method to try file loading first:
```python
def __init__(self):
    # 優先嘗試從文件加載
    loaded = self._load_mock_data_from_file()
    
    if loaded:
        self._products, self._orders = loaded
    else:
        # 回退到隨機生成（原有邏輯）
        self._products = [
            # ... existing random generation code ...
        ]
        self._orders = [
            # ... existing random generation code ...
        ]
```

---

### Task 3: Create Test Data Directory
```bash
mkdir -p backend/test_data
```

Copy the example file:
```bash
cp backend/test_data/mock_data.example.json backend/test_data/mock_data.json
```

---

### Task 4: Add to .gitignore
**File**: `.gitignore` (create if not exists)

Add:
```
# Test mock data (user-specific, should not be committed)
backend/test_data/mock_data.json
```

Keep the example file tracked:
```
# But keep the example
!backend/test_data/mock_data.example.json
```

---

### Task 5: Verification

After implementation, verify with:

```bash
# Start the backend server
cd backend && python -m uvicorn app.main:app --reload

# In another terminal, call the agent API or use the frontend
# The console should show:
# [MockHKTVConnector] 已從 .../mock_data.json 加載測試數據: 3 商品, 2 訂單
```

---

## Cleanup Instructions (For User)

When testing is complete:
```bash
# Simply delete the mock data file
rm backend/test_data/mock_data.json

# Restart server - it will auto-fallback to random data
```

---

## File Change Summary

| File | Action | Purpose |
|------|--------|---------|
| `backend/test_data/mock_data.example.json` | CREATE | Template for users |
| `backend/test_data/mock_data.json` | CREATE | Active test data (gitignored) |
| `backend/app/connectors/hktv/mock.py` | MODIFY | Add file-loading logic |
| `.gitignore` | MODIFY | Ignore user's mock_data.json |

---

## Success Criteria

1. When `mock_data.json` exists: AI uses data from file
2. When `mock_data.json` is deleted: AI falls back to random data
3. No database or production data is affected
4. Console log confirms which data source is being used
