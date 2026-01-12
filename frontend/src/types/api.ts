// =============================================
// API 類型定義
// =============================================

/**
 * API 錯誤響應格式
 */
export interface ApiError {
  /**
   * 錯誤消息
   */
  message?: string;

  /**
   * 詳細錯誤信息（FastAPI 標準格式）
   */
  detail?: string;

  /**
   * 錯誤代碼
   */
  code?: string;

  /**
   * 驗證錯誤詳情（422 錯誤時）
   */
  errors?: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

/**
 * API 成功響應格式
 */
export interface ApiResponse<T = any> {
  /**
   * 響應數據
   */
  data: T;

  /**
   * 響應消息
   */
  message?: string;

  /**
   * 響應狀態碼
   */
  status?: number;
}

/**
 * 分頁響應格式
 */
export interface PaginatedResponse<T = any> {
  /**
   * 數據列表
   */
  items: T[];

  /**
   * 總記錄數
   */
  total: number;

  /**
   * 當前頁碼
   */
  page: number;

  /**
   * 每頁大小
   */
  page_size: number;

  /**
   * 總頁數
   */
  total_pages?: number;
}
