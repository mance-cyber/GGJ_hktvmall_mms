import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";
import { ApiError } from "@/types/api";

// ==================== API 客戶端配置 ====================

/**
 * API 基礎 URL
 */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * 請求超時時間（毫秒）
 */
const REQUEST_TIMEOUT = 30000;

// ==================== Axios 實例創建 ====================

/**
 * 主要 API 客戶端實例
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// ==================== 認證 Token 管理 ====================

/**
 * 從本地儲存獲取 Token
 */
function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;

  try {
    return localStorage.getItem("token");
  } catch {
    return null;
  }
}

/**
 * 儲存 Token 到本地儲存
 */
export function setAuthToken(token: string): void {
  if (typeof window === "undefined") return;

  try {
    localStorage.setItem("token", token);
  } catch (error) {
    console.error("Failed to save auth token:", error);
  }
}

/**
 * 清除本地儲存的 Token
 */
export function clearAuthToken(): void {
  if (typeof window === "undefined") return;

  try {
    localStorage.removeItem("token");
  } catch (error) {
    console.error("Failed to clear auth token:", error);
  }
}

// ==================== 請求攔截器 ====================

/**
 * 請求攔截器：自動添加認證 Token
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 記錄請求（僅開發環境）
    if (process.env.NODE_ENV === "development") {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    }

    return config;
  },
  (error) => {
    console.error("[API Request Error]", error);
    return Promise.reject(error);
  }
);

// ==================== 響應攔截器 ====================

/**
 * 響應攔截器：統一處理錯誤與數據格式
 */
apiClient.interceptors.response.use(
  (response) => {
    // 記錄響應（僅開發環境）
    if (process.env.NODE_ENV === "development") {
      console.log(`[API Response] ${response.config.url}`, response.data);
    }

    // 直接返回 data 部分
    return response.data;
  },
  (error: AxiosError<ApiError>) => {
    // 統一錯誤處理
    const errorMessage = handleApiError(error);

    // 記錄錯誤
    console.error("[API Error]", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data,
    });

    return Promise.reject(error);
  }
);

// ==================== 錯誤處理 ====================

/**
 * 處理 API 錯誤
 * @param error - Axios 錯誤物件
 * @returns 錯誤訊息
 */
function handleApiError(error: AxiosError<ApiError>): string {
  // 網路錯誤
  if (!error.response) {
    if (error.code === "ECONNABORTED") {
      return "請求超時，請稍後再試";
    }
    return "網路連線異常，請檢查您的網路設定";
  }

  // HTTP 狀態碼錯誤
  const status = error.response.status;
  const errorData = error.response.data;

  switch (status) {
    case 400:
      return errorData?.message || "請求參數錯誤";

    case 401:
      // 未授權，清除 Token 並重定向到登入頁
      clearAuthToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return "登入已過期，請重新登入";

    case 403:
      return "您沒有權限執行此操作";

    case 404:
      return errorData?.message || "請求的資源不存在";

    case 409:
      return errorData?.message || "資料衝突，請重新整理後再試";

    case 422:
      return errorData?.message || "資料驗證失敗";

    case 429:
      return "請求過於頻繁，請稍後再試";

    case 500:
      return "伺服器錯誤，請稍後再試";

    case 502:
    case 503:
    case 504:
      return "服務暫時無法使用，請稍後再試";

    default:
      return errorData?.message || "發生未知錯誤";
  }
}

// ==================== 通用請求方法 ====================

/**
 * GET 請求
 */
export async function get<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.get<any, T>(url, config);
}

/**
 * POST 請求
 */
export async function post<T, D = any>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.post<any, T, D>(url, data, config);
}

/**
 * PUT 請求
 */
export async function put<T, D = any>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.put<any, T, D>(url, data, config);
}

/**
 * PATCH 請求
 */
export async function patch<T, D = any>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.patch<any, T, D>(url, data, config);
}

/**
 * DELETE 請求
 */
export async function del<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.delete<any, T>(url, config);
}

// ==================== 檔案上傳 ====================

/**
 * 上傳檔案
 */
export async function uploadFile(
  url: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<{ url: string }> {
  const formData = new FormData();
  formData.append("file", file);

  return apiClient.post(url, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      }
    },
  });
}

// ==================== 檔案下載 ====================

/**
 * 下載檔案
 */
export async function downloadFile(
  url: string,
  filename: string
): Promise<void> {
  try {
    // 使用原始 axios 實例以獲取完整響應，繞過響應攔截器
    const response = await axios.get(API_BASE_URL + url, {
      responseType: "blob",
      headers: {
        Authorization: `Bearer ${getAuthToken()}`,
      },
    });

    // 建立下載連結
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;

    // 觸發下載
    document.body.appendChild(link);
    link.click();

    // 清理
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error("Failed to download file:", error);
    throw error;
  }
}

// ==================== 請求取消 ====================

/**
 * 建立可取消的請求
 */
export function createCancelToken() {
  return axios.CancelToken.source();
}

/**
 * 判斷是否為取消錯誤
 */
export function isCancelError(error: any): boolean {
  return axios.isCancel(error);
}

// ==================== 工具函數 ====================

/**
 * 建立查詢字串
 */
export function buildQueryString(params: Record<string, any>): string {
  const filteredParams = Object.entries(params).reduce((acc, [key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      acc[key] = value;
    }
    return acc;
  }, {} as Record<string, any>);

  const searchParams = new URLSearchParams(filteredParams);
  return searchParams.toString();
}

/**
 * 建立完整 URL（含查詢字串）
 */
export function buildUrl(
  path: string,
  params?: Record<string, any>
): string {
  if (!params) return path;

  const queryString = buildQueryString(params);
  return queryString ? `${path}?${queryString}` : path;
}

// ==================== 健康檢查 ====================

/**
 * 檢查 API 服務是否可用
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    await apiClient.get("/health");
    return true;
  } catch {
    return false;
  }
}

/**
 * 獲取 API 版本資訊
 */
export async function getApiVersion(): Promise<{
  version: string;
  environment: string;
}> {
  return apiClient.get("/version");
}
