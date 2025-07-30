"""Configuration for instruments module."""

# Define standard sort fields to use across all instrument endpoints
INSTRUMENT_SORT_FIELDS = {
    "sort_allowed_fields": [
        "symbol",
        "type",
        "exchange",
        "country",
        "currency",
        "current_price",
    ],
    "sort_field_map": {
        "price": "current_price",
        "price_change": "price_change_percent",
    },
    "default_sort_field": "symbol",
}
