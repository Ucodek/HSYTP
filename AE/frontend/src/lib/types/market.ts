/**
 * Piyasa ve finansal verilere ilişkin tip tanımlamaları
 */

/**
 * Hisse senedi veri tipi
 */
export interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  country: string;
  currency: string;
}

/**
 * Basit market indeksi veri tipi
 */
export interface MarketIndex {
  symbol: string;
  name: string;
  country: string;
  currency: string;
  last_price: number;
  change: number;
  change_percent: number;
}

/**
 * Genişletilmiş market indeksi veri tipi (daha detaylı)
 */
export interface ExtendedMarketIndex extends MarketIndex {
  volume: number;
  previous_close: number;
  "52_w_high_price": number;
  "52_w_low_price": number;
  day_high_price: number;
  day_low_price: number;
}

/**
 * Ekonomik olay veri tipi
 */
export interface EconomicEvent {
  timestamp: number;
  event: string;
  country: string;
  impact: "low" | "medium" | "high";
  previous_value: number | null;
  forecast_value: number | null;
  actual_value: number | null;
  unit: string;
}

/**
 * Badge varyasyonları
 */
export type BadgeVariant = "default" | "secondary" | "outline" | "destructive";
