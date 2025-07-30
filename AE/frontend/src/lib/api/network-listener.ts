import { QueuedRequest, NetworkEventCallback } from "../types/api";

/**
 * Network Listener Service
 * Manages online/offline status and request queuing
 */
export class NetworkListener {
  private isOnline: boolean = true;
  private requestQueue: Array<QueuedRequest> = [];
  private eventListeners: NetworkEventCallback[] = [];
  private initialized: boolean = false;

  constructor() {
    if (typeof window !== "undefined") {
      this.initialize();
    }
  }

  /**
   * Initialize network event listeners
   */
  private initialize(): void {
    if (this.initialized) return;

    // Get initial online status
    this.isOnline = navigator.onLine;

    // Setup event listeners
    window.addEventListener("offline", () => {
      this.isOnline = false;
      console.log("Network offline. Requests will be queued.");
      this.notifyListeners(false);
    });

    window.addEventListener("online", () => {
      this.isOnline = true;
      console.log("Network online. Processing queued requests.");
      this.notifyListeners(true);
      this.processQueue();
    });

    this.initialized = true;
  }

  /**
   * Process queued requests
   */
  private processQueue(): void {
    while (this.requestQueue.length > 0) {
      const request = this.requestQueue.shift();
      if (request) request().catch(console.error);
    }
  }

  /**
   * Notify all registered event listeners
   */
  private notifyListeners(isOnline: boolean): void {
    this.eventListeners.forEach((callback) => callback(isOnline));
  }

  /**
   * Add a request to the queue (if offline)
   * @returns true if queued, false if executed immediately
   */
  queueIfOffline(request: QueuedRequest): boolean {
    if (!this.isOnline) {
      this.requestQueue.push(request);
      return true;
    }
    return false;
  }

  /**
   * Check if network is online
   */
  getIsOnline(): boolean {
    return this.isOnline;
  }

  /**
   * Get the number of queued requests
   */
  getQueueLength(): number {
    return this.requestQueue.length;
  }

  /**
   * Clear all queued requests
   */
  clearQueue(): void {
    this.requestQueue = [];
  }

  /**
   * Add an event listener for network status changes
   */
  addEventListener(callback: NetworkEventCallback): void {
    this.eventListeners.push(callback);
  }

  /**
   * Remove an event listener
   */
  removeEventListener(callback: NetworkEventCallback): void {
    this.eventListeners = this.eventListeners.filter((cb) => cb !== callback);
  }

  /**
   * Execute a function with network awareness
   * If offline, queue the request; if online, execute immediately
   */
  async executeWithNetworkAwareness<T>(fn: () => Promise<T>): Promise<T> {
    if (!this.isOnline) {
      return new Promise<T>((resolve, reject) => {
        this.requestQueue.push(() => fn().then(resolve).catch(reject));
      });
    }

    return fn();
  }
}

// Export default singleton
export const networkListener = new NetworkListener();
export default networkListener;
