// =============================================
// 安全 Token 管理器
// =============================================
// 使用 sessionStorage + 內存緩存，防止 XSS 攻擊
// 注意：這不是完美的安全方案，最佳實踐是使用 httpOnly cookies

const TOKEN_KEY = "__auth_t"
const EXPIRY_KEY = "__auth_e"

// 內存中的 token 緩存（最安全，但不持久）
let memoryToken: string | null = null
let memoryExpiry: number | null = null

// 簡單的混淆函數（不是加密，僅增加攻擊難度）
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
 * 獲取 Token
 * 優先從內存讀取，其次從 sessionStorage
 */
export function getToken(): string | null {
  // 服務端渲染時返回 null
  if (typeof window === "undefined") return null

  // 優先從內存讀取（最安全）
  if (memoryToken) {
    // 檢查是否過期
    if (memoryExpiry && memoryExpiry < Date.now()) {
      clearToken()
      return null
    }
    return memoryToken
  }

  // 嘗試從 sessionStorage 讀取
  try {
    const stored = sessionStorage.getItem(TOKEN_KEY)
    const expiry = sessionStorage.getItem(EXPIRY_KEY)

    if (!stored) return null

    // 檢查過期
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

    // 緩存到內存
    memoryToken = token
    return token
  } catch (error) {
    console.error("[SecureToken] 讀取失敗:", error)
    return null
  }
}

/**
 * 設置 Token
 * @param token - JWT token
 * @param expiresInMs - 過期時間（毫秒），預設 30 分鐘
 */
export function setToken(token: string, expiresInMs: number = 30 * 60 * 1000): void {
  if (typeof window === "undefined") return

  try {
    // 計算過期時間
    const expiry = Date.now() + expiresInMs

    // 緩存到內存
    memoryToken = token
    memoryExpiry = expiry

    // 存儲到 sessionStorage（混淆後）
    sessionStorage.setItem(TOKEN_KEY, obfuscate(token))
    sessionStorage.setItem(EXPIRY_KEY, String(expiry))
  } catch (error) {
    console.error("[SecureToken] 儲存失敗:", error)
  }
}

/**
 * 清除 Token
 */
export function clearToken(): void {
  // 清除內存
  memoryToken = null
  memoryExpiry = null

  // 清除 sessionStorage
  if (typeof window === "undefined") return

  try {
    sessionStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(EXPIRY_KEY)
    // 同時清除舊的 localStorage token（遷移用）
    localStorage.removeItem("token")
  } catch (error) {
    console.error("[SecureToken] 清除失敗:", error)
  }
}

/**
 * 檢查是否有有效 Token
 */
export function hasValidToken(): boolean {
  return getToken() !== null
}

/**
 * 從 JWT 中提取過期時間
 */
export function extractExpiry(token: string): number | null {
  try {
    const parts = token.split(".")
    if (parts.length !== 3) return null

    const payload = JSON.parse(atob(parts[1]))
    if (payload.exp) {
      return payload.exp * 1000 // 轉換為毫秒
    }
    return null
  } catch {
    return null
  }
}

/**
 * 設置 Token 並自動從 JWT 提取過期時間
 */
export function setTokenFromJWT(token: string): void {
  const expiry = extractExpiry(token)
  if (expiry) {
    const expiresInMs = expiry - Date.now()
    // 如果 token 已過期或即將過期（少於 1 分鐘），不存儲
    if (expiresInMs < 60000) {
      console.warn("[SecureToken] Token 已過期或即將過期")
      return
    }
    setToken(token, expiresInMs)
  } else {
    // 無法提取過期時間，使用預設 30 分鐘
    setToken(token)
  }
}

// =============================================
// 遷移輔助
// =============================================

/**
 * 從舊的 localStorage 遷移 token 到新的安全存儲
 */
export function migrateFromLocalStorage(): void {
  if (typeof window === "undefined") return

  try {
    const oldToken = localStorage.getItem("token")
    if (oldToken && !getToken()) {
      // 遷移到新存儲
      setTokenFromJWT(oldToken)
      // 清除舊存儲
      localStorage.removeItem("token")
      console.info("[SecureToken] 已從 localStorage 遷移 token")
    }
  } catch (error) {
    console.error("[SecureToken] 遷移失敗:", error)
  }
}

// 自動遷移
if (typeof window !== "undefined") {
  migrateFromLocalStorage()
}
