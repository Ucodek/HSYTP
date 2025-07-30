/* eslint-disable @typescript-eslint/no-explicit-any */
import axios, { AxiosInstance, AxiosError } from "axios";
import { defaultCache } from "./cache";
import circuitBreaker, { CircuitBreakerOptions } from "./circuit-breaker";
import networkListener from "./network-listener";
import { ApiRequestConfig, CacheMetrics } from "../types/api";
import { HttpMethods } from "./methods";
import authTokenManager from "./auth-token-manager";
import { CacheManager } from "./cache-manager";
import { RequestProcessor } from "./request-processor";
import { getLogger } from "../logger";

// Initialize logger
const logger = getLogger("ApiService");

class ApiService {
  private api: AxiosInstance;
  private cacheManager: CacheManager;
  private requestProcessor: RequestProcessor;
  private httpMethods: HttpMethods;

  constructor() {
    logger.debug("Initializing API Service");

    this.api = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL,
      timeout: 20000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Initialize cache manager with the default cache
    this.cacheManager = new CacheManager(defaultCache);

    // Initialize the request processor
    this.requestProcessor = new RequestProcessor(this.api, this.cacheManager);

    // Setup request interceptor with secure token using auth token manager
    this.api.interceptors.request.use(
      async (config) => {
        logger.debug(`Request: ${config.method?.toUpperCase()} ${config.url}`);
        // Apply auth token to headers
        config.headers = await authTokenManager.applyAuthHeader(config.headers);
        return config;
      },
      (error) => {
        logger.error("Request interceptor error", error);
        return Promise.reject(error);
      }
    );

    // Setup response interceptor with improved error handling
    this.api.interceptors.response.use(
      (response) => {
        logger.debug(`Response: ${response.status} ${response.config.url}`);
        return response;
      },
      async (error: AxiosError) => {
        // Add detailed logging in development environment
        logger.error(`API Error: ${error.message}`, {
          status: error.response?.status,
          url: error.config?.url,
          data: error.response?.data,
        });

        // Handle 401 Unauthorized: try to refresh token and retry once
        const config = error.config as any;
        if (error.response?.status === 401 && config && !config._retry) {
          config._retry = true;
          try {
            // Update the request headers with the new token
            config.headers = await authTokenManager.applyAuthHeader(
              config.headers
            );

            // Retry the original request with new token
            return this.api.request(config);
          } catch {
            // Refresh failed, clear tokens
            import("../storage").then(({ removeTokenResponse }) =>
              removeTokenResponse()
            );

            // Redirect to login
            window.location.href = "/login";
          }
        }
        return Promise.reject(error);
      }
    );

    // Initialize HTTP methods with the request handler
    this.httpMethods = new HttpMethods(this.request.bind(this));
    logger.info("API Service initialized successfully");
  }

  // Configure circuit breaker options
  configureCircuitBreaker(options: Partial<CircuitBreakerOptions>): void {
    logger.info("Configuring circuit breaker", options);
    circuitBreaker.configure(options);
  }

  // Reset a specific circuit
  resetCircuit(url: string): void {
    logger.info(`Resetting circuit for ${url}`);
    circuitBreaker.resetCircuit(url);
  }

  // Get circuit breaker status
  getCircuitStatus() {
    return circuitBreaker.getCircuitStatus();
  }

  // Generic request method to handle all HTTP methods - now delegates to RequestProcessor
  private async request<T>(
    method: "get" | "post" | "put" | "delete" | "patch",
    url: string,
    data?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    logger.debug(`Handling ${method.toUpperCase()} request to ${url}`);
    return this.requestProcessor.processRequest<T>(method, url, data, config);
  }

  // Get cache metrics
  getCacheMetrics(): CacheMetrics {
    return this.cacheManager.getMetrics(this.getCircuitStatus());
  }

  // HTTP method wrappers - delegate to httpMethods
  get<T>(url: string, params?: any, config?: ApiRequestConfig): Promise<T> {
    return this.httpMethods.get<T>(url, params, config);
  }

  getCritical<T>(
    url: string,
    params?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    return this.httpMethods.getCritical<T>(url, params, config);
  }

  getFresh<T>(
    url: string,
    params?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    return this.httpMethods.getFresh<T>(url, params, config);
  }

  getSWR<T>(url: string, params?: any, config?: ApiRequestConfig): Promise<T> {
    return this.httpMethods.getSWR<T>(url, params, config);
  }

  post<T>(url: string, data?: any, config?: ApiRequestConfig): Promise<T> {
    return this.httpMethods.post<T>(url, data, config);
  }

  put<T>(url: string, data?: any, config?: ApiRequestConfig): Promise<T> {
    return this.httpMethods.put<T>(url, data, config);
  }

  delete<T>(url: string, params?: any, config?: ApiRequestConfig): Promise<T> {
    return this.httpMethods.delete<T>(url, params, config);
  }

  patch<T>(url: string, data?: any, config?: ApiRequestConfig): Promise<T> {
    return this.httpMethods.patch<T>(url, data, config);
  }

  // Cache control methods
  clearCache(): void {
    this.cacheManager.clear();
  }

  invalidateCache(url: string): void {
    this.cacheManager.invalidate(url);
  }

  // Add a method to get network status
  isOnline(): boolean {
    return networkListener.getIsOnline();
  }

  // Add a method to get queued requests count
  getQueuedRequestsCount(): number {
    return networkListener.getQueueLength();
  }

  // Register network status change listener
  onNetworkStatusChange(callback: (isOnline: boolean) => void): void {
    networkListener.addEventListener(callback);
  }
}

// Export as singleton
const apiService = new ApiService();
export default apiService;
