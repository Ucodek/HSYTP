import requests from "../requests";
import { getLogger } from "../logger";
import { LoginData, RegisterData } from "../types/auth";

// Initialize logger
const logger = getLogger("AuthRepository");

/**
 * Repository for authentication-related data operations
 */
export const authRepository = {
  /**
   * Register a new user
   */
  register: async (data: RegisterData) => {
    try {
      logger.debug(`Registering user with data: ${JSON.stringify(data)}`);
      const result = await requests.auth.register(data);
      logger.info(`Registration successful for user: ${result.data.username}`);
      return result;
    } catch (error) {
      logger.error("User registration failed:", error);
      throw error;
    }
  },
  /**
   * Login a user
   */
  login: async (data: LoginData) => {
    try {
      logger.debug(`Logging in user with data: ${JSON.stringify(data)}`);
      const result = await requests.auth.login(data);
      logger.info(`Login successful for user: ${result.data.access_token}`);
      return result;
    } catch (error) {
      logger.error("User login failed:", error);
      throw error;
    }
  },
  /**
   * Get authenticated user details
   */
  getMe: async () => {
    try {
      logger.debug("Fetching authenticated user details");
      const result = await requests.auth.getMe();
      logger.info(`Fetched user details for: ${result.data.username}`);
      return result;
    } catch (error) {
      logger.error("Failed to fetch user details:", error);
      throw error;
    }
  },
  /**
   * Logout a user
   */
  logout: async () => {
    try {
      logger.debug("Logging out user");
      const result = await requests.auth.logout();
      logger.info("User logged out successfully");
      return result;
    } catch (error) {
      logger.error("User logout failed:", error);
      throw error;
    }
  },
  /**
   * Refresh access token using refresh token
   */
  refreshToken: async (refreshToken: string) => {
    try {
      logger.debug("Refreshing access token");
      const result = await requests.auth.refreshToken(refreshToken);
      logger.info("Token refresh successful");
      return result;
    } catch (error) {
      logger.error("Token refresh failed:", error);
      throw error;
    }
  },
};

export default authRepository;
