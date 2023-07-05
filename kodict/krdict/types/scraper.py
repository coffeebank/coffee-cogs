"""
Contains types defined by the krdict.scraper module.
"""

from functools import reduce
from .enums import ScrapedResponseType
from .main import (
    ResponseObject,
    PartialSearchDefinition,
    SearchDefinition,
    SearchResult,
    SearchTranslation
)

# pylint: disable=too-few-public-methods,too-many-instance-attributes


# base classes

class ScrapedTranslationURLInfo(ResponseObject):
    """Contains information about URLs that point to scraped pages."""

    def __init__(self, raw):
        self.url: str = raw['url']
        self.language: str = raw['language']

class ScrapedSearchResult(SearchResult):
    """Base class for scraped search results."""

    def __init__(self, raw):
        super().__init__(raw)
        self.translation_urls = list(map(ScrapedTranslationURLInfo, raw.get('trans_link', [])))

class ScrapedResponseData(ResponseObject):
    """Base class for scraped response data objects."""

    def __init__(self, raw):
        self.url: str = raw['link']
        self.translation_urls = list(map(ScrapedTranslationURLInfo, raw.get('trans_link', [])))
        self.page: int = raw['start']
        self.per_page: int = raw['num']
        self.total_results: int = raw['total']


# word of the day response

class WordOfTheDayData(ResponseObject):
    """Contains information about the word of the day entry."""

    def __init__(self, raw):
        self.target_code: int = raw['target_code']
        self.word: str = raw['word']
        self.url: str = raw['link']
        self.translation_urls = list(map(ScrapedTranslationURLInfo, raw.get('trans_link', [])))
        self.part_of_speech: str = raw.get('pos', '')
        self.homograph_num: int = raw['sup_no']
        self.origin: str = raw.get('origin', '')
        self.vocabulary_level: str = raw.get('word_grade', '')
        self.pronunciation: str = raw.get('pronunciation', '')
        self.pronunciation_urls: list[str] = raw.get('pronunciation_urls', [])
        self.definition: str = raw['definition']
        self.translations = list(map(SearchTranslation, raw.get('translation', [])))

class WordOfTheDayResponse(ResponseObject):
    """Contains information about the word of the day."""

    def __init__(self, raw):
        self.data = WordOfTheDayData(raw['item'])
        self.response_type = ScrapedResponseType.WORD_OF_THE_DAY.value
        self.raw: dict = raw


# word search response

class ScrapedWordSearchResult(ScrapedSearchResult):
    """A result of a scraped word search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.part_of_speech: str = raw.get('pos', '')
        self.homograph_num: int = raw['sup_no']
        self.origin: str = raw.get('origin', '')
        self.vocabulary_level: str = raw.get('word_grade', '')
        self.pronunciation: str = raw.get('pronunciation', '')
        self.pronunciation_urls: list[str] = raw.get('pronunciation_urls', [])
        self.definitions = list(map(SearchDefinition, raw['sense']))

class ScrapedWordResponseData(ScrapedResponseData):
    """Response data from a scraped word search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.results = list(map(ScrapedWordSearchResult, raw['item']))

class ScrapedWordResponse(ResponseObject):
    """Contains information about a scraped word search response."""

    def __init__(self, raw):
        self.data = ScrapedWordResponseData(raw)
        self.response_type = ScrapedResponseType.WORD.value
        self.raw: dict = raw


# definition search response

class ScrapedDefinitionSearchResult(ScrapedSearchResult):
    """A result from a scraped definition search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.homograph_num: int = raw['sup_no']
        self.definition_info = PartialSearchDefinition(raw['sense'][0])

class ScrapedDefinitionResponseData(ScrapedResponseData):
    """Response data from a scraped definition search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.results = list(map(ScrapedDefinitionSearchResult, raw['item']))

class ScrapedDefinitionResponse(ResponseObject):
    """Contains information about a scraped definition search response."""

    def __init__(self, raw):
        self.data = ScrapedDefinitionResponseData(raw)
        self.response_type = ScrapedResponseType.DEFINITION.value
        self.raw: dict = raw


# example search response

class ScrapedExampleSearchResult(ScrapedSearchResult):
    """A result of a scraped example search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.homograph_num: int = raw['sup_no']
        self.example: str = raw['example']

class ScrapedExampleResponseData(ScrapedResponseData):
    """Response data from a scraped example search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.results = list(map(ScrapedExampleSearchResult, raw['item']))

class ScrapedExampleResponse(ResponseObject):
    """Contains information about a scraped example search response."""

    def __init__(self, raw):
        self.data = ScrapedExampleResponseData(raw)
        self.response_type = ScrapedResponseType.EXAMPLE.value
        self.raw: dict = raw


# idiom/proverb search response

class ScrapedIdiomProverbSearchResult(ScrapedSearchResult):
    """A result of a scraped idiom/proverb search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.url += '&searchType=P'
        self.definitions = list(map(SearchDefinition, raw['sense']))

        for info in self.translation_urls:
            info.url += '&searchType=P'

class ScrapedIdiomProverbResponseData(ScrapedResponseData):
    """Response data from a scraped idiom/proverb search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.results = list(map(ScrapedIdiomProverbSearchResult, raw['item']))

class ScrapedIdiomProverbResponse(ResponseObject):
    """Contains information about a scraped idiom/proverb search response."""

    def __init__(self, raw):
        self.data = ScrapedIdiomProverbResponseData(raw)
        self.response_type = ScrapedResponseType.IDIOM_PROVERB.value
        self.raw: dict = raw


# view query response

class ScrapedHanjaInfo(ResponseObject):
    """Contains information about a hanja."""

    def __init__(self, raw):
        self.hanja: str = raw['hanja']
        self.radical: str = raw['radical']
        self.stroke_count: int = raw['stroke_count']
        self.readings: list[str] = raw['readings']

class ScrapedOriginalLanguageInfo(ResponseObject):
    """Contains information about the origin of a word."""

    def __init__(self, raw):
        self.original_language: str = raw['original_language']
        self.language_type: str = raw['language_type']
        self.hanja_info = list(map(ScrapedHanjaInfo, raw.get('hanja_info', [])))

class ScrapedPronunciationInfo(ResponseObject):
    """Contains information about a pronunciation of a word."""

    def __init__(self, raw):
        self.pronunciation: str = raw['pronunciation']
        self.url: str = raw.get('link', '')

class ScrapedAbbreviationInfo(ResponseObject):
    """Contains information about an abbreviation of a word."""

    def __init__(self, raw):
        self.abbreviation: str = raw['abbreviation']
        self.pronunciation_info = list(
            map(ScrapedPronunciationInfo, raw.get('pronunciation_info', [])))

class ScrapedConjugationInfo(ResponseObject):
    """Contains information about a conjugation of a word."""

    def __init__(self, raw):
        info = raw.get('conjugation_info', {})

        self.conjugation: str = info.get('conjugation', '')
        self.pronunciation_info = list(map(
            ScrapedPronunciationInfo, info.get('pronunciation_info', [])))

        self.abbreviation_info = list(map(ScrapedAbbreviationInfo,
            raw.get('abbreviation_info', [])))

class ScrapedDerivativeInfo(ResponseObject):
    """Contains information about a derivative of the entry."""

    def __init__(self, raw):
        self.word: str = raw['word']
        self.target_code: int = raw.get('link_target_code', 0)
        self.url: str = raw.get('link', '')
        self.translation_urls = list(map(ScrapedTranslationURLInfo, raw.get('trans_link', [])))
        self.has_target_code: bool = raw.get('link_type') == 'C'

class ScrapedPatternInfo(ResponseObject):
    """Contains information about a usage pattern related to the word."""

    def __init__(self, raw):
        self.pattern: str = raw['pattern']

class ScrapedExampleInfo(ResponseObject):
    """Contains information about examples of a definition."""

    def __init__(self, raw):
        self.example: str = raw['example']

class ScrapedRelatedInfo(ScrapedDerivativeInfo):
    """Contains information about a related word."""

    def __init__(self, raw):
        super().__init__(raw)
        self.type: str = raw['type']

class ScrapedMultimediaInfo(ResponseObject):
    """Contains information about the multimedia attached to an entry."""

    def __init__(self, raw):
        self.label: str = raw['label']
        self.type: str = raw['type']
        self.file_number: int = raw['file_no']
        self.url: str = raw['link']
        self.thumbnail_url: str = raw['thumb_link']
        self.content_urls: list[str] = raw.get('content_urls', [])

class ScrapedPartialDefinitionInfo(ResponseObject):
    """Contains partial information about a definition of an entry."""

    def __init__(self, raw):
        self.definition: str = raw['definition']
        self.reference: str = raw.get('reference', '')
        self.translations = list(map(SearchTranslation, raw.get('translation', [])))
        self.example_info = list(map(ScrapedExampleInfo, raw.get('example_info', [])))
        self.pattern_info = list(map(ScrapedPatternInfo, raw.get('pattern_info', [])))
        self.pattern_reference: str = raw.get('pattern_reference', '')
        self.related_info = list(map(ScrapedRelatedInfo, raw.get('rel_info', [])))

class ScrapedDefinitionInfo(ScrapedPartialDefinitionInfo):
    """Contains information about a definition of an entry."""

    def __init__(self, raw):
        super().__init__(raw)
        self.multimedia_info = list(map(ScrapedMultimediaInfo, raw.get('multimedia_info', [])))

class ScrapedSubwordInfo(ResponseObject):
    """Contains information about a "subword" such as an idiom or proverb."""

    def __init__(self, raw):
        self.subword: str = raw['subword']
        self.subword_type: str = raw['subword_unit']
        self.subdefinition_info = list(map(ScrapedPartialDefinitionInfo, raw['subsense_info']))

class ScrapedWordInfo(ResponseObject):
    """Contains information about a word and its definitions."""

    def __init__(self, raw):
        self.word: str = raw['word']
        self.part_of_speech: str = raw.get('pos', '')
        self.homograph_num: int = raw['sup_no']
        self.vocabulary_level: str = raw['word_grade']
        self.allomorph: str = raw.get('allomorph', '')
        self.reference: str = raw.get('reference', '')

        self.definition_info = list(map(ScrapedDefinitionInfo, raw['sense_info']))
        self.original_language_info = list(map(
            ScrapedOriginalLanguageInfo, raw.get('original_language_info', [])))
        self.origin = reduce(
            lambda x, y: x + y.original_language, self.original_language_info, '')
        self.pronunciation_info = list(map(
            ScrapedPronunciationInfo, raw.get('pronunciation_info', [])))
        self.conjugation_info = list(map(ScrapedConjugationInfo, raw.get('conju_info', [])))
        self.derivative_info = list(map(ScrapedDerivativeInfo, raw.get('der_info', [])))
        self.subword_info = list(map(ScrapedSubwordInfo, raw.get('subword_info', [])))

class ScrapedViewResult(ResponseObject):
    """The result of a scraped view query."""

    def __init__(self, raw):
        self.target_code: int = raw['target_code']
        self.word_info = ScrapedWordInfo(raw['word_info'])

class ScrapedViewResponseData(ResponseObject):
    """Response data from a scraped view query."""

    def __init__(self, raw):
        self.url: str = raw['link']
        self.translation_urls = list(map(ScrapedTranslationURLInfo, raw.get('trans_link', [])))
        self.total_results: int = raw['total']
        self.results = list(map(ScrapedViewResult, raw['item']))

class ScrapedViewResponse(ResponseObject):
    """Contains information about a scraped view response."""

    def __init__(self, raw):
        self.data = ScrapedViewResponseData(raw)
        self.response_type = ScrapedResponseType.VIEW.value
        self.raw: dict = raw
