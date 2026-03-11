// =============================================
// Secure Token Manager
// =============================================
// Use sessionStorage + memory cache to prevent XSS attacks
// Note: This is not a perfect security solution, best practice is to use httpOnly cookies

const TOKEN_KEY = "__auth_t"
const EXPIRY_KEY = "__auth_e"

// 內存中的 token Cache（最Security，但不持久）
let memoryToken: string | null = null
let memoryExpiry: number | null = null

// Simple obfuscation function (not encryption, just adds attack difficulty)
function obfuscate(value: string): string {
  if (typeof window === "undefined") return value
  // 使用 base64 + 反轉字符串
  const base64 = btoa(unescape(encodeURIComponent(value)))
  return base64.split("").reverse().join("")
}

function deobfuscate(value: string): string {
  if (typeof window === "undefined") return value
  try {
    const reversed = value.split("").reverse().join("")
    return decodeURIComponent(escape(atob(reversed)))
  } catch {
    return ""
  }
}

// =============================================
// 公開 API
// =============================================

/**
 * Fetch Token
 * 優先從內存讀取，其次從 sessionStorage
 */
export function getToken(): string | null {
  // 服務端Rendering時Back null
  if (typeof window === "undefined") return null

  // Prefer reading from memory (most secure)
  if (memoryToken) {
    // CheckwhetherExpired
    if (memoryExpiry && memoryExpiry < Date.now()) {
      clearToken()
      return null
    }
    return memoryToken
  }

  // Try to read from sessionStorage
  try {
    const stored = sessionStorage.getItem(TOKEN_KEY)
    const expiry = sessionStorage.getItem(EXPIRY_KEY)

    if (!stored) return null

    // CheckExpired
    if (expiry) {
      const expiryTime = parseInt(expiry, 10)
      if (expiryTime < Date.now()) {
        clearToken()
        return null
      }
      memoryExpiry = expiryTime
    }

    // 解混淆
    const token = deobfuscate(stored)
    if (!token) {
      clearToken()
      return null
    }

    // Cache到內存
    memoryToken = token
    return token
  } catch (error) {
    console.error("[SecureToken] 讀取Failed:", error)
    return null
  }
}

/**
 * Set up Token
 * @param token - JWT token
 * @param expiresInMs - ExpiredTime（毫秒），Default 30 minutes
 */
export function setToken(token: string, expiresInMs: number = 30 * 60 * 1000): void {
  if (typeof window === "undefined") return

  try {
    // CalculateExpiredTime
    const expiry = Date.now() + expiresInMs

    // Cache到內存
    memoryToken = token
    memoryExpiry = expiry

    // Store to sessionStorage (obfuscated)
    sessionStorage.setItem(TOKEN_KEY, obfuscate(token))
    sessionStorage.setItem(EXPIRY_KEY, String(expiry))
  } catch (error) {
    console.error("[SecureToken] SaveFailed:", error)
  }
}

/**
 * Clear Token
 */
export function clearToken(): void {
  // Clear內存
  memoryToken = null
  memoryExpiry = null

  // Clear sessionStorage
  if (typeof window === "undefined") return

  try {
    sessionStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(EXPIRY_KEY)
    // Also clear old localStorage token (migration)
    localStorage.removeItem("token")
  } catch (error) {
    console.error("[SecureToken] ClearFailed:", error)
  }
}

/**
 * Checkwhether有Valid Token
 */
export function hasValidToken(): boolean {
  return getToken() !== null
}

/**
 * Extract expiry time from JWT
 */
export function extractExpiry(token: string): number | null {
  try {
    const parts = token.split(".")
    if (parts.length !== 3) return null

    const payload = JSON.parse(atob(parts[1]))
    if (payload.exp) {
      return payload.exp * 1000 // Convert為毫秒
    }
    return null
  } catch {
    return null
  }
}

/**
 * Set token and auto-extract expiry time from JWT
 */
export function setTokenFromJWT(token: string): void {
  const expiry = extractExpiry(token)
  if (expiry) {
    const expiresInMs = expiry - Date.now()
    // If token is expired or expiring soon (<1 min), do not store
    if (expiresInMs < 60000) {
      console.warn("[SecureToken] Token 已Expired或即將Expired")
      return
    }
    setToken(token, expiresInMs)
  } else {
    // 無法提取ExpiredTime，使用Default 30 minutes
    setToken(token)
  }
}

// =============================================
// Migrate輔助
// =============================================

/**
 * Migrate token from old localStorage to new secure storage
 */
export function migrateFromLocalStorage(): void {
  if (typeof window === "undefined") return

  try {
    const oldToken = localStorage.getItem("token")
    if (oldToken && !getToken()) {
      // Migrate到新存儲
      setTokenFromJWT(oldToken)
      // Clear舊存儲
      localStorage.removeItem("token")
      console.info("[SecureToken] Migrated from localStorage token")
    }
  } catch (error) {
    console.error("[SecureToken] MigrateFailed:", error)
  }
}

// AutoMigrate
if (typeof window !== "undefined") {
  migrateFromLocalStorage()
}
