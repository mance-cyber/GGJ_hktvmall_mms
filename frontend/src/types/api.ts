// =============================================
// API Type definitions
// =============================================

/**
 * API ErrorResponseFormat
 */
export interface ApiError {
  /**
   * Error消息
   */
  message?: string;

  /**
   * Detailed error info (FastAPI standard format)
   */
  detail?: string;

  /**
   * Error代碼
   */
  code?: string;

  /**
   * ValidateErrorDetails（422 Error時）
   */
  errors?: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

/**
 * API SuccessResponseFormat
 */
export interface ApiResponse<T = any> {
  /**
   * ResponseData
   */
  data: T;

  /**
   * Response消息
   */
  message?: string;

  /**
   * ResponseState碼
   */
  status?: number;
}

/**
 * 分頁ResponseFormat
 */
export interface PaginatedResponse<T = any> {
  /**
   * DataList
   */
  items: T[];

  /**
   * 總Record數
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
