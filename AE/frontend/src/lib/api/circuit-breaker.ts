import {
  CircuitState,
  CircuitBreakerOptions,
  CircuitStatusInfo,
} from "../types/api";
import { getLogger } from "../logger";

// Initialize logger
const logger = getLogger("CircuitBreaker");

/**
 * Circuit Breaker pattern implementation
 * Prevents cascading failures by stopping requests to failing services
 */
export class CircuitBreaker {
  private circuitState: Map<string, CircuitState> = new Map();
  private failureCounts: Map<string, number> = new Map();
  private lastFailureTime: Map<string, number> = new Map();
  private halfOpenAttempts: Map<string, number> = new Map();

  private options: CircuitBreakerOptions = {
    failureThreshold: 5, // Open after 5 failures
    resetTimeout: 30000, // Try again after 30 seconds
    halfOpenRequests: 3, // Allow 3 requests in half-open state
  };

  constructor(options?: Partial<CircuitBreakerOptions>) {
    if (options) {
      this.configure(options);
    }
  }

  /**
   * Configure circuit breaker options
   */
  configure(options: Partial<CircuitBreakerOptions>): void {
    logger.info("Configuring circuit breaker", options);
    this.options = { ...this.options, ...options };
  }

  /**
   * Generate a circuit key based on the URL's base path
   * e.g., /api/users/123 becomes /api/users
   */
  getCircuitKey(url: string): string {
    const parsedUrl = new URL(url, window.location.origin);
    const pathParts = parsedUrl.pathname.split("/");
    return pathParts.slice(0, 3).join("/"); // Group by base resource
  }

  /**
   * Check if circuit is open (request should be blocked)
   */
  isCircuitOpen(url: string): boolean {
    const circuitKey = this.getCircuitKey(url);
    const state = this.circuitState.get(circuitKey) || CircuitState.CLOSED;
    const lastFailure = this.lastFailureTime.get(circuitKey) || 0;

    if (state === CircuitState.OPEN) {
      const now = Date.now();
      // Check if it's time to try again (half-open)
      if (now - lastFailure > this.options.resetTimeout) {
        logger.info(
          `Transitioning circuit ${circuitKey} from OPEN to HALF_OPEN`
        );
        this.circuitState.set(circuitKey, CircuitState.HALF_OPEN);
        this.halfOpenAttempts.set(circuitKey, 0);
        return false; // Allow the request through
      }
      logger.debug(`Circuit ${circuitKey} is OPEN, blocking request`);
      return true; // Circuit is open, block the request
    }

    if (state === CircuitState.HALF_OPEN) {
      logger.debug(
        `Circuit ${circuitKey} is HALF_OPEN, allowing limited requests`
      );
    }

    return false; // Circuit is closed or half-open, allow requests
  }

  /**
   * Record a successful request to the service
   */
  recordSuccess(url: string): void {
    const circuitKey = this.getCircuitKey(url);
    const state = this.circuitState.get(circuitKey) || CircuitState.CLOSED;

    if (state === CircuitState.HALF_OPEN) {
      // In half-open state, track successful requests
      const attempts = (this.halfOpenAttempts.get(circuitKey) || 0) + 1;
      this.halfOpenAttempts.set(circuitKey, attempts);
      logger.debug(
        `Successful request to ${circuitKey} in HALF_OPEN state (${attempts}/${this.options.halfOpenRequests})`
      );

      // If enough successful requests, close the circuit
      if (attempts >= this.options.halfOpenRequests) {
        logger.info(
          `Circuit ${circuitKey} recovered, transitioning from HALF_OPEN to CLOSED`
        );
        this.circuitState.set(circuitKey, CircuitState.CLOSED);
        this.failureCounts.delete(circuitKey);
        this.lastFailureTime.delete(circuitKey);
        this.halfOpenAttempts.delete(circuitKey);
      }
    } else if (state === CircuitState.CLOSED) {
      // In closed state, reset failure count on success
      if (this.failureCounts.has(circuitKey)) {
        logger.debug(`Resetting failure count for ${circuitKey}`);
        this.failureCounts.delete(circuitKey);
      }
    }
  }

  /**
   * Record a failed request to the service
   */
  recordFailure(url: string): void {
    const circuitKey = this.getCircuitKey(url);
    const state = this.circuitState.get(circuitKey) || CircuitState.CLOSED;
    const now = Date.now();

    if (state === CircuitState.HALF_OPEN) {
      // Immediately open the circuit again on failure in half-open state
      logger.warn(
        `Request to ${circuitKey} failed in HALF_OPEN state, reopening circuit`
      );
      this.circuitState.set(circuitKey, CircuitState.OPEN);
      this.lastFailureTime.set(circuitKey, now);
    } else if (state === CircuitState.CLOSED) {
      // Increment failure count
      const failures = (this.failureCounts.get(circuitKey) || 0) + 1;
      this.failureCounts.set(circuitKey, failures);
      logger.debug(
        `Failure recorded for ${circuitKey} (${failures}/${this.options.failureThreshold})`
      );

      // Open the circuit if threshold is reached
      if (failures >= this.options.failureThreshold) {
        logger.warn(
          `Failure threshold reached for ${circuitKey}, opening circuit`
        );
        this.circuitState.set(circuitKey, CircuitState.OPEN);
        this.lastFailureTime.set(circuitKey, now);
      }
    }
  }

  /**
   * Reset a specific circuit
   */
  resetCircuit(url: string): void {
    const circuitKey = this.getCircuitKey(url);
    this.circuitState.delete(circuitKey);
    this.failureCounts.delete(circuitKey);
    this.lastFailureTime.delete(circuitKey);
    this.halfOpenAttempts.delete(circuitKey);
  }

  /**
   * Get status of all circuit breakers
   */
  getCircuitStatus(): Record<string, CircuitStatusInfo> {
    const status: Record<string, CircuitStatusInfo> = {};

    for (const [key, state] of this.circuitState.entries()) {
      let stateString: string;
      switch (state) {
        case CircuitState.OPEN:
          stateString = "OPEN";
          break;
        case CircuitState.HALF_OPEN:
          stateString = "HALF_OPEN";
          break;
        case CircuitState.CLOSED:
          stateString = "CLOSED";
          break;
      }

      status[key] = {
        state: stateString,
        failures: this.failureCounts.get(key) || 0,
        lastFailure: this.lastFailureTime.get(key)
          ? new Date(this.lastFailureTime.get(key)!)
          : null,
      };
    }

    return status;
  }
}

// Re-export the types for backward compatibility
export { CircuitState };

export type { CircuitBreakerOptions, CircuitStatusInfo };

// Export default singleton instance
export const circuitBreaker = new CircuitBreaker();
export default circuitBreaker;
