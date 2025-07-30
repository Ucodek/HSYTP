/* eslint-disable @typescript-eslint/no-explicit-any */

/**
 * Request Deduplication Service
 * Manages pending requests to prevent duplicate API calls for the same resource
 */
export class RequestDeduplicator {
  // Map to track pending requests by cache key
  private pendingRequests: Map<string, Promise<any>> = new Map();

  /**
   * Check if a request is already in progress
   */
  isPending(key: string): boolean {
    return this.pendingRequests.has(key);
  }

  /**
   * Get a pending request if it exists
   */
  getPendingRequest<T>(key: string): Promise<T> | undefined {
    return this.pendingRequests.get(key);
  }

  /**
   * Register a request as pending
   */
  trackRequest<T>(key: string, requestPromise: Promise<T>): Promise<T> {
    this.pendingRequests.set(key, requestPromise);

    // Automatically clean up the request when it completes
    requestPromise.finally(() => {
      this.removePendingRequest(key);
    });

    return requestPromise;
  }

  /**
   * Remove a request from pending tracking
   */
  removePendingRequest(key: string): void {
    this.pendingRequests.delete(key);
  }

  /**
   * Clear all pending requests
   */
  clearAll(): void {
    this.pendingRequests.clear();
  }

  /**
   * Get the count of currently pending requests
   */
  getPendingCount(): number {
    return this.pendingRequests.size;
  }

  /**
   * Execute a request with deduplication
   * If an identical request is already pending, return that promise
   * Otherwise, execute the request and track it
   */
  async execute<T>(key: string, requestFn: () => Promise<T>): Promise<T> {
    // If request is already pending, return the existing promise
    if (this.isPending(key)) {
      return this.getPendingRequest<T>(key) as Promise<T>;
    }

    // Otherwise, execute the request and track it
    const promise = requestFn();
    return this.trackRequest(key, promise);
  }
}

// Export default singleton
export const requestDeduplicator = new RequestDeduplicator();
export default requestDeduplicator;
