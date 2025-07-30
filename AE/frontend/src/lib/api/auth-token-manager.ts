import {
  getAccessToken,
  getRefreshToken,
  isAccessTokenExpired,
  isRefreshTokenExpired,
  setTokenResponseWithTimestamp,
  removeTokenResponse,
} from "../storage";
import authRepository from "../repositories/auth.repository";
import { AxiosRequestHeaders } from "axios";
import { TokenResponse } from "../types/response";

/**
 * Auth Token Manager
 * Manages authentication tokens for API requests
 */
export class AuthTokenManager {
  private refreshing: boolean = false;
  // TODO: Implement promise based token refresh
  // private refreshPromise: Promise<TokenResponse | null> | null = null;
  /**
   * Get a valid access token, refreshing if needed
   */
  async getToken(): Promise<string | null> {
    const accessToken = getAccessToken();
    if (accessToken && !isAccessTokenExpired()) {
      return accessToken;
    }

    if (this.refreshing) return null; // If already refreshing, wait for the refresh to complete

    const result = await this.refreshToken();

    if (result) {
      return result.access_token;
    }

    return null;
  }

  async refreshToken(): Promise<TokenResponse | null> {
    const refreshToken = getRefreshToken();
    if (!refreshToken || isRefreshTokenExpired()) {
      removeTokenResponse();
      return null;
    }

    this.refreshing = true;
    const result = await authRepository.refreshToken(refreshToken);
    if (result) {
      setTokenResponseWithTimestamp(result.data);
      this.refreshing = false;
      return result.data;
    }

    removeTokenResponse();
    this.refreshing = false;
    return null;
  }

  /**
   * Apply authorization token to request headers
   */
  async applyAuthHeader(
    headers: AxiosRequestHeaders
  ): Promise<AxiosRequestHeaders> {
    const token = await this.getToken();
    if (token) {
      // Modify the headers in a way that preserves the AxiosRequestHeaders type
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }
}

// Export default singleton
export const authTokenManager = new AuthTokenManager();
export default authTokenManager;
