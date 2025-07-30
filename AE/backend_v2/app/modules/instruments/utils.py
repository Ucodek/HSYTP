"""
Utility functions for the instruments module.
"""
from typing import Any, Optional

from app.utils.i18n import TranslatedText


def safe_numeric(value: Any) -> Optional[float]:
    """
    Safely convert any numeric value to float.

    Args:
        value: Value to convert (can be int, float, Decimal, or None)

    Returns:
        Converted float value or None if input is None
    """
    if value is None:
        return None
    return float(value)


def get_translated_text(
    field: Optional[TranslatedText], language: str
) -> Optional[str]:
    """
    Extract text in specified language from TranslatedField with proper None handling.

    Args:
        field: TranslatedText field or None
        language: Language code to extract

    Returns:
        Extracted text, None if field is None, or empty string if translation not available
    """
    if field is None:
        return None
    text = field.get_text(language)
    return text if text else None  # Return None instead of empty string
