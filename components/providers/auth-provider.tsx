"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter, usePathname } from "next/navigation";
import { apiClient, setAuthToken, clearAuthToken } from "@/lib/api/client";

// Define User type
export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: "admin" | "operator" | "viewer";
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
  isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  // Fetch user profile
  const fetchUser = async () => {
    try {
      const token = localStorage.getItem("auth_token");
      if (!token) {
        setLoading(false);
        return;
      }
      
      const userData = await apiClient.get<User>("/api/v1/auth/me");
      setUser(userData);
    } catch (error) {
      console.error("Failed to fetch user:", error);
      clearAuthToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  // Protect routes
  useEffect(() => {
    if (loading) return;

    const isAuthPage = pathname.startsWith("/login");
    const isPublicPage = pathname === "/" || pathname.startsWith("/public"); // Add public routes if any

    if (!user && !isAuthPage && !isPublicPage) {
      router.push("/login");
    } else if (user && isAuthPage) {
      router.push("/dashboard");
    }
  }, [user, loading, pathname, router]);

  const login = async (token: string) => {
    setAuthToken(token);
    await fetchUser();
    router.push("/dashboard");
  };

  const logout = () => {
    clearAuthToken();
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
