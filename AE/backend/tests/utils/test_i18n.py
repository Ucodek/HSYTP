from app.utils.i18n import extract_request_language, get_localized_content


def test_get_localized_content():
    """Test getting localized content from a multilingual dictionary"""
    content = {"en-US": "Hello", "tr-TR": "Merhaba", "de-DE": "Hallo"}

    # Test exact match
    assert get_localized_content(content, "en-US") == "Hello"
    assert get_localized_content(content, "tr-TR") == "Merhaba"

    # Test language base match
    assert get_localized_content(content, "en-GB") == "Hello"

    # Test fallback to default
    assert get_localized_content(content, "fr-FR") == "Hello"

    # Test with different default
    assert get_localized_content(content, "fr-FR", default_language="de-DE") == "Hallo"

    # Test with empty content
    assert get_localized_content({}, "en-US") is None

    # Test with None content
    assert get_localized_content(None, "en-US") is None


def test_extract_request_language():
    """Test extracting the preferred language from Accept-Language header"""
    # Test with exact language-region format
    assert extract_request_language("en-US") == "en-US"

    # Test with language only
    assert extract_request_language("en") == "en-US"
    assert extract_request_language("tr") == "tr-TR"

    # Test with quality values
    assert extract_request_language("en-US;q=0.8,en;q=0.7") == "en-US"

    # Test with multiple languages
    assert extract_request_language("fr-FR,en-US;q=0.8,en;q=0.7") == "fr-FR"

    # Test with unknown language
    assert extract_request_language("xx") == "xx-US"  # Default region is US

    # Test with None
    assert extract_request_language(None) == "en-US"

    # Test with empty string
    assert extract_request_language("") == "en-US"
