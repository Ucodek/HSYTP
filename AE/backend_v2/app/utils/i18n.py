import json
import os
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional

from fastapi import Depends, Header, Request
from pydantic import BaseModel, Field
from sqlalchemy import JSON, Column
from sqlalchemy.ext.mutable import MutableDict

# Default language and supported languages configuration
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "tr"]

# Language mappings for UI display
LANGUAGE_MAPPINGS = {
    "en": "English",
    "tr": "Turkish",
}

# In-memory translation cache
_translations: Dict[str, Dict[str, str]] = {}


# SQLAlchemy translation model components
class TranslatedText(MutableDict):
    """Custom mutable dictionary for storing translated text in SQLAlchemy."""

    def get_text(self, language: str = DEFAULT_LANGUAGE) -> str:
        """
        Get text in specified language, falling back to default if not available.

        Args:
            language: Language code to retrieve

        Returns:
            Text in requested language or default language if not available
        """
        if language in self and self[language]:
            return self[language]
        return self.get(DEFAULT_LANGUAGE, "")


def translated_column(**kwargs) -> Column:
    """
    Create a column for storing translated text.

    Args:
        **kwargs: Additional arguments to pass to the Column constructor

    Returns:
        SQLAlchemy column configured for translations
    """
    return Column(MutableDict.as_mutable(JSON), default={}, **kwargs)


# Pydantic schema for translated fields
class TranslatedField(BaseModel):
    """Model for handling translated fields in API requests/responses."""

    en: str = Field(..., description="English text (required)")
    tr: Optional[str] = Field(None, description="Turkish text")

    def get(self, language: str = DEFAULT_LANGUAGE) -> str:
        """
        Get text in specified language, falling back to default if not available.

        Args:
            language: Language code to retrieve

        Returns:
            Text in requested language or default language if not available
        """
        if hasattr(self, language) and getattr(self, language):
            return getattr(self, language)
        return getattr(self, DEFAULT_LANGUAGE, "")

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "TranslatedField":
        """
        Create a TranslatedField from a dictionary.

        Args:
            data: Dictionary mapping language codes to translations

        Returns:
            TranslatedField instance
        """
        if not data:
            return cls(en="")

        # Create instance with values from dictionary
        field_data = {"en": data.get("en", "")}

        # Add other supported languages if present
        for lang in SUPPORTED_LANGUAGES:
            if lang != "en" and lang in data:
                field_data[lang] = data[lang]

        return cls(**field_data)

    def to_dict(self) -> Dict[str, str]:
        """
        Convert to a dictionary representation.

        Returns:
            Dictionary mapping language codes to translations
        """
        result = {}
        for lang in SUPPORTED_LANGUAGES:
            if hasattr(self, lang) and getattr(self, lang):
                result[lang] = getattr(self, lang)
        return result


@lru_cache(maxsize=10)
def load_translations(language: str) -> Dict[str, str]:
    """
    Load translations for a language from translation files.

    Args:
        language: Language code

    Returns:
        Dictionary of translations
    """
    if language in _translations:
        return _translations[language]

    # Define the path to the translation file
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    translation_path = os.path.join(base_dir, "translations", f"{language}.json")

    # If the file exists, load it; otherwise use an empty dict
    if os.path.exists(translation_path):
        with open(translation_path, "r", encoding="utf-8") as file:
            translations = json.load(file)
    else:
        translations = {}

    # Cache the translations
    _translations[language] = translations

    return translations


def get_translation(key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    Get a translated string for a key.

    Args:
        key: Translation key
        language: Language code
        **kwargs: Format parameters for the translation

    Returns:
        Translated string, or the key itself if no translation exists
    """
    translations = load_translations(language)
    translated = translations.get(key, key)

    # Apply format parameters if provided
    if kwargs and isinstance(translated, str):
        try:
            translated = translated.format(**kwargs)
        except KeyError:
            # If formatting fails, return the untranslated string
            pass

    return translated


def get_supported_languages() -> Dict[str, str]:
    """
    Get a dictionary of supported languages.

    Returns:
        Dictionary mapping language codes to language names
    """
    return LANGUAGE_MAPPINGS


def parse_accept_language(
    accept_language: Optional[str],
    supported_languages: Optional[List[str]] = None,
    default_language: str = DEFAULT_LANGUAGE,
) -> str:
    """
    Parse the Accept-Language header and determine the best language match.

    Args:
        accept_language: Accept-Language header value
        supported_languages: List of supported language codes
        default_language: Default language if no match is found

    Returns:
        Language code
    """
    if supported_languages is None:
        supported_languages = SUPPORTED_LANGUAGES

    if not accept_language:
        return default_language

    # Parse the Accept-Language header
    languages = []
    for language_option in accept_language.split(","):
        parts = language_option.strip().split(";q=")
        language = parts[0].strip().lower()
        language_base = language.split("-")[
            0
        ]  # Get base language (e.g., 'en' from 'en-US')

        # Determine quality factor
        quality = 1.0
        if len(parts) > 1:
            try:
                quality = float(parts[1])
            except ValueError:
                pass

        languages.append((language, language_base, quality))

    # Sort by quality factor, highest first
    languages.sort(key=lambda x: x[2], reverse=True)

    # Find best match
    for _, language_base, _ in languages:
        if language_base in supported_languages:
            return language_base

    return default_language


def get_language(
    accept_language: Optional[str] = Header(None, alias="Accept-Language"),
    request: Optional[Request] = None,
) -> str:
    """
    FastAPI dependency to get language preference.

    Order of precedence:
    1. Language from the Accept-Language header
    2. Language from request state (set by middleware)
    3. Default language

    Args:
        accept_language: Accept-Language header
        request: FastAPI request object

    Returns:
        Language code
    """
    # First check Accept-Language header
    if accept_language:
        language = parse_accept_language(accept_language)
        return language

    # Then check request state (set by middleware)
    if request and hasattr(request.state, "language"):
        return request.state.language

    # Fall back to default language
    return DEFAULT_LANGUAGE


def set_language(response, language: str) -> None:
    """
    Set the language cookie in the response.

    Args:
        response: FastAPI response
        language: Language code
    """
    response.set_cookie(
        key="language",
        value=language,
        max_age=60 * 60 * 24 * 30,  # 30 days
        path="/",
        httponly=True,
        samesite="lax",
    )


def get_translator(
    language: str = Depends(get_language),
) -> Callable[[str, Dict[str, Any]], str]:
    """
    FastAPI dependency to get a translation function for the current request.

    Args:
        language: Language code (from get_language dependency)

    Returns:
        Translation function bound to the language
    """

    def translate(key: str, **kwargs) -> str:
        """
        Translate a key to the current language.

        Args:
            key: Translation key
            **kwargs: Format parameters

        Returns:
            Translated string
        """
        return get_translation(key, language, **kwargs)

    return translate
