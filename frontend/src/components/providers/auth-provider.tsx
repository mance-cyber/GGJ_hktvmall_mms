"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { authApi, User } from "@/lib/api"
import { jwtDecode } from "jwt-decode"
import {
  getToken,
  setTokenFromJWT,
  clearToken,
  hasValidToken,
} from "@/lib/secure-token"

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (data: any) => Promise<void>
  loginGoogle: (credential: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const pathname = usePathname()

  const checkUser = async () => {
    // 使用Security token Management器
    const token = getToken()
    if (!token) {
      setLoading(false)
      return
    }

    try {
      // Token ExpiredCheck已由 secure-token 模組Processing
      const decoded: any = jwtDecode(token)
      if (decoded.exp * 1000 < Date.now()) {
        throw new Error("Token expired")
      }

      const userData = await authApi.getMe()
      setUser(userData)
    } catch (error) {
      console.error("Auth check failed:", error)
      clearToken()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkUser()
  }, [])

  useEffect(() => {
    const publicPaths = ["/login", "/register"]
    if (!loading && !user && !publicPaths.includes(pathname)) {
       router.push("/login")
    }
    if (!loading && user && publicPaths.includes(pathname)) {
        router.push("/")
    }
  }, [user, loading, pathname, router])

  const login = async (data: any) => {
    const res = await authApi.login(data)
    // 使用Security token Management器
    setTokenFromJWT(res.access_token)
    await checkUser()
  }

  const loginGoogle = async (credential: string) => {
    const res = await authApi.loginGoogle(credential)
    // 使用Security token Management器
    setTokenFromJWT(res.access_token)
    await checkUser()
  }

  const logout = () => {
    // 使用Security token Management器
    clearToken()
    setUser(null)
    router.push("/login")
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, loginGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
