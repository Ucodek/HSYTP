import { getLogger } from "../logger";
import authRepository from "../repositories/auth.repository";
import { useAuthStore } from "../stores/auth.store";
import apiErrorHandler from "../api/error-handler";
import {
  LoginData,
  LoginResponse,
  RegisterData,
  RegisterResponse,
  User,
  UserResponse,
} from "../types/auth";
import { TokenResponse } from "../types/response";
import {
  setTokenResponseAsyncWithTimestamp,
  removeTokenResponse,
} from "../storage";

const logger = getLogger("AuthModel");

export class Auth {
  /**
   * Static method to register a new user
   * Uses store for state management
   */
  static async register(data: RegisterData): Promise<User> {
    logger.debug("Starting user registration process");

    // Get store functions (without subscribing to state changes)
    const { updateError, updateLoading } = useAuthStore.getState();

    try {
      updateLoading("registerLoading", true);
      updateError(null); // Reset any previous errors
      const result: RegisterResponse = await authRepository.register(data);
      logger.info("User registration completed successfully");
      // registerUser(result.data);
      return result.data;
    } catch (error) {
      const standardizedError = apiErrorHandler.standardizeError(error);
      logger.error("Failed to register user:", standardizedError);
      updateError(standardizedError);
      throw standardizedError;
    } finally {
      updateLoading("registerLoading", false);
    }
  }

  /**
   * Static method to login a user
   * Uses store for state management
   */
  static async login(data: LoginData): Promise<TokenResponse> {
    logger.debug("Starting user login process");

    const { loginUser, updateError, updateLoading } = useAuthStore.getState();

    try {
      updateLoading("loginLoading", true);
      updateError(null);
      const result: LoginResponse = await authRepository.login(data);
      logger.info("User login successful");
      loginUser(result.data);

      // Store the full token response securely with timestamp
      await setTokenResponseAsyncWithTimestamp(result.data);

      // Store the access token in cookie (for SSR/middleware)
      // document.cookie = `access_token=${result.data.access_token}; path=/; secure; samesite=strict`;

      await Auth.getMe(); // Fetch user details after login

      return result.data;
    } catch (error) {
      const standardizedError = apiErrorHandler.standardizeError(error);
      logger.error("Failed to login user:", standardizedError);
      updateError(standardizedError);
      throw standardizedError;
    } finally {
      updateLoading("loginLoading", false);
    }
  }

  /**
   * Static method to get the authenticated user details
   * Uses store for state management
   */
  static async getMe(): Promise<UserResponse> {
    logger.debug("Fetching authenticated user details");

    const { updateError, updateUser, updateIsAuthenticated } =
      useAuthStore.getState();

    try {
      // updateLoading("getMeLoading", true);
      updateError(null);
      const result: UserResponse = await authRepository.getMe();
      logger.info("Fetched authenticated user details successfully");
      updateUser(result.data);
      updateIsAuthenticated(true);
      return result;
    } catch (error) {
      const standardizedError = apiErrorHandler.standardizeError(error);
      logger.error("Failed to fetch user details:", standardizedError);
      updateError(standardizedError);
      throw standardizedError;
    } finally {
      // updateLoading("getMeLoading", false);
    }
  }

  /**
   * Static method to logout a user
   * Uses store for state management
   */
  static async logout(): Promise<void> {
    logger.debug("Starting user logout process");

    const { updateError, updateLoading, resetData } = useAuthStore.getState();

    try {
      updateLoading("logoutLoading", true);
      updateError(null);
      await authRepository.logout();

      // Clear all the store
      resetData();
      // Remove all token/session data
      removeTokenResponse();
      // Clear the access token from cookie
      // document.cookie =
      //   "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; secure; samesite=strict";

      logger.info("User logged out successfully");
    } catch (error) {
      const standardizedError = apiErrorHandler.standardizeError(error);
      logger.error("Failed to logout user:", standardizedError);
      updateError(standardizedError);
      throw standardizedError;
    } finally {
      updateLoading("logoutLoading", false);
    }
  }
}

export default Auth;
