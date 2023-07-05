"""
Contains response types defined by the krdict package.
"""

from functools import reduce
from .enums import ResponseType

# pylint: disable=too-few-public-methods,too-many-instance-attributes


def _to_dict(obj):
    if isinstance(obj, ResponseObject):
        return obj.asdict()

    if isinstance(obj, list):
        return list(map(_to_dict, obj))

    return obj


# base classes

class ResponseObject:
    """Base class for response objects."""

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        attrs = vars(self).copy()

        if 'raw' in attrs:
            del attrs['raw']

        return repr(attrs)

    def asdict(self):
        """
        Converts the response object to a dict and returns the created dict.
        """

        attrs = {
            k: _to_dict(v)
            for k, v in vars(self).items()
        }

        if 'raw' in attrs:
            del attrs['raw']

        return attrs

class SearchResult(ResponseObject):
    """Base class for search results."""

    def __init__(self, raw):
        self.target_code: int = raw['target_code']
        self.word: str = raw['word']
        self.url: str = raw['link']

class SearchResponseData(ResponseObject):
    """Base class for search response data objects."""

    def __init__(self, raw):
        self.title: str = raw['title']
        self.url: str = raw['link']
        self.description: str = raw['description']
        self.last_build_date: str = raw['lastBuildDate']
        self.page: int = raw['start']
        self.per_page: int = raw['num']
        self.total_results: int = raw['total']

class SearchTranslation(ResponseObject):
    """Contains translation information for a definition."""

    def __init__(self, raw):
        self.word: str = raw.get('trans_word', '')
        self.definition: str = raw['trans_dfn']
        self.language: str = raw['trans_lang']

class PartialSearchDefinition(ResponseObject):
    """Contains partial information about a definition in a search result."""

    def __init__(self, raw):
        self.definition: str = raw['definition']
        self.translations = list(map(SearchTranslation, raw.get('translation', [])))

class SearchDefinition(PartialSearchDefinition):
    """Contains information about a definition in a search result."""

    def __init__(self, raw):
        self.order: int = raw['sense_order']
        super().__init__(raw)


# error response

class ErrorResponse(ResponseObject):
    """
    Contains information about an error response.
    """

    def __init__(self, raw, request_params):
        self.error_code: int = raw['error']['error_code']
        self.message: str = raw['error']['message']
        self.request_params: dict = request_params
        self.response_type = ResponseType.ERROR.value
        self.raw: dict = raw


# word search response

class WordSearchResult(SearchResult):
    """A result from a word search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.part_of_speech: str = raw.get('pos', '')
        self.homograph_num: int = raw['sup_no']
        self.origin: str = raw.get('origin', '')
        self.pronunciation: str = raw.get('pronunciation', '')
        self.vocabulary_level: str = raw.get('word_grade', '')
        self.definitions = list(map(SearchDefinition, raw['sense']))

class WordResponseData(SearchResponseData):
    """Response data from a word search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.results = list(map(WordSearchResult, raw.get('item', [])))

class WordResponse(ResponseObject):
    """Contains information about a word search response."""

    def __init__(self, raw, request_params):
        self.data = WordResponseData(raw['channel'])
        self.request_params: dict = request_params
        self.response_type = ResponseType.WORD.value
        self.raw: dict = raw


# definition search response

class DefinitionSearchResult(SearchResult):
    """A result from a definition search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.homograph_num: int = raw['sup_no']
        self.definition_info = PartialSearchDefinition(raw['sense'][0])

class DefinitionResponseData(SearchResponseData):
    """Response data from a definition search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.results = list(map(DefinitionSearchResult, raw.get('item', [])))

class DefinitionResponse(ResponseObject):
    """Contains information about a definition search response."""

    def __init__(self, raw, request_params):
        self.data = DefinitionResponseData(raw['channel'])
        self.request_params: dict = request_params
        self.response_type = ResponseType.DEFINITION.value
        self.raw: dict = raw


# example search response

class ExampleSearchResult(SearchResult):
    """A result from an example search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.homograph_num: int = raw['sup_no']
        self.example: str = raw['example']

class ExampleResponseData(SearchResponseData):
    """Response data from an example search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.results = list(map(ExampleSearchResult, raw.get('item', [])))

class ExampleResponse(ResponseObject):
    """Contains information about an example search response."""

    def __init__(self, raw, request_params):
        self.data = ExampleResponseData(raw['channel'])
        self.request_params: dict = request_params
        self.response_type = ResponseType.EXAMPLE.value
        self.raw: dict = raw


# idiom/proverb search response

class IdiomProverbSearchResult(SearchResult):
    """A result from an idiom/proverb search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.url += '&searchType=P'
        self.definitions = list(map(SearchDefinition, raw['sense']))

class IdiomProverbResponseData(SearchResponseData):
    """Response data from an idiom/proverb search."""

    def __init__(self, raw):
        super().__init__(raw)
        self.results = list(map(IdiomProverbSearchResult, raw.get('item', [])))

class IdiomProverbResponse(ResponseObject):
    """Contains information about an idiom/proverb search response."""

    def __init__(self, raw, request_params):
        self.data = IdiomProverbResponseData(raw['channel'])
        self.request_params: dict = request_params
        self.response_type = ResponseType.IDIOM_PROVERB.value
        self.raw: dict = raw


# view query response

class OriginalLanguageInfo(ResponseObject):
    """Information about the origin of a word."""

    def __init__(self, raw):
        self.original_language: str = raw['original_language']
        self.language_type: str = raw['language_type']

class PronunciationInfo(ResponseObject):
    """Contains a pronunciation of a word."""

    def __init__(self, raw):
        self.pronunciation: str = raw['pronunciation']

class AbbreviationInfo(ResponseObject):
    """Contains information about an abbreviation of a word."""

    def __init__(self, raw):
        self.abbreviation: str = raw['abbreviation']
        self.pronunciation_info = list(
            map(PronunciationInfo, raw.get('pronunciation_info', [])))

class ConjugationInfo(ResponseObject):
    """Contains information about a conjugation of a word."""

    def __init__(self, raw):
        self.conjugation: str = raw.get('conjugation', '')
        info = raw.get('conjugation_info', {})

        self.pronunciation_info = list(map(
            PronunciationInfo, info.get('pronunciation_info', [])))
        self.abbreviation_info = list(map(
            AbbreviationInfo, info.get('abbreviation_info', [])))

class ReferenceInfo(ResponseObject):
    """Contains information about a reference word."""

    def __init__(self, raw):
        self.word: str = raw['word']
        self.target_code: int = raw.get('link_target_code', 0)
        self.url: str = raw.get('link', '')
        self.has_target_code: bool = raw.get('link_type') == 'C'

class CategoryInfo(ResponseObject):
    """Contains information about a category that a word belongs to."""

    def __init__(self, raw):
        self.type: str = raw['type']
        self.name: str = raw['written_form']

class PatternInfo(ResponseObject):
    """Contains information about a usage pattern related to the word."""

    def __init__(self, raw):
        self.pattern: str = raw['pattern']
        self.pattern_reference: str = raw.get('pattern_reference', '')

class ExampleInfo(ResponseObject):
    """Contains information about examples of a definition."""
    def __init__(self, raw):
        self.type: str = raw['type']
        self.example: str = raw['example']

class RelatedInfo(ReferenceInfo):
    """Contains information about a related word."""

    def __init__(self, raw):
        super().__init__(raw)
        self.type: str = raw['type']

class MultimediaInfo(ResponseObject):
    """Contains information about the multimedia attached to an entry."""

    def __init__(self, raw):
        self.label: str = raw['label']
        self.type: str = raw['type']
        self.url: str = raw['link']

class PartialDefinitionInfo(ResponseObject):
    """Contains partial information about a definition."""

    def __init__(self, raw):
        self.definition: str = raw['definition']
        self.reference: str = raw.get('reference', '')
        self.translations = list(map(SearchTranslation, raw.get('translation', [])))
        self.example_info = list(map(ExampleInfo, raw.get('example_info', [])))
        self.pattern_info = list(map(PatternInfo, raw.get('pattern_info', [])))
        self.related_info = list(map(RelatedInfo, raw.get('rel_info', [])))

class DefinitionInfo(PartialDefinitionInfo):
    """Contains information about a definition."""

    def __init__(self, raw):
        super().__init__(raw)
        self.multimedia_info = list(map(MultimediaInfo, raw.get('multimedia_info', [])))

class SubwordInfo(ResponseObject):
    """Contains information about a "subword" such as an idiom or proverb."""

    def __init__(self, raw):
        self.subword: str = raw['subword']
        self.subword_type: str = raw['subword_unit']
        self.subdefinition_info = list(map(PartialDefinitionInfo, raw['subsense_info']))

class WordInfo(ResponseObject):
    """Contains information about a word and its definitions."""

    def __init__(self, raw):
        self.word: str = raw['word']
        self.word_unit: str = raw['word_unit']
        self.word_type: str = raw['word_type']
        self.part_of_speech: str = raw.get('pos', '')
        self.homograph_num: int = raw['sup_no']
        self.vocabulary_level: str = raw['word_grade']
        self.allomorph: str = raw.get('allomorph', '')
        self.reference: str = raw.get('reference', '')

        self.definition_info = list(map(DefinitionInfo, raw['sense_info']))
        self.original_language_info = list(map(
            OriginalLanguageInfo, raw.get('original_language_info', [])))
        self.origin = reduce(
            lambda x, y: x + y.original_language, self.original_language_info, '')
        self.pronunciation_info = list(map(
            PronunciationInfo, raw.get('pronunciation_info', [])))
        self.conjugation_info = list(map(ConjugationInfo, raw.get('conju_info', [])))
        self.derivative_info = list(map(ReferenceInfo, raw.get('der_info', [])))
        self.reference_info = list(map(ReferenceInfo, raw.get('ref_info', [])))
        self.category_info = list(map(CategoryInfo, raw.get('category_info', [])))
        self.subword_info = list(map(SubwordInfo, raw.get('subword_info', [])))

class ViewResult(ResponseObject):
    """The result of a view query."""

    def __init__(self, raw):
        self.target_code: int = raw['target_code']
        self.word_info = WordInfo(raw['word_info'])

class ViewResponseData(ResponseObject):
    """Response data from a view query."""

    def __init__(self, raw):
        self.title: str = raw['title']
        self.url: str = raw['link']
        self.description: str = raw['description']
        self.last_build_date: str = raw['lastBuildDate']
        self.total_results: int = raw['total']
        self.results = list(map(ViewResult, raw.get('item', [])))

class ViewResponse(ResponseObject):
    """Contains information about a view query response."""

    def __init__(self, raw, request_params):
        self.data = ViewResponseData(raw['channel'])
        self.request_params: dict = request_params
        self.response_type = ResponseType.VIEW.value
        self.raw: dict = raw
