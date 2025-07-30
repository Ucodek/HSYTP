import { BarChart3, LineChart, PieChart, TrendingUp } from "lucide-react";

// Product IDs - used as keys for internationalization and routing
export enum ProductId {
  PORTFOLIO_OPTIMIZATION = "portfolioOptimization",
  MARKET_ANALYSIS = "marketAnalysis",
  INVESTMENT_INSIGHTS = "investmentInsights",
  TRADING_ALERTS = "tradingAlerts",
}

// Define the product interface
export interface Product {
  id: ProductId;
  icon: React.ElementType;
  href: string;
  enabled: boolean; // Easily enable/disable products
}

// Centralized product data
export const PRODUCTS: Product[] = [
  {
    id: ProductId.PORTFOLIO_OPTIMIZATION,
    icon: BarChart3,
    href: "/products/portfolio-optimization",
    enabled: true,
  },
  {
    id: ProductId.MARKET_ANALYSIS,
    icon: LineChart,
    href: "/products/market-analysis",
    enabled: true,
  },
  {
    id: ProductId.INVESTMENT_INSIGHTS,
    icon: PieChart,
    href: "/products/investment-insights",
    enabled: true,
  },
  {
    id: ProductId.TRADING_ALERTS,
    icon: TrendingUp,
    href: "/products/trading-alerts",
    enabled: true,
  },
  // Example of a disabled product - can be easily enabled later
  // {
  //   id: "portfolioTracker",
  //   icon: BarChart3,
  //   href: "/products/portfolio-tracker",
  //   enabled: false,
  // },
];

// Helper function to get only enabled products
export const getEnabledProducts = (): Product[] => {
  return PRODUCTS.filter(product => product.enabled);
};

// Helper function to get product by ID
export const getProductById = (id: ProductId): Product | undefined => {
  return PRODUCTS.find(product => product.id === id);
};
