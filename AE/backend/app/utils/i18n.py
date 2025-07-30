from typing import Any, Dict, Optional


def get_localized_content(
    content: Dict[str, Any], language: str, default_language: str = "en-US"
) -> Any:
    """
    Extract localized content from a multilingual dictionary.
    Falls back to default language if requested language is not available.

    Args:
        content: Dictionary with language codes as keys
        language: Requested language code
        default_language: Fallback language code

    Returns:
        The content in the requested language, or fallback language
    """
    if not content:
        return None

    # First try exact language match
    if language in content and content[language]:
        return content[language]

    # Then try language without region (e.g., "en" from "en-US")
    language_base = language.split("-")[0]
    for key in content:
        if key.startswith(language_base) and content[key]:
            return content[key]

    # Fallback to default language
    if default_language in content and content[default_language]:
        return content[default_language]

    # Last resort: return first non-empty value
    for value in content.values():
        if value:
            return value

    # If all else fails, return None
    return None


def extract_request_language(accept_language_header: Optional[str]) -> str:
    """
    Extract preferred language from the Accept-Language header.

    Args:
        accept_language_header: The Accept-Language header value

    Returns:
        The preferred language code, defaulting to "en-US"
    """
    if not accept_language_header:
        return "en-US"

    # Parse the header (basic implementation)
    languages = accept_language_header.split(",")
    if not languages:
        return "en-US"

    # Get highest priority language
    primary_language = languages[0].split(";")[0].strip()

    # Ensure we have a proper format like "en-US"
    if "-" not in primary_language:
        # Default region when only language code is provided
        lang_regions = {"en": "US", "tr": "TR", "de": "DE", "fr": "FR", "es": "ES"}
        language = primary_language.lower()
        region = lang_regions.get(language, "US")
        return f"{language}-{region}"

    return primary_language
