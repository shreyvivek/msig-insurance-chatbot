/**
 * Robust API Client for WanderSure Backend
 * Handles timeouts, retries, and proper error differentiation
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'
const REQUEST_TIMEOUT = 30000 // 30 seconds
const MAX_RETRIES = 2

export interface ApiError {
  success: false
  error_code: 'NETWORK_ERROR' | 'TIMEOUT' | 'VALIDATION_ERROR' | 'SERVER_ERROR' | 'UNKNOWN_ERROR'
  message: string
  status?: number
}

export interface ApiResponse<T = any> {
  success: true
  data: T
}

type ApiResult<T> = ApiResponse<T> | ApiError

class ApiClient {
  private baseUrl: string
  private timeout: number

  constructor(baseUrl: string = API_BASE_URL, timeout: number = REQUEST_TIMEOUT) {
    this.baseUrl = baseUrl.replace(/\/$/, '') // Remove trailing slash
    this.timeout = timeout
  }

  /**
   * Check if backend is available
   */
  async checkHealth(): Promise<boolean> {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000) // 5s for health check

      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Accept': 'application/json'
        }
      })

      clearTimeout(timeoutId)
      return response.ok
    } catch (error) {
      return false
    }
  }

  /**
   * Make a request with timeout and retry logic
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retries: number = MAX_RETRIES
  ): Promise<ApiResult<T>> {
    const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), this.timeout)

    const requestOptions: RequestInit = {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers
      }
    }

    try {
      const response = await fetch(url, requestOptions)
      clearTimeout(timeoutId)

      // Handle non-OK responses
      if (!response.ok) {
        let errorData: any = {}
        try {
          errorData = await response.json()
        } catch {
          // Response is not JSON
        }

        // Retry on 5xx errors
        if (response.status >= 500 && retries > 0) {
          await new Promise(resolve => setTimeout(resolve, 1000)) // Wait 1s before retry
          return this.request<T>(endpoint, options, retries - 1)
        }

        // 4xx errors - don't retry
        if (response.status >= 400 && response.status < 500) {
          return {
            success: false,
            error_code: 'VALIDATION_ERROR',
            message: errorData.message || errorData.detail || `Request failed: ${response.statusText}`,
            status: response.status
          }
        }

        // 5xx errors after retries exhausted
        return {
          success: false,
          error_code: 'SERVER_ERROR',
          message: errorData.message || `Server error: ${response.statusText}`,
          status: response.status
        }
      }

      // Parse successful response
      const data = await response.json()
      return {
        success: true,
        data
      }
    } catch (error: any) {
      clearTimeout(timeoutId)

      // Timeout
      if (error.name === 'AbortError') {
        if (retries > 0) {
          await new Promise(resolve => setTimeout(resolve, 1000))
          return this.request<T>(endpoint, options, retries - 1)
        }
        return {
          success: false,
          error_code: 'TIMEOUT',
          message: 'Request timed out. The server may be slow or unavailable.'
        }
      }

      // Network error
      if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
        if (retries > 0) {
          await new Promise(resolve => setTimeout(resolve, 1000))
          return this.request<T>(endpoint, options, retries - 1)
        }
        return {
          success: false,
          error_code: 'NETWORK_ERROR',
          message: 'Cannot connect to server. Make sure the backend is running on port 8002.'
        }
      }

      // Unknown error
      return {
        success: false,
        error_code: 'UNKNOWN_ERROR',
        message: error.message || 'An unexpected error occurred'
      }
    }
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, options?: RequestInit): Promise<ApiResult<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, body?: any, options?: RequestInit): Promise<ApiResult<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined
    })
  }
}

// Export singleton instance
export const apiClient = new ApiClient()

// Export convenience methods
export const api = {
  health: () => apiClient.checkHealth(),
  greeting: (userId: string, language: string = 'en') =>
    apiClient.get(`/api/greeting?user_id=${encodeURIComponent(userId)}&language=${encodeURIComponent(language)}`),
  ask: (question: string, options: {
    userId?: string
    language?: string
    contextData?: any
    isVoice?: boolean
  } = {}) =>
    apiClient.post('/api/ask', {
      question,
      language: options.language || 'en',
      user_id: options.userId || 'default_user',
      is_voice: options.isVoice || false,
      context_data: options.contextData || {}
    })
}

