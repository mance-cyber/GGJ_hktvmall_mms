import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";
import { ApiError } from "@/types/api";
import {
  getToken,
  setTokenFromJWT,
  clearToken,
  hasValidToken,
} from "@/lib/secure-token";

// ==================== API 客戶端Configuration ====================

/**
 * API 基礎 URL
 */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * RequestTimeoutTime（毫秒）
 */
const REQUEST_TIMEOUT = 30000;

// ==================== Axios 實例Create ====================

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

// ==================== Authentication Token Management ====================
// Use secure token manager (sessionStorage + memory cache)

/**
 * 從Security存儲Fetch Token
 */
function getAuthToken(): string | null {
  return getToken();
}

/**
 * Save token to secure storage
 * @param token - JWT token
 */
export function setAuthToken(token: string): void {
  setTokenFromJWT(token);
}

/**
 * ClearSecurity存儲的 Token
 */
export function clearAuthToken(): void {
  clearToken();
}

/**
 * Checkwhether有Valid的 Token
 */
export function hasAuthToken(): boolean {
  return hasValidToken();
}

// ==================== RequestIntercept器 ====================

/**
 * Request interceptor: auto-add authentication Token
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // RecordRequest（僅DevelopmentEnvironment）
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

// ==================== ResponseIntercept器 ====================

/**
 * Response interceptor: unified error handling and data formatting
 */
apiClient.interceptors.response.use(
  (response) => {
    // RecordResponse（僅DevelopmentEnvironment）
    if (process.env.NODE_ENV === "development") {
      console.log(`[API Response] ${response.config.url}`, response.data);
    }

    // Return data part directly
    return response.data;
  },
  (error: AxiosError<ApiError>) => {
    // UnifiedErrorProcessing
    const errorMessage = handleApiError(error);

    // RecordError
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

// ==================== ErrorProcessing ====================

/**
 * Processing API Error
 * @param error - Axios Error物items
 * @returns Error訊息
 */
function handleApiError(error: AxiosError<ApiError>): string {
  // 網路Error
  if (!error.response) {
    if (error.code === "ECONNABORTED") {
      return "RequestTimeout，請稍後再試";
    }
    return "Network connection error, please check your networkSettings";
  }

  // HTTP State碼Error
  const status = error.response.status;
  const errorData = error.response.data;

  switch (status) {
    case 400:
      return errorData?.message || "RequestParameterError";

    case 401:
      // Unauthorized, clear token and redirect to login頁
      clearAuthToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return "Login已Expired，請Re-Login";

    case 403:
      return "您沒有Permission執行此Operation";

    case 404:
      return errorData?.message || "Request的資源不存在";

    case 409:
      return errorData?.message || "資料衝突，請Re-整理後再試";

    case 422:
      return errorData?.message || "資料ValidateFailed";

    case 429:
      return "Too many requests, please try again later";

    case 500:
      return "ServerError，請稍後再試";

    case 502:
    case 503:
    case 504:
      return "Service temporarily unavailable, please try again later";

    default:
      return errorData?.message || "occurredUnknownError";
  }
}

// ==================== 通用RequestMethod ====================

/**
 * GET Request
 */
export async function get<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.get<any, T>(url, config);
}

/**
 * POST Request
 */
export async function post<T, D = any>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.post<any, T, D>(url, data, config);
}

/**
 * PUT Request
 */
export async function put<T, D = any>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.put<any, T, D>(url, data, config);
}

/**
 * PATCH Request
 */
export async function patch<T, D = any>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.patch<any, T, D>(url, data, config);
}

/**
 * DELETE Request
 */
export async function del<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  return apiClient.delete<any, T>(url, config);
}

// ==================== 檔案Upload ====================

/**
 * Upload檔案
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

// ==================== 檔案Download ====================

/**
 * Download檔案
 */
export async function downloadFile(
  url: string,
  filename: string
): Promise<void> {
  try {
    // Use raw axios instance for full response, bypass response interceptor
    const response = await axios.get(API_BASE_URL + url, {
      responseType: "blob",
      headers: {
        Authorization: `Bearer ${getAuthToken()}`,
      },
    });

    // Create download link
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;

    // TriggerDownload
    document.body.appendChild(link);
    link.click();

    // Clean up
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    console.error("Failed to download file:", error);
    throw error;
  }
}

// ==================== RequestCancel ====================

/**
 * Create cancellable request
 */
export function createCancelToken() {
  return axios.CancelToken.source();
}

/**
 * Determine if cancellation error
 */
export function isCancelError(error: any): boolean {
  return axios.isCancel(error);
}

// ==================== 工具Function ====================

/**
 * 建立QueryString
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
 * 建立完整 URL（含QueryString）
 */
export function buildUrl(
  path: string,
  params?: Record<string, any>
): string {
  if (!params) return path;

  const queryString = buildQueryString(params);
  return queryString ? `${path}?${queryString}` : path;
}

// ==================== 健康Check ====================

/**
 * Check if API service is available
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
 * Fetch API VersionInformation
 */
export async function getApiVersion(): Promise<{
  version: string;
  environment: string;
}> {
  return apiClient.get("/version");
}
