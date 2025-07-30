/* eslint-disable @typescript-eslint/no-explicit-any */
import { AxiosRequestConfig } from "axios";

/**
 * Extended request config type with cache options
 */
export interface ApiRequestConfig extends AxiosRequestConfig {
  useCache?: boolean;
  cacheTTL?: number;
  cacheKey?: string;
  staleWhileRevalidate?: boolean;
  bypassCircuitBreaker?: boolean; // Skip circuit breaker check for critical requests
  bypassNetworkCheck?: boolean; // Skip offline check for critical requests
}

/**
 * API Error Response structure
 */
export interface ApiErrorResponse {
  status: number;
  message: string;
  data?: any;
}

/**
 * Cache metrics structure
 */
export interface CacheMetrics {
  hits: number;
  misses: number;
  requests: number;
  hitRate: string;
  circuitBreakerStatus: Record<string, any>;
}

/**
 * Circuit breaker state enum
 */
export enum CircuitState {
  CLOSED, // Normal operation, requests flow through
  OPEN, // Circuit is open, requests are blocked with immediate rejection
  HALF_OPEN, // Testing if service is recovered
}

/**
 * Circuit breaker configuration and tracking
 */
export interface CircuitBreakerOptions {
  failureThreshold: number; // Number of failures before opening circuit
  resetTimeout: number; // Time in ms before trying half-open state
  halfOpenRequests: number; // Number of requests to allow in half-open state
}

/**
 * Circuit breaker status information
 */
export interface CircuitStatusInfo {
  state: string;
  failures: number;
  lastFailure: Date | null;
}

/**
 * Type definition for request queue items
 */
export type QueuedRequest = () => Promise<any>;

/**
 * Network event callback type
 */
export type NetworkEventCallback = (isOnline: boolean) => void;
