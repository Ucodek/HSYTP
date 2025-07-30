import { getLogger } from "../logger";
import portfolioRepository from "../repositories/portfolio.repository";
import { usePortfolioStore } from "../stores/portfolio.store";
import apiErrorHandler from "../api/error-handler";
import {
  Asset,
  PortfolioOptimizationParams,
  OptimizationResult,
} from "../types";

const logger = getLogger("Portfolio");

export class Portfolio {
  id?: string;
  name: string;
  assets: Asset[];
  expectedReturn: number;
  volatility: number;
  sharpeRatio: number;
  sortinoRatio: number;
  optimizationStrategy?: number;

  constructor(data: Partial<Portfolio>) {
    this.id = data.id;
    this.name = data.name || "New Portfolio";
    this.assets = data.assets || [];
    this.expectedReturn = data.expectedReturn || 0;
    this.volatility = data.volatility || 0;
    this.sharpeRatio = data.sharpeRatio || 0;
    this.sortinoRatio = data.sortinoRatio || 0;
    this.optimizationStrategy = data.optimizationStrategy;
  }

  /**
   * Calculate the total weight of all assets
   */
  getTotalWeight(): number {
    return this.assets.reduce((sum, asset) => sum + asset.weight, 0);
  }

  /**
   * Check if weights are properly distributed (sum to 1)
   */
  hasValidWeights(): boolean {
    const totalWeight = this.getTotalWeight();
    return Math.abs(totalWeight - 1) < 0.0001; // Allow small floating point errors
  }

  /**
   * Get assets sorted by weight
   */
  getAssetsSortedByWeight(): Asset[] {
    return [...this.assets].sort((a, b) => b.weight - a.weight);
  }

  /**
   * Static factory method to create a portfolio from optimization results
   */
  static fromOptimizationResult(
    result: OptimizationResult,
    name?: string
  ): Portfolio {
    logger.debug("Creating portfolio model from optimization result");

    // Verify result structure to avoid undefined errors
    if (!result || !result.assets || !result.portfolio) {
      logger.error("Invalid optimization result structure", result);
      throw new Error(
        "Cannot create portfolio from invalid optimization result"
      );
    }

    return new Portfolio({
      name: name || `Optimized Portfolio ${new Date().toLocaleDateString()}`,
      assets: result.assets,
      expectedReturn: result.portfolio.expected_return,
      volatility: result.portfolio.volatility,
      sharpeRatio: result.portfolio.sharpe_ratio,
      sortinoRatio: result.portfolio.sortino_ratio,
      optimizationStrategy: result.portfolio.optimization_strategy,
    });
  }

  /**
   * Static factory method to optimize a new portfolio
   * Uses store for state management
   */
  static async optimize(
    params: PortfolioOptimizationParams
  ): Promise<Portfolio> {
    logger.debug("Starting portfolio optimization process");

    // Get store functions (without subscribing to state changes)
    const { updatePortfolio, updateError, updateLoading } =
      usePortfolioStore.getState();

    try {
      updateLoading("optimizeLoading", true);

      const result = await portfolioRepository.optimize(params);
      logger.info("Portfolio optimization completed successfully");

      const portfolio = Portfolio.fromOptimizationResult(result);

      // Update store with new portfolio
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      updatePortfolio(portfolio as any);

      return portfolio;
    } catch (error) {
      // Use the error handler to standardize the error format
      const standardizedError = apiErrorHandler.standardizeError(error);
      logger.error("Failed to optimize portfolio:", standardizedError);

      // Store the standardized error
      updateError(standardizedError);

      // Re-throw the standardized error
      throw standardizedError;
    } finally {
      updateLoading("optimizeLoading", false);
    }
  }

  /**
   * Get risk-adjusted return using Sharpe ratio
   */
  getRiskAdjustedReturn(): number {
    return this.sharpeRatio;
  }

  /**
   * Calculate diversification score based on asset weights
   * Returns a value between 0-100, where higher is better diversified
   */
  getDiversificationScore(): number {
    if (this.assets.length <= 1) return 0;

    // A simple diversification score based on how evenly distributed the weights are
    const idealWeight = 1 / this.assets.length;
    const weightDeviations = this.assets.map(
      (asset) => Math.abs(asset.weight - idealWeight) / idealWeight
    );

    const averageDeviation =
      weightDeviations.reduce((sum, dev) => sum + dev, 0) / this.assets.length;

    // Convert to a 0-100 scale where 100 is perfectly diversified
    return Math.max(0, Math.min(100, 100 * (1 - averageDeviation)));
  }

  /**
   * Convert to API format for saving/transmission
   */
  toApiFormat() {
    return {
      id: this.id,
      name: this.name,
      assets: this.assets,
      portfolio: {
        expected_return: this.expectedReturn,
        volatility: this.volatility,
        sharpe_ratio: this.sharpeRatio,
        sortino_ratio: this.sortinoRatio,
        optimization_strategy: this.optimizationStrategy,
      },
    };
  }
}

export default Portfolio;
