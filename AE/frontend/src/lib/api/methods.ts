/* eslint-disable @typescript-eslint/no-explicit-any */
import { ApiRequestConfig } from "../types/api";

/**
 * HTTP Methods Service
 * Provides wrappers for common HTTP methods with enhanced functionality
 */
export class HttpMethods {
  /**
   * Constructor takes a request handler function
   * @param requestHandler - Function that handles the actual HTTP requests
   */
  constructor(
    private requestHandler: <T>(
      method: "get" | "post" | "put" | "delete" | "patch",
      url: string,
      data?: any,
      config?: ApiRequestConfig
    ) => Promise<T>
  ) {}

  /**
   * GET request with default caching
   */
  async get<T>(
    url: string,
    params?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    return this.requestHandler<T>("get", url, params, {
      useCache: true,
      staleWhileRevalidate: false,
      ...config,
    });
  }

  /**
   * Add a method for critical requests that bypass circuit breaker
   */
  async getCritical<T>(
    url: string,
    params?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    return this.requestHandler<T>("get", url, params, {
      useCache: true,
      bypassCircuitBreaker: true,
      ...config,
    });
  }

  /**
   * Force a fresh GET request bypassing cache
   */
  async getFresh<T>(
    url: string,
    params?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    return this.requestHandler<T>("get", url, params, {
      useCache: false,
      ...config,
    });
  }

  /**
   * Stale-while-revalidate GET (returns cached data but refreshes in background)
   */
  async getSWR<T>(
    url: string,
    params?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    return this.requestHandler<T>("get", url, params, {
      useCache: true,
      staleWhileRevalidate: true,
      ...config,
    });
  }

  /**
   * POST request
   */
  async post<T>(
    url: string,
    data?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    return this.requestHandler<T>("post", url, data, config);
  }

  /**
   * PUT request
   */
  async put<T>(url: string, data?: any, config?: ApiRequestConfig): Promise<T> {
    return this.requestHandler<T>("put", url, data, config);
  }

  /**
   * DELETE request
   */
  async delete<T>(
    url: string,
    params?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    return this.requestHandler<T>("delete", url, params, config);
  }

  /**
   * PATCH request
   */
  async patch<T>(
    url: string,
    data?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    return this.requestHandler<T>("patch", url, data, config);
  }
}
