# Code Review Report: HKTVmall Scraping System

**Review Date:** 2026-01-28
**Reviewer:** Code Review Agent
**Base SHA:** 199b9c1 (feat: Firecrawl optimization)
**Head SHA:** 0ef2af1 (fix: Clawdbot build errors)

---

## Executive Summary

This review covers the newly implemented HKTVmall scraping and sync system, including the UnifiedScraper interface, Clawdbot WebSocket connector, API endpoints, and supporting scripts.

### Overall Assessment: **NEEDS ATTENTION**

| Category | Rating | Summary |
|----------|--------|---------|
| Security | **HIGH RISK** | Multiple SSRF vulnerabilities, insufficient input validation |
| Code Quality | **MEDIUM** | Good structure, but TypeScript types could be stricter |
| Architecture | **GOOD** | Clean separation, proper abstraction layers |
| Performance | **MEDIUM** | Missing timeout guards, potential memory issues |
| Documentation | **GOOD** | Well-commented code with clear purpose statements |

### Statistics
- **Critical Issues:** 4
- **High Issues:** 7
- **Medium Issues:** 8
- **Low Issues:** 5

---

## Critical Issues (Must Fix)

### CRIT-1: Server-Side Request Forgery (SSRF) Vulnerability

**File:** `frontend/src/app/api/v1/scrape/route.ts`
**Lines:** 91-102, 208-219

**Problem:**
The API accepts arbitrary URLs from user input without validation, allowing attackers to:
- Access internal network resources (localhost, 127.0.0.1, internal IPs)
- Probe cloud metadata endpoints (169.254.169.254)
- Scan internal infrastructure

```typescript
// Lines 91-102 - No URL validation
async function handleScrapeProduct(scraper: any, params: any) {
  const { url } = params;  // <-- User-controlled URL directly used

  if (!url) {
    return NextResponse.json(
      { success: false, error: '缺少 url 参数' },
      { status: 400 }
    );
  }

  console.log(`🛍️ 抓取商品: ${url}`);
  const result = await scraper.scrapeHKTVProduct(url);  // <-- Direct use
```

**Recommendation:**
```typescript
// Add URL validation helper
function validateScrapeUrl(url: string): { valid: boolean; error?: string } {
  try {
    const parsed = new URL(url);

    // Only allow HTTPS
    if (parsed.protocol !== 'https:') {
      return { valid: false, error: 'Only HTTPS URLs allowed' };
    }

    // Block internal IPs
    const blockedPatterns = [
      /^127\./,
      /^10\./,
      /^172\.(1[6-9]|2[0-9]|3[01])\./,
      /^192\.168\./,
      /^169\.254\./,
      /^localhost$/i,
      /^0\.0\.0\.0$/,
    ];

    if (blockedPatterns.some(p => p.test(parsed.hostname))) {
      return { valid: false, error: 'Internal addresses not allowed' };
    }

    // Whitelist allowed domains (HKTVmall specific)
    const allowedDomains = ['www.hktvmall.com', 'hktvmall.com'];
    if (!allowedDomains.includes(parsed.hostname)) {
      return { valid: false, error: 'Domain not in whitelist' };
    }

    return { valid: true };
  } catch {
    return { valid: false, error: 'Invalid URL format' };
  }
}
```

---

### CRIT-2: Missing Authentication on Scrape API

**File:** `frontend/src/app/api/v1/scrape/route.ts`
**Lines:** 15-84

**Problem:**
The scrape API has no authentication, allowing anyone to:
- Abuse the scraping infrastructure
- Generate costs (for Firecrawl)
- Perform denial-of-service attacks
- Use the server as a proxy for malicious activity

```typescript
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();  // <-- No auth check
    const { action, params } = body;
    // ... proceeds directly to scraping
```

**Recommendation:**
```typescript
import { getServerSession } from 'next-auth';

export async function POST(request: NextRequest) {
  // Authentication check
  const session = await getServerSession();
  if (!session) {
    return NextResponse.json(
      { success: false, error: 'Unauthorized' },
      { status: 401 }
    );
  }

  // Rate limiting per user
  const userRateLimit = await checkUserRateLimit(session.user.id);
  if (!userRateLimit.allowed) {
    return NextResponse.json(
      {
        success: false,
        error: 'Rate limit exceeded',
        retryAfter: userRateLimit.retryAfter
      },
      { status: 429 }
    );
  }

  // ... rest of handler
```

---

### CRIT-3: Unvalidated Array Size in Batch Scraping

**File:** `frontend/src/app/api/v1/scrape/route.ts`
**Lines:** 149-174

**Problem:**
No limit on the `urls` array size in batch scraping, enabling:
- Memory exhaustion attacks
- Extended server blocking
- Cost exploitation (Firecrawl billing)

```typescript
async function handleScrapeBatch(scraper: any, params: any) {
  const { urls } = params;

  if (!urls || !Array.isArray(urls)) {  // <-- Only checks if array, not size
    return NextResponse.json(
      { success: false, error: 'urls 必须是数组' },
      { status: 400 }
    );
  }

  console.log(`📦 批量抓取: ${urls.length} 个 URL`);  // Could be 10000+ URLs
  const results = await scraper.scrapeBatch(urls);  // <-- Processes all
```

**Recommendation:**
```typescript
const MAX_BATCH_SIZE = 50;  // Configure based on resources

async function handleScrapeBatch(scraper: any, params: any) {
  const { urls } = params;

  if (!urls || !Array.isArray(urls)) {
    return NextResponse.json(
      { success: false, error: 'urls 必须是数组' },
      { status: 400 }
    );
  }

  if (urls.length === 0) {
    return NextResponse.json(
      { success: false, error: 'urls 数组不能为空' },
      { status: 400 }
    );
  }

  if (urls.length > MAX_BATCH_SIZE) {
    return NextResponse.json(
      {
        success: false,
        error: `批量抓取最多支持 ${MAX_BATCH_SIZE} 个 URL`,
        maxAllowed: MAX_BATCH_SIZE,
        provided: urls.length
      },
      { status: 400 }
    );
  }

  // Validate each URL
  for (const url of urls) {
    const validation = validateScrapeUrl(url);
    if (!validation.valid) {
      return NextResponse.json(
        { success: false, error: `无效 URL: ${url} - ${validation.error}` },
        { status: 400 }
      );
    }
  }
```

---

### CRIT-4: API Key Exposure Risk in Client-Side Code

**File:** `frontend/src/lib/config/scraper.config.ts`
**Lines:** 43-49

**Problem:**
While the API key is read from environment variables, the config structure could accidentally expose keys if the config object is ever serialized or logged.

```typescript
production: {
  type: 'firecrawl',
  endpoint: process.env.FIRECRAWL_API_URL || 'https://api.firecrawl.dev/v1',
  apiKey: process.env.FIRECRAWL_API_KEY,  // <-- Stored in object
  timeout: 120000,
  retryAttempts: 5,
  rateLimitPerMinute: 60,
},
```

**File:** `frontend/src/lib/config/scraper.config.ts`
**Lines:** 129-140

```typescript
export function printScraperConfig(): void {
  const config = getScraperConfig();

  console.log('\n==================== 爬虫配置 ====================');
  // ...
  console.log(`API Key: ${config.apiKey ? '✅ 已配置' : '❌ 未配置'}`);
  // Safe here, but the config object itself contains the key
```

**Recommendation:**
```typescript
// Never store actual API key in config object
export interface ScraperConfig {
  type: ScraperType;
  endpoint: string;
  hasApiKey: boolean;  // Only store boolean
  timeout: number;
  retryAttempts: number;
  rateLimitPerMinute: number;
}

// Retrieve key only when needed, never cache
function getApiKey(): string {
  const key = process.env.FIRECRAWL_API_KEY;
  if (!key) {
    throw new Error('FIRECRAWL_API_KEY not configured');
  }
  return key;
}
```

---

## High Priority Issues (Should Fix)

### HIGH-1: Loose TypeScript Typing with `any`

**Files:**
- `frontend/src/app/api/v1/scrape/route.ts`: Lines 91, 120, 149, 179, 208
- `frontend/src/app/api/v1/scrape/clawdbot/route.ts`: Lines 69, 96, 123, 152

**Problem:**
Extensive use of `any` type defeats TypeScript's safety guarantees.

```typescript
async function handleScrapeProduct(scraper: any, params: any) {  // <-- any any
  const { url } = params;
```

**Recommendation:**
```typescript
import { UnifiedScraper, UnifiedScrapeResult } from '@/lib/connectors/unified-scraper';

interface ScrapeProductParams {
  url: string;
}

async function handleScrapeProduct(
  scraper: UnifiedScraper,
  params: ScrapeProductParams
): Promise<NextResponse<ApiResponse<UnifiedScrapeResult>>> {
  const { url } = params;
```

---

### HIGH-2: WebSocket Connection Not Properly Cleaned Up

**File:** `frontend/src/lib/connectors/clawdbot-connector.ts`
**Lines:** 83-123

**Problem:**
WebSocket connection timeout doesn't clean up the partially connected socket, leading to potential resource leaks.

```typescript
async connect(): Promise<void> {
  // ...
  setTimeout(() => {
    if (!this.connected) {
      reject(new Error('Clawdbot 連接超時'));
      // <-- WebSocket still exists but in limbo state
    }
  }, 10000);
```

**Recommendation:**
```typescript
async connect(): Promise<void> {
  if (this.connected && this.ws?.readyState === WebSocket.OPEN) {
    return;
  }

  return new Promise((resolve, reject) => {
    try {
      this.ws = new WebSocket(this.config.gatewayUrl);

      const timeout = setTimeout(() => {
        if (!this.connected) {
          // Clean up the socket
          if (this.ws) {
            this.ws.removeAllListeners();
            this.ws.terminate();  // Force close
            this.ws = null;
          }
          reject(new Error('Clawdbot 連接超時'));
        }
      }, 10000);

      this.ws.on('open', () => {
        clearTimeout(timeout);
        console.log('✅ 已連接到 Clawdbot Gateway');
        this.connected = true;
        resolve();
      });

      this.ws.on('error', (error) => {
        clearTimeout(timeout);
        this.cleanup();
        reject(error);
      });
```

---

### HIGH-3: Task Queue Memory Leak

**File:** `frontend/src/lib/connectors/clawdbot-connector.ts`
**Lines:** 64, 194-212

**Problem:**
If a task times out, it's removed from the queue, but if the WebSocket later receives a response for that task (delayed response), there's no handling. More critically, if the WebSocket disconnects mid-task, pending tasks are never cleaned up.

```typescript
private taskQueue: Map<string, (result: ScrapeResult) => void> = new Map();

// In scrape():
this.taskQueue.set(task.id, (result: ScrapeResult) => {
  clearTimeout(timeout);
  resolve(result);
});

// If connection drops, these callbacks are never resolved or rejected
```

**Recommendation:**
```typescript
// Add cleanup on disconnect
private cleanup(): void {
  // Reject all pending tasks
  for (const [taskId, resolver] of this.taskQueue.entries()) {
    // Can't call resolver with error, need different approach
  }
  this.taskQueue.clear();

  if (this.ws) {
    this.ws.close();
    this.ws = null;
  }
  this.connected = false;
}

// Better task tracking with reject capability
interface PendingTask {
  resolve: (result: ScrapeResult) => void;
  reject: (error: Error) => void;
  timeout: NodeJS.Timeout;
}

private taskQueue: Map<string, PendingTask> = new Map();
```

---

### HIGH-4: No Request Deduplication

**File:** `frontend/src/lib/connectors/unified-scraper.ts`
**Lines:** 251-279

**Problem:**
Batch scraping doesn't deduplicate URLs, allowing wasted resources on duplicate requests.

```typescript
async scrapeBatch(urls: string[]): Promise<UnifiedScrapeResult[]> {
  const results: UnifiedScrapeResult[] = [];

  for (const url of urls) {  // <-- No deduplication
    // Same URL could be scraped multiple times
```

**Recommendation:**
```typescript
async scrapeBatch(urls: string[]): Promise<UnifiedScrapeResult[]> {
  // Deduplicate URLs
  const uniqueUrls = [...new Set(urls)];
  const results: Map<string, UnifiedScrapeResult> = new Map();

  for (const url of uniqueUrls) {
    try {
      const result = await this.scrape({ url });
      results.set(url, result);
      await this.randomDelay(1000, 3000);
    } catch (error) {
      // ...error handling
    }
  }

  // Return results in original order, including duplicates
  return urls.map(url => results.get(url)!);
}
```

---

### HIGH-5: Synchronous JSON.parse Without Error Boundary

**File:** `frontend/src/lib/connectors/clawdbot-connector.ts`
**Lines:** 139-153

**Problem:**
If the WebSocket receives malformed JSON, the error is logged but the connection continues, potentially in an inconsistent state.

```typescript
private handleMessage(message: string): void {
  try {
    const response = JSON.parse(message);  // <-- Could fail

    if (response.type === 'task_result') {
      const resolver = this.taskQueue.get(response.taskId);
      if (resolver) {
        resolver(response.result);
        this.taskQueue.delete(response.taskId);
      }
    }
  } catch (error) {
    console.error('解析 Clawdbot 消息失敗:', error);
    // <-- Connection continues in unknown state
  }
}
```

**Recommendation:**
```typescript
private handleMessage(message: string): void {
  let response: ClawdbotMessage;

  try {
    response = JSON.parse(message);
  } catch (error) {
    console.error('解析 Clawdbot 消息失敗:', error);
    console.error('原始消息:', message.substring(0, 200));
    // Don't proceed with corrupted data
    return;
  }

  // Validate message structure
  if (!response || typeof response !== 'object') {
    console.error('無效的消息格式:', response);
    return;
  }

  if (response.type === 'task_result') {
    if (!response.taskId || !response.result) {
      console.error('task_result 缺少必要字段');
      return;
    }
    // ... handle valid message
  }
}
```

---

### HIGH-6: Deprecated `substr` Method Usage

**Files:**
- `frontend/src/lib/connectors/unified-scraper.ts`: Lines 165, 225
- `frontend/src/lib/connectors/clawdbot-connector.ts`: Lines 337
- `frontend/src/app/api/v1/scrape/clawdbot/route.ts`: Lines 164

**Problem:**
`String.prototype.substr()` is deprecated.

```typescript
return `firecrawl_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
//                                                          ^^^^^^ deprecated
```

**Recommendation:**
```typescript
// Use substring instead
return `firecrawl_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;

// Or use crypto for better randomness
import { randomUUID } from 'crypto';
return `firecrawl_${Date.now()}_${randomUUID().split('-')[0]}`;
```

---

### HIGH-7: Script Import Path Issues

**File:** `scripts/scrape-and-sync.ts`
**Lines:** 5

**Problem:**
Import path assumes specific directory structure that may not work with ts-node execution.

```typescript
import { getUnifiedScraper } from '../lib/connectors/unified-scraper';
// This relative path assumes scripts/ is at same level as lib/
```

**Recommendation:**
```typescript
// Use path aliases configured in tsconfig
import { getUnifiedScraper } from '@/lib/connectors/unified-scraper';

// Or use absolute paths with proper tsconfig configuration
// tsconfig.json:
// {
//   "compilerOptions": {
//     "baseUrl": ".",
//     "paths": {
//       "@/*": ["frontend/src/*"]
//     }
//   }
// }
```

---

## Medium Priority Issues (Consider Fixing)

### MED-1: Console Logging in Production Code

**Files:** Multiple files

**Problem:**
Extensive console.log/console.error usage should use a proper logging framework with levels.

**Recommendation:**
Implement a logger service with configurable levels (debug/info/warn/error) that can be adjusted per environment.

---

### MED-2: Magic Numbers in Configuration

**File:** `frontend/src/lib/config/scraper.config.ts`

**Problem:**
Hard-coded timeout values without clear documentation of their purpose.

```typescript
timeout: 60000,  // Why 60 seconds?
timeout: 120000, // Why 120 seconds for production?
```

**Recommendation:**
Define constants with descriptive names and comments explaining the rationale.

---

### MED-3: No Request Cancellation Support

**File:** `frontend/src/lib/connectors/unified-scraper.ts`

**Problem:**
Long-running scrape operations cannot be cancelled by the caller.

**Recommendation:**
Add AbortController support to allow request cancellation.

---

### MED-4: Error Messages Expose Internal Details

**File:** `frontend/src/app/api/v1/scrape/route.ts`
**Lines:** 74-82

**Problem:**
Error messages may expose internal implementation details.

```typescript
return NextResponse.json(
  {
    success: false,
    error: error instanceof Error ? error.message : '未知错误',
    // error.message could contain sensitive stack info
  },
  { status: 500 }
);
```

**Recommendation:**
Sanitize error messages and log full details server-side only.

---

### MED-5: Singleton Pattern Without Cleanup

**Files:**
- `frontend/src/lib/connectors/unified-scraper.ts`: Lines 410-417
- `frontend/src/lib/connectors/clawdbot-connector.ts`: Lines 365-372

**Problem:**
Global singleton instances persist for application lifetime without cleanup mechanism.

**Recommendation:**
Add reset/cleanup methods for testing and graceful shutdown scenarios.

---

### MED-6: Missing Input Sanitization for Search Keywords

**File:** `frontend/src/lib/connectors/unified-scraper.ts`
**Lines:** 326-366

**Problem:**
Search keywords are URL-encoded but not sanitized for potential injection.

```typescript
const searchUrl = `https://www.hktvmall.com/search?q=${encodeURIComponent(keyword)}`;
```

**Recommendation:**
Add keyword validation (length limits, character whitelist).

---

### MED-7: Test Scripts Use Hardcoded URLs

**Files:**
- `scripts/test-hktv-scrape.ts`: Lines 10-16
- `scripts/test-hktv-simple.js`: Line 5

**Problem:**
Test URLs are hardcoded and may become stale.

**Recommendation:**
Use environment variables or a config file for test URLs.

---

### MED-8: No Exponential Backoff Cap

**File:** `frontend/src/lib/connectors/unified-scraper.ts`
**Lines:** 126-128

**Problem:**
Exponential backoff can grow indefinitely with many retries.

```typescript
await new Promise((resolve) =>
  setTimeout(resolve, Math.pow(2, attempt) * 1000)  // Could be very long
);
```

**Recommendation:**
```typescript
const MAX_BACKOFF_MS = 30000;
const backoff = Math.min(Math.pow(2, attempt) * 1000, MAX_BACKOFF_MS);
await new Promise((resolve) => setTimeout(resolve, backoff));
```

---

## Low Priority Issues (Nice to Have)

### LOW-1: Inconsistent Language in Code Comments

**Problem:**
Comments mix Simplified Chinese and Traditional Chinese across files.

**Recommendation:**
Standardize on one Chinese variant throughout the codebase.

---

### LOW-2: Missing JSDoc for Public APIs

**Problem:**
Public functions lack comprehensive JSDoc documentation.

**Recommendation:**
Add @param, @returns, @throws documentation.

---

### LOW-3: No Type Export for External Consumers

**File:** `frontend/src/lib/connectors/unified-scraper.ts`

**Problem:**
Types are defined but some are not exported for external use.

**Recommendation:**
Export all public interface types.

---

### LOW-4: Screenshot Data Could Be Large

**File:** `frontend/src/lib/connectors/unified-scraper.ts`

**Problem:**
Base64 screenshots in response could be very large and impact memory.

**Recommendation:**
Consider streaming screenshots or storing separately.

---

### LOW-5: No Version Tracking for Scraper Results

**Problem:**
Scraped data has no version/schema information for future compatibility.

**Recommendation:**
Add a version field to scrape results.

---

## Architecture Review

### Strengths

1. **Clean Abstraction Layer:**
   The UnifiedScraper provides a good facade over Clawdbot and Firecrawl implementations, allowing easy switching between providers.

2. **Environment-Based Configuration:**
   The scraper.config.ts provides sensible defaults with environment-specific overrides.

3. **Separation of Concerns:**
   API routes, connectors, and configuration are properly separated.

4. **React Query Integration:**
   The useClawdbot hook properly leverages React Query for state management.

### Areas for Improvement

1. **Missing Repository/Service Layer:**
   Direct scraper calls from API routes. Consider adding a service layer for business logic.

2. **No Event/Queue System:**
   For batch operations, a proper job queue (Bull, BullMQ) would be more robust.

3. **No Caching Layer:**
   Scraped data could be cached to reduce redundant requests.

4. **Missing Monitoring/Metrics:**
   No instrumentation for tracking scraper performance, success rates, etc.

---

## Security Review Summary

| Vulnerability | Severity | Status |
|--------------|----------|--------|
| SSRF via unvalidated URLs | Critical | **OPEN** |
| Missing Authentication | Critical | **OPEN** |
| Unbounded Batch Size | Critical | **OPEN** |
| API Key in Config Object | High | **OPEN** |
| Error Message Leakage | Medium | **OPEN** |
| Missing Rate Limiting | High | **OPEN** |

### Recommended Security Additions

1. **URL Validation Middleware:**
   Create reusable URL validation that blocks internal addresses and whitelists allowed domains.

2. **Authentication Middleware:**
   Add session-based or API key authentication to all scrape endpoints.

3. **Rate Limiting:**
   Implement per-user and global rate limits.

4. **Request Logging:**
   Log all scrape requests for audit purposes.

5. **Input Validation Schema:**
   Use Zod or similar for request body validation.

---

## Priority Fix Recommendations

### Immediate (Before Production)

1. **CRIT-1:** Implement URL validation with domain whitelist
2. **CRIT-2:** Add authentication to scrape API
3. **CRIT-3:** Limit batch size and validate all URLs
4. **CRIT-4:** Refactor API key handling

### Short-term (Next Sprint)

1. **HIGH-1:** Replace `any` types with proper interfaces
2. **HIGH-2:** Fix WebSocket cleanup
3. **HIGH-3:** Handle task queue disconnection
4. **HIGH-6:** Replace deprecated `substr`

### Medium-term (Technical Debt)

1. **HIGH-4:** Add URL deduplication
2. **MED-1:** Implement proper logging
3. **MED-3:** Add request cancellation support

---

## Files Reviewed

| File | Lines | Issues Found |
|------|-------|--------------|
| `frontend/src/lib/connectors/unified-scraper.ts` | 449 | 6 |
| `frontend/src/lib/connectors/clawdbot-connector.ts` | 373 | 5 |
| `frontend/src/lib/config/scraper.config.ts` | 142 | 2 |
| `frontend/src/app/api/v1/scrape/route.ts` | 263 | 7 |
| `frontend/src/app/api/v1/scrape/clawdbot/route.ts` | 206 | 4 |
| `frontend/src/hooks/use-clawdbot.ts` | 129 | 1 |
| `scripts/scrape-and-sync.ts` | 217 | 2 |
| `scripts/test-hktv-scrape.ts` | 182 | 1 |
| `scripts/test-hktv-simple.js` | 133 | 1 |
| `scripts/test-simple-url.js` | 34 | 1 |
| `scripts/test-playwright-direct.js` | 97 | 0 |
| `scripts/test-playwright-hktv.js` | 130 | 0 |

---

## Conclusion

The HKTVmall scraping system has a solid architectural foundation with clean abstraction between the unified interface and underlying providers (Clawdbot/Firecrawl). However, **the system is not production-ready** due to critical security vulnerabilities, particularly the lack of URL validation and authentication.

**Recommended Actions:**
1. **Do not deploy to production** until CRIT-1 through CRIT-4 are resolved
2. Prioritize security fixes before feature development
3. Add comprehensive integration tests for the scraping flow
4. Implement monitoring before production deployment

---

*Report generated by Code Review Agent on 2026-01-28*
