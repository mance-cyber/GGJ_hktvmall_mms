# Project Context

## Purpose
GoGoJap 是一個 AI 驅動的電商運營平台，專為香港 HKTVmall 賣家設計。核心目標是通過競品監測、智能定價、AI 文案生成等功能，幫助賣家提升銷售效率和利潤率。

**商業模式**: Result-as-a-Service (RaaS) — 賣「結果」而非「工具」

## Tech Stack

### Backend
- Python 3.11+
- FastAPI 0.109
- SQLAlchemy 2.0 (Async)
- PostgreSQL 14+ (Neon)
- Celery 5.3 + Redis
- Alembic (遷移)

### Frontend
- Next.js 14 (App Router)
- React 18
- TypeScript
- TanStack Query 5
- shadcn/ui + Radix UI
- Tailwind CSS
- Recharts

### AI/ML
- Anthropic Claude API (文案生成)
- Firecrawl (網頁抓取)
- Clawdbot (瀏覽器自動化)

### Infrastructure
- Cloudflare Pages (前端)
- Zeabur (後端)
- Cloudflare R2 (文件存儲)
- Redis (緩存 + 隊列)

## Project Conventions

### Code Style
- **語言**: 代碼使用英文命名，註釋/文檔使用中文
- **後端**: Black + isort 格式化，Type hints 必須
- **前端**: ESLint + Prettier，嚴格 TypeScript
- **縮進**: 4 spaces (Python), 2 spaces (TS/TSX)

### Architecture Patterns
- **後端**: 分層架構 (Router → Service → Model)
- **前端**: Feature-based 目錄結構
- **API**: RESTful，FastAPI 自動生成 OpenAPI
- **狀態管理**: Server state 用 TanStack Query，Client state 用 React Context

### Testing Strategy
- **後端**: pytest + pytest-asyncio
- **前端**: Vitest + React Testing Library
- **E2E**: Playwright (規劃中)
- **覆蓋率目標**: 80%+

### Git Workflow
- **主分支**: main
- **提交格式**: `type: description` (feat/fix/docs/refactor/test)
- **PR 要求**: 需要 Code Review
- **禁止**: Force push to main

## Domain Context

### HKTVmall 電商平台
- 香港最大網上超市之一
- 提供 MMS (Merchant Management System) API
- 佣金模式：按銷售額收取

### 核心業務流程
1. **競品監測**: 抓取競爭對手價格 → 生成告警
2. **智能定價**: AI 分析市場 → 生成改價提案 → 人工審批 → 執行
3. **AI 文案**: 輸入商品信息 → Claude 生成描述 → 人工微調 → 上架
4. **SEO 優化**: 監測 Ranking → 生成優化建議

### 關鍵數據模型
- `products` — 自家商品
- `competitor_products` — 競品商品
- `price_proposals` — AI 改價提案
- `price_alerts` — 價格異動告警
- `settlements` — HKTVmall 結算單

## Important Constraints

### Technical
- HKTVmall API Rate Limit
- Firecrawl 月度配額限制
- PostgreSQL 連接池上限

### Business
- Human-in-the-Loop：改價必須人工審批
- 最低售價保護：不能低於成本 + 5%
- 合規：不能抓取需要登錄的頁面

### Security
- API Keys 必須通過環境變量
- 敏感數據加密存儲
- Google OAuth 白名單認證

## External Dependencies

| 服務 | 用途 | 文檔 |
|-----|------|------|
| HKTVmall MMS API | 商品/訂單同步 | 內部文檔 |
| Anthropic Claude | AI 文案生成 | docs.anthropic.com |
| Firecrawl | 網頁抓取 | firecrawl.dev |
| Neon | PostgreSQL 託管 | neon.tech |
| Zeabur | 後端部署 | zeabur.com |
| Cloudflare | CDN + R2 存儲 | cloudflare.com |
