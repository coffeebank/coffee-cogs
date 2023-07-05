"""
Retrieves information from the krdict website via scraping.
"""

from ..types import (
    ScrapedDefinitionResponse,
    ScrapedExampleResponse,
    ScrapedIdiomProverbResponse,
    ScrapedResponseType,
    ScrapedViewResponse,
    ScrapedWordResponse,
    ScraperSearchTarget,
    ScraperTargetLanguage,
    ScraperTranslationLanguage,
    ScraperVocabularyLevel,
    WordOfTheDayResponse
)
from .main import (
    advanced_search,
    fetch_semantic_category_words,
    fetch_subject_category_words,
    fetch_word_of_the_day,
    search,
    view
)

__all__ = [
    'advanced_search',
    'fetch_semantic_category_words',
    'fetch_subject_category_words',
    'fetch_word_of_the_day',
    'search',
    'view',
    'ScrapedDefinitionResponse',
    'ScrapedExampleResponse',
    'ScrapedIdiomProverbResponse',
    'ScrapedResponseType',
    'ScrapedWordResponse',
    'ScrapedViewResponse',
    'ScraperSearchTarget',
    'ScraperTargetLanguage',
    'ScraperTranslationLanguage',
    'ScraperVocabularyLevel',
    'WordOfTheDayResponse'
]
