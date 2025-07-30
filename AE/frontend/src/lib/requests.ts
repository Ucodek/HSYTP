import apiService from "./api/api";
import { PortfolioOptimizationParams, OptimizationResult } from "./types";
import {
  LoginData,
  LoginResponse,
  RegisterData,
  RegisterResponse,
  UserResponse,
} from "./types/auth";
import {
  InstrumentListQuery,
  ListInstrumentResponse,
  ListInstrumentWithLatestPriceResponse,
} from "./types/instrument";
import { DataResponse } from "./types/response";

/**
 * Centralized API request definitions
 * Organized by domain for better maintainability
 */
export const requests = {
  auth: {
    /**
     * Register a new user
     */
    register: (data: RegisterData): Promise<RegisterResponse> => {
      return apiService.post<RegisterResponse>("/api/v1/auth/register", data);
    },
    /**
     * Login a user
     */
    login: (data: LoginData): Promise<LoginResponse> => {
      return apiService.post<LoginResponse>("/api/v1/auth/login", data, {
        withCredentials: true,
      });
    },
    /**
     * Get authenticated user details
     * This endpoint is used to fetch the current user's information
     */
    getMe: (): Promise<UserResponse> => {
      return apiService.get<UserResponse>("/api/v1/auth/me");
    },
    /**
     * Logout a user
     */
    logout: (): Promise<DataResponse<null>> => {
      return apiService.post<DataResponse<null>>(
        "/api/v1/auth/logout",
        {},
        {
          withCredentials: true,
        }
      );
    },
    /**
     * Refresh access token using refresh token
     */
    refreshToken: (refreshToken: string): Promise<LoginResponse> => {
      return apiService.post<LoginResponse>(
        "/api/v1/auth/refresh",
        {
          refresh_token: refreshToken,
        },
        { withCredentials: true }
      );
    },
  },
  instrument: {
    /**
     * List instruments
     */
    list: (queries: InstrumentListQuery): Promise<ListInstrumentResponse> => {
      return apiService.get<ListInstrumentResponse>(
        "/api/v1/instruments",
        queries
      );
    },
    /**
     * List instruments with latest prices
     */
    listWithLatestPrice: (
      queries: InstrumentListQuery
    ): Promise<ListInstrumentWithLatestPriceResponse> => {
      return apiService.get<ListInstrumentWithLatestPriceResponse>(
        "/api/v1/instruments/with-latest-price",
        queries
      );
    },
  },
  portfolio: {
    /**
     * Get portfolio optimization results based on parameters
     */
    optimize: (
      params: PortfolioOptimizationParams
    ): Promise<OptimizationResult> => {
      return apiService.post<OptimizationResult>("/portfolio/optimize", params);
    },
  },

  // Other domains can be added here (market, user, etc.)
};

export default requests;
