import {
  Stock,
  EconomicEvent,
  NewsArticle,
  Post,
  MarketIndex,
  ExtendedMarketIndex,
  OptimizationResult,
} from "@/lib/types";

// Define the SearchItem type to ensure consistency
export type SearchItemType = "stock" | "index" | "crypto" | "etf";

export interface SearchItem {
  id: string;
  symbol: string;
  name: string;
  type: SearchItemType;
  price?: number;
  change?: number;
}

// Arama öğeleri için örnek veriler
export const MOCK_SEARCH_ITEMS: SearchItem[] = [
  {
    id: "1",
    symbol: "AAPL",
    name: "Apple Inc.",
    type: "stock",
    price: 172.62,
    change: 0.41,
  },
  {
    id: "2",
    symbol: "MSFT",
    name: "Microsoft Corporation",
    type: "stock",
    price: 326.67,
    change: -0.32,
  },
  {
    id: "3",
    symbol: "GOOGL",
    name: "Alphabet Inc.",
    type: "stock",
    price: 134.99,
    change: 0.87,
  },
  {
    id: "4",
    symbol: "AMZN",
    name: "Amazon.com Inc.",
    type: "stock",
    price: 126.75,
    change: 1.25,
  },
  {
    id: "5",
    symbol: "^GSPC",
    name: "S&P 500",
    type: "index",
    price: 4193.8,
    change: 0.53,
  },
  {
    id: "6",
    symbol: "^DJI",
    name: "Dow Jones Industrial Average",
    type: "index",
    price: 33670.29,
    change: -0.21,
  },
  {
    id: "7",
    symbol: "BTC-USD",
    name: "Bitcoin USD",
    type: "crypto",
    price: 36789.12,
    change: 2.35,
  },
  {
    id: "8",
    symbol: "ETH-USD",
    name: "Ethereum USD",
    type: "crypto",
    price: 2085.47,
    change: 1.18,
  },
  {
    id: "9",
    symbol: "SPY",
    name: "SPDR S&P 500 ETF Trust",
    type: "etf",
    price: 418.72,
    change: 0.48,
  },
  {
    id: "10",
    symbol: "QQQ",
    name: "Invesco QQQ Trust",
    type: "etf",
    price: 367.3,
    change: 0.74,
  },
];

// Kazandıran hisse senetleri için örnek veriler
export const MOCK_TOP_GAINERS: Stock[] = [
  {
    symbol: "AAPL",
    name: "Apple Inc.",
    price: 145.67,
    change: 3.25,
    change_percent: 2.3,
    volume: 2345000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "TSLA",
    name: "Tesla, Inc.",
    price: 210.45,
    change: 12.65,
    change_percent: 6.4,
    volume: 5623000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "AMZN",
    name: "Amazon.com Inc.",
    price: 126.78,
    change: 4.38,
    change_percent: 3.58,
    volume: 3456000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "NVDA",
    name: "NVIDIA Corporation",
    price: 432.95,
    change: 21.45,
    change_percent: 5.22,
    volume: 6789000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "AMD",
    name: "Advanced Micro Devices, Inc.",
    price: 102.33,
    change: 3.89,
    change_percent: 3.95,
    volume: 2198000,
    country: "USA",
    currency: "USD",
  },
];

// Kaybettiren hisse senetleri için örnek veriler
export const MOCK_TOP_LOSERS: Stock[] = [
  {
    symbol: "META",
    name: "Meta Platforms, Inc.",
    price: 178.32,
    change: -8.45,
    change_percent: -4.52,
    volume: 4325000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "INTC",
    name: "Intel Corporation",
    price: 34.21,
    change: -1.54,
    change_percent: -4.31,
    volume: 1987000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "DIS",
    name: "The Walt Disney Company",
    price: 89.76,
    change: -3.21,
    change_percent: -3.45,
    volume: 2456000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "NFLX",
    name: "Netflix, Inc.",
    price: 365.42,
    change: -12.34,
    change_percent: -3.27,
    volume: 1678000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "PYPL",
    name: "PayPal Holdings, Inc.",
    price: 65.43,
    change: -2.76,
    change_percent: -4.05,
    volume: 1543000,
    country: "USA",
    currency: "USD",
  },
];

// En aktif hisse senetleri için örnek veriler
export const MOCK_MOST_ACTIVE: Stock[] = [
  {
    symbol: "AAPL",
    name: "Apple Inc.",
    price: 145.67,
    change: 3.25,
    change_percent: 2.3,
    volume: 23450000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "MSFT",
    name: "Microsoft Corporation",
    price: 267.89,
    change: 1.23,
    change_percent: 0.46,
    volume: 18970000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "TSLA",
    name: "Tesla, Inc.",
    price: 210.45,
    change: 12.65,
    change_percent: 6.4,
    volume: 15623000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "NVDA",
    name: "NVIDIA Corporation",
    price: 432.95,
    change: 21.45,
    change_percent: 5.22,
    volume: 12789000,
    country: "USA",
    currency: "USD",
  },
  {
    symbol: "BAC",
    name: "Bank of America Corporation",
    price: 28.76,
    change: -0.45,
    change_percent: -1.54,
    volume: 11567000,
    country: "USA",
    currency: "USD",
  },
];

// Ekonomik olaylar için örnek veriler
export const MOCK_ECONOMIC_EVENTS: EconomicEvent[] = [
  {
    timestamp: 1676983800,
    event: "Federal Reserve Interest Rate Decision",
    country: "USA",
    impact: "high",
    previous_value: 5.25,
    forecast_value: 5.5,
    actual_value: 5.55,
    unit: "%",
  },
  {
    timestamp: 1677070200,
    event: "Initial Jobless Claims",
    country: "USA",
    impact: "medium",
    previous_value: 210,
    forecast_value: 225,
    actual_value: 220,
    unit: "K",
  },
  {
    timestamp: 1677156600,
    event: "GDP Growth Rate QoQ Adv",
    country: "USA",
    impact: "high",
    previous_value: 2.1,
    forecast_value: 2.0,
    actual_value: null,
    unit: "%",
  },
  {
    timestamp: 1677243000,
    event: "Consumer Price Index YoY",
    country: "EUR",
    impact: "low",
    previous_value: 3.4,
    forecast_value: 3.2,
    actual_value: 3.1,
    unit: "%",
  },
  {
    timestamp: 1677329400,
    event: "Retail Sales MoM",
    country: "JPN",
    impact: "medium",
    previous_value: 0.7,
    forecast_value: 0.8,
    actual_value: null,
    unit: "%",
  },
];

// Piyasa endeksleri için örnek veriler
export const MOCK_MARKET_INDICES: MarketIndex[] = [
  {
    symbol: "^GSPC",
    name: "S&P 500",
    country: "USA",
    currency: "USD",
    last_price: 4298.65,
    change: 28.37,
    change_percent: 0.66,
  },
  {
    symbol: "^IXIC",
    name: "NASDAQ Composite",
    country: "USA",
    currency: "USD",
    last_price: 13533.75,
    change: 159.39,
    change_percent: 1.19,
  },
  {
    symbol: "^GDAXI",
    name: "DAX",
    country: "GER",
    currency: "EUR",
    last_price: 15476.43,
    change: 82.91,
    change_percent: 0.54,
  },
  {
    symbol: "^N225",
    name: "Nikkei 225",
    country: "JPN",
    currency: "JPY",
    last_price: 27587.46,
    change: -48.31,
    change_percent: -0.17,
  },
];

// BIST 100 gibi detaylı piyasa endeksi örneği
export const MOCK_BIST100: ExtendedMarketIndex = {
  symbol: "^BIST",
  name: "BIST 100",
  country: "Turkey",
  currency: "TRY",
  last_price: 8924.32,
  change: 78.45,
  change_percent: 0.89,
  volume: 5240000,
  previous_close: 8845.87,
  "52_w_high_price": 9200.1,
  "52_w_low_price": 8200.35,
  day_high_price: 8950.2,
  day_low_price: 8890.15,
};

// Türk borsası hisseleri için örnek veriler
export const MOCK_TURKISH_STOCKS: Stock[] = [
  {
    symbol: "THYAO",
    name: "Türk Hava Yolları",
    price: 245.67,
    change: 3.25,
    change_percent: 1.35,
    volume: 2345000,
    country: "Turkey",
    currency: "TRY",
  },
  {
    symbol: "GARAN",
    name: "Garanti Bankası",
    price: 36.8,
    change: 0.6,
    change_percent: 1.66,
    volume: 1845000,
    country: "Turkey",
    currency: "TRY",
  },
  {
    symbol: "YKBNK",
    name: "Yapı Kredi Bankası",
    price: 12.5,
    change: 0.25,
    change_percent: 2.04,
    volume: 3012000,
    country: "Turkey",
    currency: "TRY",
  },
  {
    symbol: "AKBNK",
    name: "Akbank",
    price: 28.35,
    change: 1.15,
    change_percent: 4.23,
    volume: 3215000,
    country: "Turkey",
    currency: "TRY",
  },
  {
    symbol: "EREGL",
    name: "Ereğli Demir Çelik",
    price: 32.44,
    change: -0.56,
    change_percent: -1.7,
    volume: 2865000,
    country: "Turkey",
    currency: "TRY",
  },
  {
    symbol: "ASELS",
    name: "Aselsan",
    price: 42.64,
    change: -0.84,
    change_percent: -2.01,
    volume: 1945000,
    country: "Turkey",
    currency: "TRY",
  },
  {
    symbol: "KCHOL",
    name: "Koç Holding",
    price: 92.83,
    change: -1.25,
    change_percent: -1.33,
    volume: 1956000,
    country: "Turkey",
    currency: "TRY",
  },
  {
    symbol: "PGSUS",
    name: "Pegasus Hava Taşımacılığı",
    price: 182.50,
    change: -8.35,
    change_percent: -4.38,
    volume: 2785000,
    country: "Turkey",
    currency: "TRY",
  },
];

// Haberler için örnek veriler
export const MOCK_NEWS: NewsArticle[] = [
  {
    timestamp: 1676983800,
    title: "US Federal Reserve Raises Interest Rates",
    source: "Reuters",
    url: "https://www.reuters.com/article/usa-fed-rate-increase-idUS12345",
    summary:
      "The Federal Reserve raised its key interest rate by 0.25% to curb inflation and stabilize the economy.",
    cover:
      "https://images.pexels.com/photos/518543/pexels-photo-518543.jpeg?auto=compress&cs=tinysrgb&w=600",
  },
  {
    timestamp: 1676980200,
    title: "Tech Stocks Rally as Investor Confidence Returns to Market",
    source: "Bloomberg",
    url: "https://www.bloomberg.com/news/articles/tech-stocks-rally",
    summary:
      "Major technology stocks saw significant gains today as investors returned to growth sectors following positive earnings reports.",
    cover:
      "https://images.pexels.com/photos/3183197/pexels-photo-3183197.jpeg?auto=compress&cs=tinysrgb&w=600",
  },
  {
    timestamp: 1676976600,
    title: "Oil Prices Fall Amid Global Economic Concerns",
    source: "Financial Times",
    url: "https://www.ft.com/content/oil-prices-fall",
    summary:
      "Crude oil prices dropped by 3% today as concerns about global economic slowdown affected commodity markets worldwide.",
    cover:
      "https://images.pexels.com/photos/208670/pexels-photo-208670.jpeg?auto=compress&cs=tinysrgb&w=600",
  },
  {
    timestamp: 1676973000,
    title: "European Markets Close Higher Following ECB Announcement",
    source: "CNBC",
    url: "https://www.cnbc.com/europe-markets-higher",
    summary:
      "European stock indices closed higher after the European Central Bank signaled a potential pause in interest rate hikes.",
    cover:
      "https://images.pexels.com/photos/3183197/pexels-photo-3183197.jpeg?auto=compress&cs=tinysrgb&w=600",
  },
];

// Blog yazıları için örnek veriler
export const MOCK_POSTS: Post[] = [
  {
    timestamp: 1676983800,
    title: "Understanding Stock Market Trends",
    url: "/insights/understanding-stock-market-trends",
    summary:
      "Learn how to interpret stock market trends and make better investment decisions. This guide covers technical analysis basics and pattern recognition.",
    category: "Analysis",
  },
  {
    timestamp: 1676897400,
    title: "Top 5 Investment Strategies for 2023",
    url: "/insights/top-investment-strategies-2023",
    summary:
      "Discover the most effective investment strategies that financial experts are recommending for the current economic climate.",
    category: "Investing",
  },
  {
    timestamp: 1676811000,
    title: "How to Build a Diversified Portfolio",
    url: "/insights/build-diversified-portfolio",
    summary:
      "Protecting your investments through diversification is key to long-term success. Learn how to create a well-balanced portfolio across different asset classes.",
    category: "Portfolio",
  },
  {
    timestamp: 1676724600,
    title: "Understanding Market Volatility",
    url: "/insights/understanding-market-volatility",
    summary:
      "Market volatility can be intimidating, but it also creates opportunities. Learn how to navigate volatile markets and make informed decisions.",
    category: "Markets",
  },
];

// Portfolio optimization mock data
export const MOCK_OPTIMIZATION_RESULT: OptimizationResult = {
  assets: [
    {
      symbol: "AAPL",
      name: "Apple Inc.",
      weight: 0.25,
      expected_return: 0.08,
      volatility: 0.15,
      correlation: 0.2,
    },
    {
      symbol: "TSLA",
      name: "Tesla Inc.",
      weight: 0.35,
      expected_return: 0.12,
      volatility: 0.2,
      correlation: 0.3,
    },
    {
      symbol: "AMZN",
      name: "Amazon Inc.",
      weight: 0.25,
      expected_return: 0.08,
      volatility: 0.15,
      correlation: 0.2,
    },
    {
      symbol: "MSFT",
      name: "Microsoft Corporation",
      weight: 0.15,
      expected_return: 0.07,
      volatility: 0.12,
      correlation: 0.18,
    },
  ],
  risk_distribution: [
    {
      symbol: "TSLA",
      percentage: 0.35,
      risk_score: 0.85,
    },
    {
      symbol: "AAPL",
      percentage: 0.25,
      risk_score: 0.45,
    },
    {
      symbol: "AMZN",
      percentage: 0.2,
      risk_score: 0.55,
    },
    {
      symbol: "MSFT",
      percentage: 0.2,
      risk_score: 0.35,
    },
  ],
  backtesting_results: {
    "1_year_return": 0.12,
    "3_year_return": 0.15,
    "5_year_return": 0.18,
  },
  portfolio: {
    expected_return: 0.1,
    volatility: 0.12,
    sharpe_ratio: 1.5,
    sortino_ratio: 2.0,
    optimization_strategy: 3,
  },
};
