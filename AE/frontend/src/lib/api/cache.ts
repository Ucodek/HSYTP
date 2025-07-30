/* eslint-disable @typescript-eslint/no-explicit-any */
import { StorageAdapter, LocalStorageAdapter } from "../storage";

// Types
interface CacheItem<T> {
  data: T;
  expiry: number;
  metadata?: Record<string, any>; // For additional info like source, version, etc.
}

interface CacheOptions {
  ttl: number; // Time to live in milliseconds
  namespace?: string; // Cache namespace for grouping related items
  secure?: boolean; // Use secure storage mechanism
  storageAdapter?: StorageAdapter; // Custom storage adapter
}

class CacheService {
  private namespace: string;
  private defaultTTL: number;
  private secure: boolean;
  private memoryCache: Map<string, CacheItem<any>>;
  private storageAdapter: StorageAdapter;
  private cleanupInterval: number | null = null;

  constructor(options: CacheOptions = { ttl: 5 * 60 * 1000 }) {
    this.namespace = options.namespace || "app-cache";
    this.defaultTTL = options.ttl;
    this.secure = options.secure || false;
    this.memoryCache = new Map();
    this.storageAdapter = options.storageAdapter || new LocalStorageAdapter();

    // Cleanup expired items on init
    this.cleanup();

    // Set up periodic cleanup if in browser
    if (typeof window !== "undefined") {
      this.cleanupInterval = window.setInterval(() => {
        this.cleanup();
      }, 5 * 60 * 1000); // Cleanup every 5 minutes
    }
  }

  /**
   * Destroy cache service (clear intervals, etc.)
   */
  destroy(): void {
    if (this.cleanupInterval !== null && typeof window !== "undefined") {
      window.clearInterval(this.cleanupInterval);
    }
  }

  /**
   * Create cache key with namespace
   */
  private createKey(key: string): string {
    return `${this.namespace}:${key}`;
  }

  /**
   * Get item from cache
   */
  get<T>(key: string): T | null {
    const cacheKey = this.createKey(key);

    // Try memory first (fastest)
    const memoryItem = this.memoryCache.get(cacheKey);
    if (memoryItem) {
      if (memoryItem.expiry > Date.now()) {
        return memoryItem.data as T;
      } else {
        // Expired, remove from memory
        this.memoryCache.delete(cacheKey);
      }
    }

    // Try storage next
    const item = this.storageAdapter.getItem<CacheItem<T>>(cacheKey);
    if (!item) return null;

    // Check if expired
    if (item.expiry > Date.now()) {
      // Update memory cache for faster future access
      this.memoryCache.set(cacheKey, item);
      return item.data;
    } else {
      // Expired, remove from storage
      this.storageAdapter.removeItem(cacheKey);
      return null;
    }
  }

  /**
   * Set item in cache with optional metadata
   */
  set<T>(
    key: string,
    data: T,
    ttl?: number,
    metadata?: Record<string, any>
  ): void {
    const cacheKey = this.createKey(key);
    const expiryTime = Date.now() + (ttl || this.defaultTTL);

    const cacheItem: CacheItem<T> = {
      data,
      expiry: expiryTime,
      metadata,
    };

    // Set in memory for faster access
    this.memoryCache.set(cacheKey, cacheItem);

    // Set in storage for persistence
    this.storageAdapter.setItem(cacheKey, cacheItem);
  }

  /**
   * Get cache item with metadata
   */
  getWithMetadata<T>(
    key: string
  ): { data: T; metadata?: Record<string, any> } | null {
    const cacheKey = this.createKey(key);

    // Try memory first
    const memoryItem = this.memoryCache.get(cacheKey);
    if (memoryItem && memoryItem.expiry > Date.now()) {
      return {
        data: memoryItem.data as T,
        metadata: memoryItem.metadata,
      };
    }

    // Try storage
    const item = this.storageAdapter.getItem<CacheItem<T>>(cacheKey);
    if (item && item.expiry > Date.now()) {
      return {
        data: item.data,
        metadata: item.metadata,
      };
    }

    return null;
  }

  /**
   * Update TTL for an existing cache item
   */
  updateTTL(key: string, newTTL: number): boolean {
    const cacheKey = this.createKey(key);

    // Try memory first
    const memoryItem = this.memoryCache.get(cacheKey);
    if (memoryItem) {
      memoryItem.expiry = Date.now() + newTTL;
      this.memoryCache.set(cacheKey, memoryItem);

      // Update in storage too
      this.storageAdapter.setItem(cacheKey, memoryItem);
      return true;
    }

    // Try storage
    const item = this.storageAdapter.getItem<CacheItem<any>>(cacheKey);
    if (item) {
      item.expiry = Date.now() + newTTL;
      this.storageAdapter.setItem(cacheKey, item);
      // Update memory cache
      this.memoryCache.set(cacheKey, item);
      return true;
    }

    return false;
  }

  /**
   * Check if key exists in cache (and is not expired)
   */
  has(key: string): boolean {
    return this.get(key) !== null;
  }

  /**
   * Remove item from cache
   */
  remove(key: string): void {
    const cacheKey = this.createKey(key);
    this.memoryCache.delete(cacheKey);
    this.storageAdapter.removeItem(cacheKey);
  }

  /**
   * Clear all items in this cache namespace
   */
  clear(): void {
    this.memoryCache.clear();

    // Remove all items with this namespace from storage
    if (typeof window !== "undefined") {
      Object.keys(localStorage)
        .filter((key) => key.startsWith(this.namespace))
        .forEach((key) => this.storageAdapter.removeItem(key));
    }
  }

  /**
   * Remove items matching pattern from cache
   * @param pattern RegExp to match against cache keys (without namespace)
   */
  removeByPattern(pattern: RegExp): void {
    // Clear memory cache
    for (const key of this.memoryCache.keys()) {
      const plainKey = key.slice(this.namespace.length + 1); // +1 for the colon
      if (pattern.test(plainKey)) {
        this.memoryCache.delete(key);
      }
    }

    // Clear storage cache
    if (typeof window !== "undefined") {
      const prefix = `${this.namespace}:`;
      Object.keys(localStorage)
        .filter((key) => key.startsWith(prefix))
        .forEach((key) => {
          const plainKey = key.slice(prefix.length);
          if (pattern.test(plainKey)) {
            this.storageAdapter.removeItem(key);
          }
        });
    }
  }

  /**
   * Clean up expired cache items
   */
  cleanup(): void {
    const now = Date.now();

    // Clean memory cache
    for (const [key, item] of this.memoryCache.entries()) {
      if (item.expiry < now) {
        this.memoryCache.delete(key);
      }
    }

    // Scan storage for expired items
    if (typeof window !== "undefined") {
      const prefix = `${this.namespace}:`;
      Object.keys(localStorage)
        .filter((key) => key.startsWith(prefix))
        .forEach((key) => {
          try {
            const item = JSON.parse(localStorage.getItem(key) || "{}");
            if (item.expiry && item.expiry < now) {
              this.storageAdapter.removeItem(key);
            }
          } catch (e) {
            // Invalid cache item, remove it
            this.storageAdapter.removeItem(key);
            console.error(`Error cleaning up cache item "${key}":`, e);
          }
        });
    }
  }
}

// Create default cache instance
const defaultCache = new CacheService();

export { CacheService, defaultCache };
