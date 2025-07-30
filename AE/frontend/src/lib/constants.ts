import { TrendStyles } from "@/lib/types";

export const NAV_LINKS = [
  {
    href: "/",
    key: "home",
  },
  {
    href: "/products",
    key: "products",
    children: [
      {
        href: "/products/portfolio-optimization",
        key: "portfolioOptimization",
      },
      {
        href: "/products/market-analysis",
        key: "marketAnalysis",
      },
      // {
      //   href: "/products/portfolio-tracker",
      //   key: "portfolioTracker",
      // },
      {
        href: "/products/investment-insights",
        key: "investmentInsights",
      },
      {
        href: "/products/trading-alerts",
        key: "tradingAlerts",
      },
    ],
  },
  {
    href: "/market",
    key: "market",
  },
  {
    href: "/news",
    key: "news",
  },
];

// Trend stillerinin merkezi tanımlanması
export const TREND_STYLES: TrendStyles = {
  positive: {
    text: "text-green-600 dark:text-green-500",
    price: "text-green-600/90 dark:text-green-500",
    bg: "bg-green-600 dark:bg-green-500",
    hover:
      "hover:border-green-500/30 hover:bg-green-500/5 dark:hover:border-green-500/70 dark:hover:bg-green-500/10",
  },
  negative: {
    text: "text-red-600 dark:text-red-500",
    price: "text-red-600/90 dark:text-red-500",
    bg: "bg-red-600 dark:bg-red-500",
    hover:
      "hover:border-red-500/30 hover:bg-red-500/5 dark:hover:border-red-500/70 dark:hover:bg-red-500/10",
  },
};
