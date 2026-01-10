---
name: testing-patterns
description: Testing patterns for GoGoJap project. Use when writing tests, creating mocks, or following TDD workflow.
---

# Testing Patterns

## 項目測試架構

### Frontend (Next.js + React)
- 使用 Jest + React Testing Library
- 測試文件放在 `__tests__` 目錄或使用 `.test.tsx` 後綴

### Backend (FastAPI + Python)
- 使用 pytest
- 測試文件放在 `tests/` 目錄

## Test Structure

### AAA Pattern (Arrange, Act, Assert)
```typescript
describe('ProductCard', () => {
  it('should display product name and price', () => {
    // Arrange
    const product = { name: '北海道毛蟹', price: 580 }

    // Act
    render(<ProductCard product={product} />)

    // Assert
    expect(screen.getByText('北海道毛蟹')).toBeInTheDocument()
    expect(screen.getByText('$580')).toBeInTheDocument()
  })
})
```

## Mocking Patterns

### Factory Functions
```typescript
// 建立 mock 數據工廠
function getMockProduct(overrides = {}) {
  return {
    id: 1,
    name: '測試商品',
    price: 100,
    sku: 'TEST-001',
    status: 'active',
    ...overrides
  }
}

// 使用
const expensiveProduct = getMockProduct({ price: 9999 })
```

### API Mocking
```typescript
// Mock API 調用
jest.mock('@/lib/api', () => ({
  api: {
    getProducts: jest.fn().mockResolvedValue({
      data: [getMockProduct()],
      total: 1
    })
  }
}))
```

## React Testing Library 最佳實踐

### 查詢優先級
1. `getByRole` - 最推薦，模擬用戶行為
2. `getByLabelText` - 表單元素
3. `getByText` - 一般文字
4. `getByTestId` - 最後手段

### 測試用戶互動
```typescript
import userEvent from '@testing-library/user-event'

it('should handle click', async () => {
  const user = userEvent.setup()
  const onClick = jest.fn()

  render(<Button onClick={onClick}>點擊</Button>)
  await user.click(screen.getByRole('button'))

  expect(onClick).toHaveBeenCalledTimes(1)
})
```

## Python/Pytest Patterns

### Fixtures
```python
@pytest.fixture
def mock_product():
    return {
        "id": 1,
        "name": "測試商品",
        "price": 100,
        "sku": "TEST-001"
    }

def test_create_product(mock_product):
    result = create_product(mock_product)
    assert result.name == "測試商品"
```

### Async Tests
```python
@pytest.mark.asyncio
async def test_fetch_competitors():
    result = await fetch_competitors()
    assert len(result) > 0
```

## 命名規範

- 測試文件：`component.test.tsx` 或 `test_module.py`
- 測試描述：使用中文清楚描述行為
- describe：描述被測試的組件/功能
- it/test：描述預期行為
