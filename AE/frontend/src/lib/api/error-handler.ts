/* eslint-disable @typescript-eslint/no-explicit-any */
import axios, { AxiosError } from "axios";
import { ApiErrorResponse } from "../types/api";
import { getLogger } from "../logger";

// Initialize logger
const logger = getLogger("ErrorHandler");

/**
 * API Error Handler
 * Provides consistent error handling for API requests
 */
export class ApiErrorHandler {
  /**
   * Handles and standardizes errors from API requests
   */
  handleError(error: any): never {
    // Check if it's an Axios error
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;

      logger.error("Handling Axios error", {
        status: axiosError.response?.status,
        url: axiosError.config?.url,
        message: this.getErrorMessage(axiosError),
      });

      // Format the error response in a consistent way
      const errorResponse: ApiErrorResponse = {
        status: axiosError.response?.status || 0,
        message: this.getErrorMessage(axiosError),
        data: axiosError.response?.data,
      };

      throw errorResponse;
    }

    // Handle non-Axios errors
    logger.error("Handling non-Axios error", error);
    throw {
      status: 0,
      message: error?.message || "Unknown error occurred",
      data: error,
    };
  }

  /**
   * Extract appropriate error message from Axios error
   */
  private getErrorMessage(error: AxiosError): string {
    // Return error based on priority
    return (
      // First priority: Backend returned error message
      (error.response?.data as any)?.message ||
      // Second priority: Error status with text
      (error.response?.status
        ? `${error.response.status}: ${error.response.statusText}`
        : null) ||
      // Third priority: Network error
      (error.request && !error.response
        ? "Network error. Please check your connection."
        : null) ||
      // Fallback
      error.message ||
      "An unknown error occurred"
    );
  }

  /**
   * Determine if an error appears to be a server error (5xx)
   */
  isServerError(error: any): boolean {
    const status = error?.status || error?.response?.status;
    return (status >= 500 && status < 600) || !status;
  }

  /**
   * Standardize any error into a consistent error object with a message property
   * This can be used outside of the axios error handling flow
   */
  standardizeError(error: any): Error {
    // If it's already an Error object with a message, return it
    if (error instanceof Error) {
      return error;
    }

    // If it's an Axios error, format it consistently
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      const message = this.getErrorMessage(axiosError);

      const standardError = new Error(message);
      // Add additional properties for debugging
      Object.assign(standardError, {
        status: axiosError.response?.status,
        url: axiosError.config?.url,
        data: axiosError.response?.data,
      });

      return standardError;
    }

    // If it's an object with a message property, convert to Error
    if (error && typeof error === "object" && error.message) {
      const standardError = new Error(error.message);
      // Add any additional properties for context
      Object.assign(standardError, error);
      return standardError;
    }

    // For any other type, create a new Error with the best string representation
    return new Error(
      typeof error === "string" ? error : "An unknown error occurred"
    );
  }
}

// Export default singleton
export const apiErrorHandler = new ApiErrorHandler();
export default apiErrorHandler;
