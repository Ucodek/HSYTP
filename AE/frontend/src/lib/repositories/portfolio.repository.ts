import requests from "../requests";
import { PortfolioOptimizationParams, OptimizationResult } from "../types";
import { getLogger } from "../logger";

// Initialize logger
const logger = getLogger("PortfolioRepository");

/**
 * Repository for portfolio-related data operations
 */
export const portfolioRepository = {
  /**
   * Get an optimized portfolio based on input parameters
   */
  optimize: async (
    params: PortfolioOptimizationParams
  ): Promise<OptimizationResult> => {
    try {
      // Convert string strategy to number if needed
      if (typeof params.optimization_strategy === "string") {
        params.optimization_strategy = parseInt(params.optimization_strategy);
      }

      logger.debug(
        `Optimizing portfolio with parameters: ${JSON.stringify(params)}`
      );
      const result = await requests.portfolio.optimize(params);

      // Add null check before accessing properties
      logger.info(
        `Portfolio optimization successful, returned ${
          result?.assets?.length || 0
        } assets`
      );

      // Verify result has expected structure
      if (!result || !result.assets || !result.portfolio) {
        throw new Error("Invalid optimization result structure");
      }

      return result;
    } catch (error) {
      // Log the error using the logger
      logger.error("Portfolio optimization request failed:", error);
      throw error;
    }
  },

  // Additional methods would go here
};

export default portfolioRepository;
