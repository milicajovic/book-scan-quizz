# app/utils/language_utils.py
import langcodes
from flask import current_app


def get_language_code(language):
    """
    Convert a language code or name to its ISO 639-1 (two-character) representation.

    Args:
    language (str): A language code or name.

    Returns:
    str: The ISO 639-1 two-character language code, or 'en' if not found.
    """
    try:
        return langcodes.Language.get(language).language_name()
    except (langcodes.LanguageTagError, AttributeError) as e:
        current_app.logger.error(f"Error converting language '{language}' to code: {str(e)}")
        return 'en'  # Default to English if language is not found or invalid


def get_language_name(code):
    """
    Get the full name of a language from its ISO 639-1 (two-character) code.

    Args:
    code (str): An ISO 639-1 two-character language code.

    Returns:
    str: The full name of the language, or 'English' if not found.
    """
    try:
        return langcodes.Language.get(code).display_name()
    except (langcodes.LanguageTagError, AttributeError) as e:
        current_app.logger.error(f"Error getting language name for code '{code}': {str(e)}")
        return 'English'  # Default to English if code is not found or invalid


def get_language_from_headers(headers):
    """
    Extract the language code from request headers.

    Args:
    headers (werkzeug.datastructures.EnvironHeaders): The request headers.

    Returns:
    str: The ISO 639-1 two-character language code, or 'en' if not found.
    """
    # Try to get the language from the Accept-Language header
    accept_language = headers.get('Accept-Language')
    if accept_language:
        try:
            primary_language = accept_language.split(',')[0].split('-')[0]
            return get_language_code(primary_language)
        except Exception as e:
            current_app.logger.error(f"Error extracting language from headers: {str(e)}")
    else:
        current_app.logger.warning("No Accept-Language header found in request")
    return 'en'  # Default to English if no language header is found or in case of error
