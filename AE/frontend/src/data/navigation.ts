import { ProductId } from "@/data/products";

// Navigation link IDs - used as keys for internationalization
export enum NavLinkId {
  HOME = "home",
  PRODUCTS = "products",
  MARKET = "market",
  NEWS = "news",
}

// Types for navigation link

// Define navigation link interface
export interface NavLink {
  id: string;
  href: string;
  enabled: boolean;
}

// Define navigation link with children interface
export interface NavLinkItem extends NavLink {
  children?: NavLink[];
}

// Centralized navigation data
export const NAV_LINKS: NavLinkItem[] = [
  {
    id: NavLinkId.HOME,
    href: "/",
    enabled: true,
  },
  {
    id: NavLinkId.PRODUCTS,
    href: "/products",
    enabled: true,
    children: [
      {
        id: ProductId.PORTFOLIO_OPTIMIZATION,
        href: "/products/portfolio-optimization",
        enabled: true,
      },
      {
        id: ProductId.MARKET_ANALYSIS,
        href: "/products/market-analysis",
        enabled: true,
      },
      {
        id: ProductId.INVESTMENT_INSIGHTS,
        href: "/products/investment-insights",
        enabled: true,
      },
      {
        id: ProductId.TRADING_ALERTS,
        href: "/products/trading-alerts",
        enabled: true,
      },
    ],
  },
  {
    id: NavLinkId.MARKET,
    href: "/market",
    enabled: true,
  },
  {
    id: NavLinkId.NEWS,
    href: "/news",
    enabled: true,
  },
];

// Helper function to get only enabled navigation links
export const getEnabledNavLinks = (): NavLink[] => {
  return NAV_LINKS.filter((link) => link.enabled);
};

// Helper function to get navigation link by ID
export const getNavLinkById = (id: NavLinkId): NavLink | undefined => {
  return NAV_LINKS.find((link) => link.id === id);
};

// Helper function to get only enabled child navigation links
export const getEnabledChildNavLinks = (id: NavLinkId): NavLink[] => {
  const parent = NAV_LINKS.find((link) => link.id === id);

  if (!parent || !parent.children) {
    return [];
  }

  return parent.children.filter((link) => link.enabled);
};
