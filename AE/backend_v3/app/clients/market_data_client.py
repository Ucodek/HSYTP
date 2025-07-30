import concurrent.futures
from datetime import datetime, timezone
from typing import List

import yfinance as yf
from fastcore.logging.manager import ensure_logger

from app.modules.instruments.utils import map_market, map_quote_type

logger = ensure_logger(None, __name__)


class MarketDataClient:
    """
    Client for fetching real-time and historical market data for indices and stocks.
    Uses yfinance as the backend. Can be extended for other providers.
    """

    @staticmethod
    def _format_instrument(info) -> dict:
        """
        Extract and format instrument (static) fields from yfinance info dict.
        """
        # pprint(info)

        country = (
            info.get("market").split("_")[0].upper() if info.get("market") else None
        )

        return {
            "symbol": info.get("symbol"),
            "name": info.get("longName") or info.get("shortName"),
            "type": map_quote_type(info.get("quoteType", "")),
            "market": map_market(
                # info.get("market", ""),  # tr_market, us_market, etc.
                info.get("exchange", ""),  # IST, NMS, NYSE, etc.
                # info.get("fullExchangeName", ""),  # Istanbul, NasdaqGS, etc.
            ),
            "currency": info.get("currency"),
            # "country": info.get("country") or country,
            "country": country,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "is_active": info.get("tradeable", True),
            # NOTE: Some fields are commented out as they may not be relevant for all use cases.
            # market_cap: info.get("marketCap"),
            # market_state: info.get("marketState"),
            # avg_analyst_rating: info.get("averageAnalystRating"), # 1.3 - Strong Buy, 2.1 - Buy, etc.
            # avg_volume: info.get("averageVolume"),
        }

    @staticmethod
    def _format_history(row, info, idx) -> dict:
        """
        Extract and format price history (time series) fields from yfinance row and info dict.
        """
        # High: day high
        # Low: day low
        # Open: day open
        # Close: current price or last price

        open_price = float(row.get("Open", 0))
        close_price = float(row.get("Close", 0))

        def get_val(info_key, row_key=None, default=None, cast=float):
            if row_key and row.get(row_key) is not None:
                return cast(row[row_key])
            if info.get(info_key) is not None:
                return cast(info[info_key])
            return default

        prev_close = info.get("regularMarketPreviousClose")
        if prev_close is None:
            prev_close = info.get("previousClose")
        if prev_close is None:
            prev_close = row.get("Close", 0)

        if isinstance(idx, datetime):
            market_timestamp = idx
        else:
            market_timestamp = datetime.now(timezone.utc)

        return {
            "price": get_val("regularMarketPrice", "Close"),
            "change": get_val("regularMarketChange", None, close_price - open_price),
            "change_percent": get_val("regularMarketChangePercent", None, None),
            "volume": get_val("regularMarketVolume", "Volume", 0, int),
            "day_high": get_val("regularMarketDayHigh", "High"),
            "day_low": get_val("regularMarketDayLow", "Low"),
            "previous_close": float(prev_close),
            "w52_high": get_val("fiftyTwoWeekHigh", None, close_price),
            "w52_low": get_val("fiftyTwoWeekLow", None, close_price),
            "market_timestamp": market_timestamp,
        }

    @staticmethod
    def _format_row(row, info, idx) -> dict:
        """
        Merge instrument and price history fields for a single time point.
        """
        instrument_fields = MarketDataClient._format_instrument(info)
        price_fields = MarketDataClient._format_history(row, info, idx)
        return {**instrument_fields, **price_fields}

    @staticmethod
    def get_historical_data(
        symbol: str, period: str = "5y", interval: str = "1d"
    ) -> List[dict]:
        """
        Fetches historical market data for a given symbol.
        Args:
            symbol (str): The stock or index symbol to fetch data for.
            period (str): The period for which to fetch data. Default is "5y".
            interval (str): The interval for the data. Default is "1d".
        Returns:
            list: A list of dictionaries containing market data.
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                logger.warning(f"No historical data found for symbol: {symbol}")
                return []

            info = getattr(ticker, "info", {})

            return [
                MarketDataClient._format_row(row, info, idx)
                for idx, row in hist.iterrows()
            ]
        except Exception as e:
            logger.error(f"Error fetching historical data for symbol {symbol}: {e}")
            return []

    @staticmethod
    def get_latest_market_data(symbol: str, period: str = "1d") -> dict:
        """
        Fetches the latest market data for a given symbol (stock or index).
        Args:
            symbol (str): The symbol to fetch data for.
            period (str): The period for which to fetch data. Default is "1d".
        Returns:
            dict: A dictionary containing the latest market data for the symbol.
        """
        data = MarketDataClient.get_historical_data(
            symbol, period=period, interval="15m"
        )
        return data[-1] if data else None

    @staticmethod
    def get_symbols_by_index(index_symbol: str) -> List[str]:
        """
        Fetch constituent stock symbols for a given index symbol from TradingView's index component API.

        Args:
            index_symbol (str): Example: "BIST;XU100" or "NASDAQ;NDX" or "SP:SPX"

        Returns:
            List[str]: List of stock symbols that are components of the given index.
        """
        import requests

        headers = {
            "accept": "application/json",
            "content-type": "text/plain;charset=UTF-8",
            # "origin": "https://www.tradingview.com",
            # "referer": "https://www.tradingview.com/",
            # "user-agent": "Mozilla/5.0",
        }

        payload = {
            "columns": ["name"],
            # "ignore_unknown_fields": False,
            # "options": {"lang": "en"},
            # "range": [0, 10],
            # "sort": {
            #     "sortBy": "market_cap_basic",
            #     "sortOrder": "desc",
            #     "nullsFirst": False,
            # },
            "symbols": {"symbolset": [f"SYML:{index_symbol}"]},
            # "preset": "index_components_market_pages",
        }

        response = requests.post(
            "https://scanner.tradingview.com/global/scan?label-product=symbols-components",
            headers=headers,
            json=payload,
        )

        response.raise_for_status()

        result = response.json()
        # pprint(result)
        # return [item["d"][0] for item in result.get("data", [])]

        # if the symbols from BIST, add ".IS" to the end of each symbol
        symbols = [
            item["d"][0] + ".IS" if item["s"].startswith("BIST") else item["d"][0]
            for item in result.get("data", [])
        ]
        return symbols

    @staticmethod
    def get_stocks_by_index(
        index_symbol: str,
        # size: int = 10,
        batch_size: int = 25,
        max_workers: int = 8,
    ) -> List[dict]:
        """
        Fetch all stock instrument info for a given exchange using yfinance's screening API, in parallel batches.

        This method first collects all stock symbols for the specified exchange using yfinance's screening API.
        It then fetches instrument info for these symbols in parallel batches using ThreadPoolExecutor for improved performance.
        Each batch is fetched using yfinance's batch API (yf.Tickers), and results are merged into a single list.
        Handles pagination, batching, and errors gracefully.

        Args:
            exchange (str): Exchange code (e.g., 'IST' for BIST, 'NMS' for NASDAQ, 'NYSE' for New York Stock Exchange).
            size (int): Number of results to fetch per screening API call (pagination size).
            batch_size (int): Number of symbols per batch for info fetching (yfinance batch API).
            max_workers (int): Number of threads to use for parallel fetching of batches.
        Returns:
            List[dict]: List of instrument info dicts for all stocks on the exchange.
        """

        # symbols = []
        stocks = []
        # offset = 0

        # Collect all symbols
        # while True:
        # q = yf.EquityQuery("is-in", ["exchange", exchange])
        # response = yf.screen(q, size=size, offset=offset)

        # if not response or "quotes" not in response or not response["quotes"]:
        #     break

        # symbols.extend([item["symbol"] for item in response["quotes"]])

        # if len(response["quotes"]) < size:
        #     break

        # offset += size

        symbols = MarketDataClient.get_symbols_by_index(index_symbol)

        logger.info(f"Fetched {len(symbols)} symbols from index {index_symbol}")
        # pprint(symbols)

        def fetch_batch(batch):
            tickers_str = ",".join(batch)
            result = yf.Tickers(tickers_str)
            batch_stocks = []
            for symbol in batch:
                try:
                    ticker_obj = result.tickers.get(symbol)
                    if ticker_obj and ticker_obj.info:
                        batch_stocks.append(
                            MarketDataClient._format_instrument(ticker_obj.info)
                        )
                except Exception as e:
                    logger.warning(f"Failed to fetch info for {symbol}: {e}")
            return batch_stocks

        # Fetch info in parallel batches
        batches = [
            symbols[i : i + batch_size] for i in range(0, len(symbols), batch_size)
        ]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_batch, batch) for batch in batches]
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                batch_result = future.result()
                stocks.extend(batch_result)
                logger.info(f"Fetched info for {len(batch_result)} stocks in batch {i}")

        logger.info(f"Fetched info for {len(stocks)} stocks from index {index_symbol}")
        return stocks
