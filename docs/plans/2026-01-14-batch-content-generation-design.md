# AI 文案批量生成功能设计

> 创建日期：2026-01-14
> 状态：已实现

---

## 一、需求概述

在现有 AI 文案生成功能基础上，新增批量生成能力：

1. **两种输入方式**：从商品列表选择 / CSV 文件导入
2. **智能处理模式**：≤10 个即时等待，>10 个后台异步
3. **结果管理**：逐个检视编辑 + 批量导出 CSV
4. **存储策略**：只保存生成结果，不追踪批量任务本身

---

## 二、系统架构

```
┌─────────────────┐     ┌─────────────────┐
│  商品列表选择    │     │  CSV/Excel 导入  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌─────────────────────────┐
         │     批量生成引擎         │
         │  ≤10个：同步即时返回     │
         │  >10个：异步后台处理     │
         │  并发控制：最多 3 个请求  │
         └──────────┬──────────────┘
                    ▼
         ┌─────────────────────────┐
         │     结果管理界面         │
         │  • 列表展示生成状态      │
         │  • 单品详情/对话优化     │
         │  • 批量导出 CSV         │
         └─────────────────────────┘
```

---

## 三、前端设计

### 3.1 页面结构

在现有 `/ai-content` 页面新增「批量生成」Tab：

| Tab | 功能 |
|-----|------|
| 生成文案 | 现有单品生成（保持不变） |
| **批量生成** | 新功能入口 |
| 历史记录 | 现有历史（保持不变） |

### 3.2 批量生成 Tab 布局

```
┌─────────────────────────────────────────────────────┐
│  [商品选择] [文件导入]  ← 切换按钮                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   输入区             │  │   配置区             │  │
│  │   商品列表/文件上传   │  │   类型、风格、语言    │  │
│  └─────────────────────┘  └─────────────────────┘  │
│                                                     │
│  [开始批量生成] 按钮                                 │
│                                                     │
├─────────────────────────────────────────────────────┤
│  结果区                                             │
│  ┌────┬────────┬──────┬────────┬─────┐            │
│  │状态│商品名称 │ 标题  │ 操作    │     │  [导出CSV] │
│  ├────┼────────┼──────┼────────┼─────┤            │
│  │ ✓  │商品A   │标题A │查看/编辑│     │            │
│  │ ✓  │商品B   │标题B │查看/编辑│     │            │
│  │ ⏳ │商品C   │ --   │ --     │     │            │
│  └────┴────────┴──────┴────────┴─────┘            │
└─────────────────────────────────────────────────────┘
```

### 3.3 商品选择模块

| 功能 | 说明 |
|-----|------|
| 搜索筛选 | 按名称、品牌、分类筛选 |
| 多选操作 | Checkbox 勾选 + 全选/取消全选 |
| 已选预览 | 显示已选数量，可移除单个 |
| 上限控制 | 单次最多 100 个，超出提示 |

### 3.4 文件导入模块

| 功能 | 说明 |
|-----|------|
| 模板下载 | 提供 CSV 模板下载按钮 |
| 文件上传 | 支持 .csv, .xlsx 格式 |
| 预览校验 | 解析后展示预览表格，标记错误行 |
| 错误处理 | 必填字段缺失时高亮提示 |

**CSV 模板字段：**

| 字段 | 必填 | 说明 |
|-----|------|------|
| name | ✓ | 商品名称 |
| brand | | 品牌 |
| features | | 特点（逗号分隔多个） |
| target_audience | | 目标受众 |
| price | | 价格 |
| category | | 分类 |

### 3.5 结果管理

| 功能 | 说明 |
|-----|------|
| 状态显示 | ⏳ 生成中 / ✓ 成功 / ✗ 失败 |
| 进度条 | 异步模式显示整体进度 |
| 单品操作 | 点击查看详情，可进入对话优化 |
| 批量导出 | CSV 格式导出所有成功结果 |

---

## 四、后端 API 设计

### 4.1 批量生成 API（改造现有）

```
POST /api/v1/content/batch-generate
```

**请求体：**
```json
{
  "items": [
    {
      "product_id": "uuid",           // 方式一：从商品库选择
      "product_info": null
    },
    {
      "product_id": null,
      "product_info": {               // 方式二：手动输入/CSV导入
        "name": "商品名称",
        "brand": "品牌",
        "features": ["特点1", "特点2"],
        "target_audience": "目标受众",
        "price": "100",
        "category": "分类"
      }
    }
  ],
  "content_type": "full_copy",        // title / selling_points / description / full_copy
  "style": "professional",            // professional / casual / playful / formal
  "target_languages": ["TC"]          // TC / SC / EN
}
```

**响应（≤10 个，同步模式）：**
```json
{
  "mode": "sync",
  "results": [
    {
      "index": 0,
      "success": true,
      "content_id": "uuid",
      "product_name": "商品A",
      "content": {
        "title": "标题",
        "selling_points": ["卖点1", "卖点2"],
        "description": "描述内容"
      }
    },
    {
      "index": 1,
      "success": false,
      "product_name": "商品B",
      "error": "生成失败：AI 服务暂时不可用"
    }
  ],
  "summary": {
    "total": 2,
    "success": 1,
    "failed": 1
  }
}
```

**响应（>10 个，异步模式）：**
```json
{
  "mode": "async",
  "task_id": "uuid",
  "total": 25,
  "message": "批量任务已提交，请通过任务ID查询进度"
}
```

### 4.2 任务进度查询 API（新增）

```
GET /api/v1/content/batch-generate/{task_id}/status
```

**响应：**
```json
{
  "task_id": "uuid",
  "status": "processing",             // pending / processing / completed / failed
  "progress": {
    "total": 25,
    "completed": 12,
    "failed": 1,
    "percent": 48
  },
  "results": [
    {
      "index": 0,
      "success": true,
      "content_id": "uuid",
      "product_name": "商品A",
      "content": { ... }
    }
  ]
}
```

### 4.3 批量导出 API（新增）

```
GET /api/v1/content/export?content_ids=uuid1,uuid2,...&format=csv
```

**响应：** 直接返回 CSV 文件流

**CSV 导出字段：**
- product_name：商品名称
- title：生成标题
- selling_points：卖点（换行分隔）
- description：描述
- status：状态
- generated_at：生成时间

### 4.4 CSV 模板下载 API（新增）

```
GET /api/v1/content/template/download
```

**响应：** 返回 CSV 模板文件

---

## 五、数据模型

### 5.1 异步任务缓存（Redis）

```python
# Key 格式
batch_task:{task_id}

# Value 结构
{
    "status": "processing",
    "total": 25,
    "completed": 12,
    "failed": 1,
    "items": [...],              # 原始请求项
    "config": {                  # 生成配置
        "content_type": "full_copy",
        "style": "professional",
        "target_languages": ["TC"]
    },
    "results": [...],            # 已完成结果
    "created_at": "2026-01-14T10:00:00Z"
}

# TTL: 24 小时
```

### 5.2 现有 AIContent 表（无需修改）

生成结果直接保存到现有 `ai_contents` 表，每个商品一条记录。

---

## 六、异步任务处理

### 6.1 处理流程

```
1. 接收批量请求
2. 判断数量
   ├─ ≤10：同步处理，直接返回结果
   └─ >10：创建异步任务
           ├─ 生成 task_id
           ├─ 保存任务信息到 Redis
           ├─ 启动后台协程处理
           └─ 立即返回 task_id
3. 后台处理（异步模式）
   ├─ 使用信号量控制并发（最多 3 个）
   ├─ 逐个调用 AI 生成
   ├─ 实时更新 Redis 进度
   └─ 全部完成后更新状态为 completed
```

### 6.2 并发控制

```python
# 使用 asyncio.Semaphore 限制并发
semaphore = asyncio.Semaphore(3)

async def generate_with_limit(item):
    async with semaphore:
        return await generate_single_content(item)
```

### 6.3 错误处理

- 单个商品生成失败不影响其他商品
- 失败结果记录错误原因
- 任务整体状态根据结果判断：
  - 全部成功：completed
  - 部分失败：completed（results 中标记失败项）
  - 全部失败：failed

---

## 七、实现计划

### 阶段一：后端核心（预计工作量：中）

1. **改造批量生成 API**
   - 新增 `BatchGenerateItem` schema
   - 实现同步/异步智能判断逻辑
   - 同步模式：循环调用现有 generate 逻辑

2. **新增异步任务处理**
   - Redis 任务状态管理
   - 后台协程处理器
   - 并发控制（Semaphore）

3. **新增进度查询 API**
   - 从 Redis 读取任务状态
   - 返回进度和已完成结果

4. **新增导出 API**
   - CSV 文件生成
   - 流式响应

5. **新增模板下载 API**
   - 返回预设 CSV 模板

### 阶段二：前端界面（预计工作量：中）

1. **新增批量生成 Tab**
   - Tab 切换逻辑
   - 输入方式切换（商品选择/文件导入）

2. **商品选择模块**
   - 商品列表加载（复用现有 API）
   - 搜索筛选
   - 多选逻辑

3. **文件导入模块**
   - 模板下载按钮
   - 文件上传组件
   - CSV/Excel 解析（前端 papaparse/xlsx）
   - 预览表格

4. **结果展示模块**
   - 结果列表/卡片
   - 进度条（异步模式）
   - 轮询进度更新
   - 单品详情弹窗
   - 导出按钮

### 阶段三：集成测试

1. 同步模式完整流程测试
2. 异步模式完整流程测试
3. 错误场景测试（部分失败、全部失败）
4. 导出功能测试

---

## 八、文件变更清单

### 后端

| 文件 | 变更类型 | 说明 |
|-----|---------|------|
| `backend/app/schemas/content.py` | 修改 | 新增批量生成相关 schema |
| `backend/app/api/v1/content.py` | 修改 | 改造 batch-generate，新增 status/export/template API |
| `backend/app/services/batch_content_service.py` | 新增 | 批量生成核心逻辑 |
| `backend/app/services/redis_service.py` | 新增/修改 | 任务状态管理 |

### 前端

| 文件 | 变更类型 | 说明 |
|-----|---------|------|
| `frontend/src/app/ai-content/page.tsx` | 修改 | 新增批量生成 Tab |
| `frontend/src/components/content/BatchContentGenerator.tsx` | 新增 | 批量生成主组件 |
| `frontend/src/components/content/ProductSelector.tsx` | 新增 | 商品选择组件 |
| `frontend/src/components/content/FileImporter.tsx` | 新增 | 文件导入组件 |
| `frontend/src/components/content/BatchResultList.tsx` | 新增 | 结果列表组件 |
| `frontend/src/lib/api.ts` | 修改 | 新增批量相关 API 调用 |

---

## 九、待确认事项

- [x] 即时/异步阈值：10 个
- [x] 单次上限：100 个
- [x] 并发控制：3 个
- [x] 任务缓存 TTL：24 小时
- [ ] 是否需要任务取消功能？（当前设计不包含）

---

## 十、风险与考量

1. **AI API 限流**：已通过并发控制（3个）缓解
2. **大批量耗时**：100 个商品预估 5-10 分钟，用户需有心理预期
3. **Redis 依赖**：异步模式依赖 Redis，需确保 Redis 服务稳定
