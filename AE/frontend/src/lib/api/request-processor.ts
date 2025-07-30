/* eslint-disable @typescript-eslint/no-explicit-any */
import { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";
import { ApiRequestConfig } from "../types/api";
import circuitBreaker from "./circuit-breaker";
import apiErrorHandler from "./error-handler";
import requestDeduplicator from "./request-deduplication";
import networkListener from "./network-listener";
import { CacheManager } from "./cache-manager";
import { getLogger } from "../logger";

// Initialize logger
const logger = getLogger("RequestProcessor");

/**
 * Request Processor
 * Core logic for processing HTTP requests with caching, circuit breaking, and error handling
 */
export class RequestProcessor {
  constructor(private api: AxiosInstance, private cacheManager: CacheManager) {
    logger.debug("Request processor initialized");
  }

  /**
   * Process an HTTP request with all enhancement features
   */
  async processRequest<T>(
    method: "get" | "post" | "put" | "delete" | "patch",
    url: string,
    data?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    try {
      logger.debug(`Processing ${method.toUpperCase()} request to ${url}`);

      // Track request in cache manager
      this.cacheManager.trackRequest();

      // Check if we're offline (unless bypass is set)
      if (!config?.bypassNetworkCheck && !networkListener.getIsOnline()) {
        logger.info(`Network offline, checking cache for ${url}`);

        // For GET requests, try to use cache when offline
        if (method === "get" && config?.useCache !== false) {
          const cacheKey =
            config?.cacheKey ||
            this.cacheManager.generateCacheKey(method, url, data);
          const cachedData = this.cacheManager.tryGet<T>(cacheKey);
          if (cachedData) {
            logger.debug(`Returning cached data for offline request to ${url}`);
            return cachedData;
          }
        }

        // Otherwise, queue the request for when we're back online
        logger.info(`Queuing ${method} request to ${url} for when online`);
        return new Promise<T>((resolve, reject) => {
          networkListener.queueIfOffline(async () => {
            try {
              logger.debug(
                `Processing queued request to ${url} now that we're online`
              );
              const result = await this.processRequest<T>(
                method,
                url,
                data,
                config
              );
              resolve(result);
            } catch (error) {
              logger.error(`Error processing queued request to ${url}`, error);
              reject(error);
            }
          });
        });
      }

      // Check circuit breaker state (unless bypassed)
      if (!config?.bypassCircuitBreaker && circuitBreaker.isCircuitOpen(url)) {
        logger.warn(`Circuit breaker open for ${url}, checking cache`);

        // Circuit is open, try to use cache for GET
        if (method === "get" && config?.useCache !== false) {
          const cacheKey =
            config?.cacheKey ||
            this.cacheManager.generateCacheKey(method, url, data);
          const cachedData = this.cacheManager.tryGet<T>(cacheKey);
          if (cachedData) {
            logger.debug(
              `Returning cached data for circuit-open request to ${url}`
            );
            return cachedData;
          }
        }

        logger.error(`Circuit open for ${url} and no cache available`);
        throw {
          status: 503,
          message: "Service temporarily unavailable (circuit breaker open)",
          data: { circuitBreaker: true, url },
        };
      }

      const cacheKey =
        config?.cacheKey ||
        this.cacheManager.generateCacheKey(method, url, data);

      // For GET requests, check cache first if caching is enabled
      if (method === "get" && config?.useCache !== false) {
        const cachedData = this.cacheManager.tryGet<T>(cacheKey);

        if (cachedData) {
          logger.debug(`Cache hit for ${url}`);

          // Implement stale-while-revalidate pattern
          if (config?.staleWhileRevalidate) {
            logger.debug(
              `Stale-while-revalidate: returning cached data for ${url} and refreshing in background`
            );
            // Return cached data immediately, but refresh in background
            setTimeout(() => {
              logger.debug(`Background refresh for ${url}`);
              this.makeRequest<T>(method, url, data, {
                ...config,
                useCache: false,
              })
                .then((freshData) => {
                  logger.debug(`Background refresh completed for ${url}`);
                  this.cacheManager.set(cacheKey, freshData, config?.cacheTTL);
                })
                .catch((error) => {
                  logger.error(`Background refresh failed for ${url}`, error);
                });
            }, 0);
          }

          return cachedData;
        }

        logger.debug(`Cache miss for ${url}`);
      }

      // For GET requests, use the request deduplicator
      if (method === "get") {
        logger.debug(`Using request deduplication for GET ${url}`);
        return requestDeduplicator.execute<T>(cacheKey, async () => {
          try {
            const response = await this.makeAndCacheRequest<T>(
              method,
              url,
              data,
              config,
              cacheKey
            );
            logger.debug(
              `Request to ${url} successful, recording success for circuit breaker`
            );
            circuitBreaker.recordSuccess(url);
            return response;
          } catch (error) {
            // Record failure for circuit breaker if it's a server error
            if (apiErrorHandler.isServerError(error)) {
              logger.warn(
                `Server error for ${url}, recording failure for circuit breaker`,
                error
              );
              circuitBreaker.recordFailure(url);
            } else {
              logger.debug(
                `Non-server error for ${url}, not recording for circuit breaker`,
                error
              );
            }
            throw error;
          }
        });
      }

      // For non-GET requests
      try {
        logger.debug(`Making ${method.toUpperCase()} request to ${url}`);
        const response = await this.makeAndCacheRequest<T>(
          method,
          url,
          data,
          config,
          cacheKey
        );
        logger.debug(`Non-GET request to ${url} successful`);
        circuitBreaker.recordSuccess(url);
        return response;
      } catch (error) {
        // Only record failure for server errors
        if (apiErrorHandler.isServerError(error)) {
          logger.warn(
            `Server error on ${method.toUpperCase()} request to ${url}, recording for circuit breaker`
          );
          circuitBreaker.recordFailure(url);
        } else {
          logger.debug(
            `Non-server error on ${method.toUpperCase()} request to ${url}`
          );
        }
        throw error;
      }
    } catch (error) {
      logger.error(
        `Error processing ${method.toUpperCase()} request to ${url}`,
        error
      );
      return apiErrorHandler.handleError(error);
    }
  }

  /**
   * Make a request and cache the response
   */
  private async makeAndCacheRequest<T>(
    method: "get" | "post" | "put" | "delete" | "patch",
    url: string,
    data?: any,
    config?: ApiRequestConfig,
    cacheKey?: string
  ): Promise<T> {
    logger.debug(`Making ${method} request to ${url}`);
    const response = await this.makeRequest<T>(method, url, data, config);

    // Cache GET requests if caching is enabled
    if (method === "get" && config?.useCache !== false && cacheKey) {
      logger.debug(
        `Caching response for ${url} with TTL ${config?.cacheTTL || "default"}`
      );
      this.cacheManager.set(cacheKey, response, config?.cacheTTL);
    }

    // Invalidate cache for non-GET requests that modify data
    if (method !== "get") {
      logger.debug(
        `Invalidating cache for ${url} after ${method.toUpperCase()} request`
      );
      this.cacheManager.invalidateResource(url);
    }

    return response;
  }

  /**
   * Make the actual API request
   */
  private async makeRequest<T>(
    method: "get" | "post" | "put" | "delete" | "patch",
    url: string,
    data?: any,
    config?: ApiRequestConfig
  ): Promise<T> {
    const requestConfig: AxiosRequestConfig = {
      method,
      url,
      ...(method === "get" ? { params: data } : { data }),
      ...config,
    };

    logger.debug(`Executing axios ${method.toUpperCase()} request to ${url}`);
    const response: AxiosResponse<T> = await this.api(requestConfig);
    logger.debug(
      `Axios ${method.toUpperCase()} request to ${url} complete: ${
        response.status
      }`
    );
    return response.data;
  }
}
