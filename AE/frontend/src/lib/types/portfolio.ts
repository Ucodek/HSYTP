/**
 * Core types for portfolio optimization feature
 */

export interface Asset {
  symbol: string;
  name: string;
  weight: number;
  expected_return: number;
  volatility: number;
  correlation?: number;
}

export interface PortfolioOptimizationParams {
  exchange: string;
  portfolio_creation_date: Date;
  training_period_days: number;
  optimization_strategy: number;
  number_of_assets: number;
  custom_weights?: Record<string, number>; // For custom weight strategy
}

export interface PortfolioMetrics {
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  optimization_strategy: number;
}

export interface RiskDistribution {
  labels: string[];
  values: number[];
}

export interface BacktestResult {
  date: string;
  portfolio_value: number;
  benchmark_value: number;
}

export interface OptimizationResult {
  portfolio: PortfolioMetrics;
  assets: Asset[];
  risk_distribution: RiskDistribution;
  backtesting_results: BacktestResult[];
}
