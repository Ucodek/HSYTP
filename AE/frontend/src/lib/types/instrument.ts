// Instrument types for the frontend, matching backend_v3 instrument schemas

import { ListResponse } from "./response";

export enum InstrumentType {
  STOCK = "stock",
  ETF = "etf",
  CRYPTO = "crypto",
  INDEX = "index",
  FOREX = "forex",
  OTHER = "other",
}

export enum MarketType {
  NASDAQ = "nasdaq",
  NYSE = "nyse",
  BIST = "bist",
  CRYPTO = "crypto",
  FOREX = "forex",
  OTHER = "other",
}

export interface InstrumentBase {
  symbol: string;
  name: string;
  type: InstrumentType;
  market: MarketType;
  currency: string;
  country?: string;
  sector?: string;
  industry?: string;
  is_active: boolean;
}

export interface InstrumentResponse extends InstrumentBase {
  id: number;
  created_at?: Date;
  updated_at?: Date;
}

export interface InstrumentWithLatestPriceResponse extends InstrumentResponse {
  price?: number;
  market_timestamp?: Date;
  change?: number;
  change_percent?: number;
  volume?: number;
  day_high?: number;
  day_low?: number;
  w52_high?: number;
  w52_low?: number;
  previous_close?: number;
}

export interface InstrumentListQuery {
  page: number;
  page_size: number;
  symbol?: string;
  name?: string;
  type?: InstrumentType;
  market?: MarketType;
  currency?: string;
  country?: string;
  sector?: string;
  industry?: string;
  is_active?: boolean;
}

export type ListInstrumentResponse = ListResponse<InstrumentResponse>;

export type ListInstrumentWithLatestPriceResponse =
  ListResponse<InstrumentWithLatestPriceResponse>;
