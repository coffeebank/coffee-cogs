"""
Provides functions that query the Korean Learners' Dictionary API.
"""

from . import scraper
from .request import set_key
from .main import advanced_search, search, view
from .types import (
    Classification,
    DefinitionResponse,
    ErrorResponse,
    ExampleResponse,
    IdiomProverbResponse,
    KRDictException,
    SemanticCategory,
    MultimediaType,
    OriginType,
    PartOfSpeech,
    ResponseType,
    SearchMethod,
    SearchTarget,
    SearchType,
    SortMethod,
    SubjectCategory,
    TargetLanguage,
    TranslationLanguage,
    ViewResponse,
    VocabularyLevel,
    WordResponse
)

__all__ = [
    'scraper',
    'advanced_search',
    'search',
    'set_key',
    'view',
    'Classification',
    'DefinitionResponse',
    'ErrorResponse',
    'ExampleResponse',
    'IdiomProverbResponse',
    'KRDictException',
    'SemanticCategory',
    'MultimediaType',
    'OriginType',
    'PartOfSpeech',
    'ResponseType',
    'SearchMethod',
    'SearchTarget',
    'SearchType',
    'SortMethod',
    'SubjectCategory',
    'TargetLanguage',
    'TranslationLanguage',
    'ViewResponse',
    'VocabularyLevel',
    'WordResponse'
]
