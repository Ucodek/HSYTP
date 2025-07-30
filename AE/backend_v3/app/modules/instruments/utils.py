from .models import InstrumentType, MarketType


def map_quote_type(quote_type: str) -> InstrumentType:
    """
    Map a yfinance quoteType string to the corresponding InstrumentType enum.

    Args:
        quote_type (str): The quoteType string from yfinance (e.g., 'EQUITY', 'INDEX').
    Returns:
        InstrumentType: The mapped enum value, or InstrumentType.OTHER if not recognized.
    """
    mapping = {
        "EQUITY": InstrumentType.STOCK,
        "INDEX": InstrumentType.INDEX,
        "ETF": InstrumentType.ETF,
        "CRYPTOCURRENCY": InstrumentType.CRYPTO,
        "CURRENCY": InstrumentType.FOREX,
    }

    return mapping.get(quote_type, InstrumentType.OTHER)


def map_market(market: str) -> MarketType:
    """
    Map yfinance market or exchange strings to the corresponding MarketType enum.

    Args:
        market (str): The market string from yfinance (e.g., 'IST', 'NYSE').
    Returns:
        MarketType: The mapped enum value, or MarketType.OTHER if not recognized.
    """
    mapping = {
        "IST": MarketType.BIST,
        "BIST": MarketType.BIST,
        # "Istanbul": MarketType.BIST,
        "NMS": MarketType.NASDAQ,
        "NASDAQ": MarketType.NASDAQ,
        "NIM": MarketType.NASDAQ,
        # "NasdaqGS": MarketType.NASDAQ,
        "NYSE": MarketType.NYSE,
        # "Crypto": MarketType.CRYPTO,
        # "Forex": MarketType.FOREX,
    }

    return mapping.get(market, MarketType.OTHER)


def map_market_to_yf_exchange(market: MarketType) -> str:
    """
    Map your MarketType enum to yfinance exchange code for use in yfinance screen API.
    Args:
        market (MarketType): Your MarketType enum value.
    Returns:
        str: yfinance exchange code (e.g., 'IST', 'NMS', 'NYSE'), or None if not mapped.
    """
    mapping = {
        MarketType.BIST: "IST",
        MarketType.NASDAQ: "NMS",
        MarketType.NYSE: "NYSE",
    }

    return mapping.get(market)
