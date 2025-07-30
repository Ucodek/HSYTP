/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  encrypt,
  decrypt,
  encryptData,
  decryptData,
  isEncryptionAvailable,
} from "./encryption";
import { TokenResponse } from "./types/response";

/**
 * Check if we're in browser environment
 */
const isBrowser = () => typeof window !== "undefined";

/**
 * Storage adapter interface for different storage backends
 */
export interface StorageAdapter {
  getItem<T>(key: string, parse?: boolean): T | null;
  setItem<T>(key: string, value: T, stringify?: boolean): void;
  removeItem(key: string): void;
  clear(): void;
  keys(): string[];
}

/**
 * Default localStorage adapter
 */
export class LocalStorageAdapter implements StorageAdapter {
  getItem<T>(key: string, parse: boolean = true): T | null {
    if (!isBrowser()) return null;

    try {
      const value = localStorage.getItem(key);
      if (!value) return null;
      return parse ? JSON.parse(value) : (value as unknown as T);
    } catch (e) {
      console.error(`Error getting item ${key} from localStorage:`, e);
      return null;
    }
  }

  setItem<T>(key: string, value: T, stringify: boolean = true): void {
    if (!isBrowser()) return;

    try {
      const storageValue = stringify ? JSON.stringify(value) : String(value);
      localStorage.setItem(key, storageValue);
    } catch (e) {
      console.error(`Error setting item ${key} in localStorage:`, e);
    }
  }

  removeItem(key: string): void {
    if (!isBrowser()) return;

    try {
      localStorage.removeItem(key);
    } catch (e) {
      console.error(`Error removing item ${key} from localStorage:`, e);
    }
  }

  clear(): void {
    if (!isBrowser()) return;

    try {
      localStorage.clear();
    } catch (e) {
      console.error("Error clearing localStorage:", e);
    }
  }

  keys(): string[] {
    if (!isBrowser()) return [];

    try {
      return Object.keys(localStorage);
    } catch (e) {
      console.error("Error getting keys from localStorage:", e);
      return [];
    }
  }
}

/**
 * In-memory only adapter (for sensitive data)
 */
export class MemoryStorageAdapter implements StorageAdapter {
  private storage = new Map<string, any>();

  getItem<T>(key: string, parse: boolean = false): T | null {
    try {
      const value = this.storage.get(key);
      if (!value) return null;
      return parse ? JSON.parse(value) : (value as unknown as T);
    } catch (e) {
      console.error(`Error getting item ${key} from MemoryStorage:`, e);
      return null;
    }
  }

  setItem<T>(key: string, value: T, stringify: boolean = false): void {
    try {
      const storageValue = stringify ? JSON.stringify(value) : value;
      this.storage.set(key, storageValue);
    } catch (e) {
      console.error(`Error setting item ${key} in MemoryStorage:`, e);
    }
  }

  removeItem(key: string): void {
    this.storage.delete(key);
  }

  clear(): void {
    this.storage.clear();
  }

  keys(): string[] {
    return Array.from(this.storage.keys());
  }
}

/**
 * SessionStorage adapter
 */
export class SessionStorageAdapter implements StorageAdapter {
  getItem<T>(key: string, parse: boolean = true): T | null {
    if (!isBrowser()) return null;

    try {
      const value = sessionStorage.getItem(key);
      if (!value) return null;
      return parse ? JSON.parse(value) : (value as unknown as T);
    } catch (e) {
      console.error(`Error getting item ${key} from sessionStorage:`, e);
      return null;
    }
  }

  setItem<T>(key: string, value: T, stringify: boolean = true): void {
    if (!isBrowser()) return;

    try {
      const storageValue = stringify ? JSON.stringify(value) : String(value);
      sessionStorage.setItem(key, storageValue);
    } catch (e) {
      console.error(`Error setting item ${key} in sessionStorage:`, e);
    }
  }

  removeItem(key: string): void {
    if (!isBrowser()) return;

    try {
      sessionStorage.removeItem(key);
    } catch (e) {
      console.error(`Error removing item ${key} from sessionStorage:`, e);
    }
  }

  clear(): void {
    if (!isBrowser()) return;

    try {
      sessionStorage.clear();
    } catch (e) {
      console.error("Error clearing sessionStorage:", e);
    }
  }

  keys(): string[] {
    if (!isBrowser()) return [];

    try {
      return Object.keys(sessionStorage);
    } catch (e) {
      console.error("Error getting keys from sessionStorage:", e);
      return [];
    }
  }
}

/**
 * EncryptedStorage adapter for securely storing sensitive data
 */
export class SecureStorageAdapter implements StorageAdapter {
  private baseAdapter: StorageAdapter;
  private securePrefix: string;

  constructor(baseAdapter?: StorageAdapter, securePrefix: string = "secure_") {
    this.baseAdapter = baseAdapter || new LocalStorageAdapter();
    this.securePrefix = securePrefix;
  }

  private isSecureKey(key: string): boolean {
    return key.startsWith(this.securePrefix);
  }

  getItem<T>(key: string, parse: boolean = true): T | null {
    const value = this.baseAdapter.getItem<string>(key, false);
    if (!value) return null;

    try {
      // If it's a secure key, decrypt the value
      const finalValue =
        this.isSecureKey(key) && isEncryptionAvailable()
          ? decrypt(value)
          : value;

      return parse ? JSON.parse(finalValue) : (finalValue as unknown as T);
    } catch (e) {
      console.error(`Error getting secure item ${key}:`, e);
      return null;
    }
  }

  setItem<T>(key: string, value: T, stringify: boolean = true): void {
    try {
      // Convert to string if needed
      const stringValue = stringify ? JSON.stringify(value) : String(value);

      // Encrypt if it's a secure key
      const finalValue =
        this.isSecureKey(key) && isEncryptionAvailable()
          ? encrypt(stringValue)
          : stringValue;

      this.baseAdapter.setItem(key, finalValue as any, false);
    } catch (e) {
      console.error(`Error setting secure item ${key}:`, e);
    }
  }

  async getItemAsync<T>(key: string, parse: boolean = true): Promise<T | null> {
    const value = this.baseAdapter.getItem<string>(key, false);
    if (!value) return null;

    try {
      // If it's a secure key, decrypt the value with async API
      let finalValue = value;
      if (this.isSecureKey(key) && isEncryptionAvailable()) {
        finalValue = await decryptData(value);
      }

      return parse ? JSON.parse(finalValue) : (finalValue as unknown as T);
    } catch (e) {
      console.error(`Error getting secure item ${key}:`, e);
      return null;
    }
  }

  async setItemAsync<T>(
    key: string,
    value: T,
    stringify: boolean = true
  ): Promise<void> {
    try {
      // Convert to string if needed
      const stringValue = stringify ? JSON.stringify(value) : String(value);

      // Encrypt if it's a secure key with async API
      let finalValue = stringValue;
      if (this.isSecureKey(key) && isEncryptionAvailable()) {
        finalValue = await encryptData(stringValue);
      }

      this.baseAdapter.setItem(key, finalValue as any, false);
    } catch (e) {
      console.error(`Error setting secure item ${key}:`, e);
    }
  }

  removeItem(key: string): void {
    this.baseAdapter.removeItem(key);
  }

  clear(): void {
    // Only clear secure items
    const allKeys = this.baseAdapter.keys();
    const secureKeys = allKeys.filter((key) => this.isSecureKey(key));

    for (const key of secureKeys) {
      this.baseAdapter.removeItem(key);
    }
  }

  keys(): string[] {
    return this.baseAdapter.keys();
  }
}

// --- Secure Item Helpers ---
function setSecureItem<T>(
  key: string,
  value: T,
  stringify: boolean = true
): void {
  const secureStorage = new SecureStorageAdapter();
  secureStorage.setItem(key, value, stringify);
  // secureStorage.setItem(`secure_${key}`, value, stringify);
}

function getSecureItem<T>(key: string, parse: boolean = true): T | null {
  const secureStorage = new SecureStorageAdapter();
  return secureStorage.getItem<T>(key, parse);
  // return secureStorage.getItem<T>(`secure_${key}`, parse);
}

async function setSecureItemAsync<T>(
  key: string,
  value: T,
  stringify: boolean = true
): Promise<void> {
  const secureStorage = new SecureStorageAdapter();
  await secureStorage.setItemAsync(key, value, stringify);
  // await secureStorage.setItemAsync(`secure_${key}`, value, stringify);
}

async function getSecureItemAsync<T>(
  key: string,
  parse: boolean = true
): Promise<T | null> {
  const secureStorage = new SecureStorageAdapter();
  return await secureStorage.getItemAsync<T>(key, parse);
  // return await secureStorage.getItemAsync<T>(`secure_${key}`, parse);
}

function removeSecureItem(key: string): void {
  const secureStorage = new SecureStorageAdapter();
  secureStorage.removeItem(key);
  // secureStorage.removeItem(`secure_${key}`);
}

// --- Token Storage & Session Helpers ---
// Store the full TokenResponse securely
export function setTokenResponse(tokenResponse: TokenResponse): void {
  setSecureItem("token_response", tokenResponse, true);
}

export function getTokenResponse(): TokenResponse | null {
  return getSecureItem<TokenResponse>("token_response", true);
}

export async function setTokenResponseAsync(
  tokenResponse: TokenResponse
): Promise<void> {
  await setSecureItemAsync("token_response", tokenResponse, true);
}

export async function getTokenResponseAsync(): Promise<TokenResponse | null> {
  return getSecureItemAsync<TokenResponse>("token_response", true);
}

export function removeTokenResponse(): void {
  removeSecureItem("token_response");
}

// Helpers to get access/refresh tokens and expiry
export function getAccessToken(): string | null {
  const tokenResponse = getTokenResponse();
  return tokenResponse?.access_token || null;
}

export function getRefreshToken(): string | null {
  const tokenResponse = getTokenResponse();
  return tokenResponse?.refresh_token || null;
}

export function getAccessTokenExpiry(): number | null {
  const tokenResponse = getTokenResponse();
  const expiry = tokenResponse?.access_expires_in;
  const num = Number(expiry);
  return isNaN(num) ? null : num;
}

export function getRefreshTokenExpiry(): number | null {
  const tokenResponse = getTokenResponse();
  const expiry = tokenResponse?.refresh_expires_in;
  const num = Number(expiry);
  return isNaN(num) ? null : num;
}

export function isAccessTokenExpired(): boolean {
  // const tokenResponse = getTokenResponse();
  const accessExpiresIn = getAccessTokenExpiry();
  if (!accessExpiresIn) {
    return true;
  }
  const storedAt = getTokenStoredAt();
  if (!storedAt) {
    return true;
  }
  const now = Math.floor(Date.now() / 1000);
  const expired = now >= storedAt + accessExpiresIn;
  return expired;
}

export function isRefreshTokenExpired(): boolean {
  // const tokenResponse = getTokenResponse();
  const refreshExpiresIn = getRefreshTokenExpiry();
  if (!refreshExpiresIn) {
    return true;
  }
  const storedAt = getTokenStoredAt();
  if (!storedAt) {
    return true;
  }
  const now = Math.floor(Date.now() / 1000);
  const expired = now >= storedAt + refreshExpiresIn;
  return expired;
}

// Store the time when the token was set (for expiry calculation)
function setTokenStoredAt(): void {
  const ts = Math.floor(Date.now() / 1000);
  setSecureItem("token_stored_at", ts, false);
}

function getTokenStoredAt(): number | null {
  const ts = getSecureItem<number>("token_stored_at", false);
  const num = Number(ts);
  return isNaN(num) ? null : num;
}

// Update setTokenResponse to also store the timestamp
export function setTokenResponseWithTimestamp(
  tokenResponse: TokenResponse
): void {
  setTokenResponse(tokenResponse);
  setTokenStoredAt();
}

export async function setTokenResponseAsyncWithTimestamp(
  tokenResponse: TokenResponse
): Promise<void> {
  await setTokenResponseAsync(tokenResponse);
  setTokenStoredAt();
}

// Export default storage adapter instance
export const defaultStorage = new LocalStorageAdapter();
