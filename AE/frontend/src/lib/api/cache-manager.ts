/* eslint-disable @typescript-eslint/no-explicit-any */
import { CacheService } from "./cache";
import { CacheMetrics } from "../types/api";

/**
 * Cache Manager
 * Handles caching operations for API requests
 */
export class CacheManager {
  private metrics = {
    hits: 0,
    misses: 0,
    requests: 0,
  };

  constructor(private cache: CacheService) {}

  /**
   * Generate a consistent cache key
   */
  generateCacheKey(method: string, url: string, params?: any): string {
    return `${method}:${url}:${params ? JSON.stringify(params) : ""}`;
  }

  /**
   * Try to get data from cache
   * @returns The cached data if found, undefined otherwise
   */
  tryGet<T>(cacheKey: string): T | undefined {
    const data = this.cache.get<T>(cacheKey);
    if (data) {
      this.metrics.hits++;
      return data;
    }
    this.metrics.misses++;
    return undefined;
  }

  /**
   * Set data in cache with optional TTL
   */
  set<T>(cacheKey: string, data: T, ttl?: number): void {
    // Skip cache for auth-related endpoints
    if (cacheKey.includes("/auth/")) return;
    this.cache.set(cacheKey, data, ttl);
  }

  /**
   * Clear entire cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Invalidate cache entries by pattern
   */
  invalidateByPattern(pattern: RegExp): void {
    this.cache.removeByPattern(pattern);
  }

  /**
   * Invalidate cache for a specific URL pattern
   */
  invalidate(url: string): void {
    this.invalidateByPattern(new RegExp(`^.*${url}.*$`));
  }

  /**
   * Invalidate cache for resource modifications
   * (for non-GET requests that modify data)
   */
  invalidateResource(url: string): void {
    // Remove the specific ID to match the entire resource collection
    this.invalidateByPattern(new RegExp(url.replace(/\/\d+$/, "(/\\d+)?$")));
  }

  /**
   * Track a cache request
   */
  trackRequest(): void {
    this.metrics.requests++;
  }

  /**
   * Get cache metrics
   */
  getMetrics(circuitBreakerStatus: Record<string, any>): CacheMetrics {
    return {
      ...this.metrics,
      hitRate: this.metrics.requests
        ? ((this.metrics.hits / this.metrics.requests) * 100).toFixed(2) + "%"
        : "0%",
      circuitBreakerStatus,
    };
  }
}

// Note: We don't export a default instance here because it needs the cache service instance
