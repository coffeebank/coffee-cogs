from typing import Iterable, Literal, TypedDict, Union, overload

from ..types import (
    Classification,
    SemanticCategory,
    MultimediaType,
    OriginType,
    PartOfSpeech,
    ScrapedDefinitionResponse,
    ScrapedExampleResponse,
    ScrapedIdiomProverbResponse,
    ScrapedWordResponse,
    ScrapedViewResponse,
    ScraperTranslationLanguage,
    SearchMethod,
    SearchTarget,
    SearchType,
    SortMethod,
    SubjectCategory,
    TargetLanguage,
    VocabularyLevel,
    WordOfTheDayResponse
)
from ..main import (
    TClassification,
    TSemanticCategory,
    TMultimediaType,
    TOriginType,
    TPartOfSpeech,
    TSearchMethod,
    TSearchTarget,
    TSearchType,
    TSortMethod,
    TSubjectCategory,
    TTargetLanguage,
    TVocabularyLevel
)

TScraperTranslationLanguage = ScraperTranslationLanguage | int | Literal[
    'english',
    'japanese',
    'french',
    'spanish',
    'arabic',
    'mongolian',
    'vietnamese',
    'thai',
    'indonesian',
    'russian',
    'chinese'
]
TScrapedResponse = Union[
    ScrapedDefinitionResponse,
    ScrapedExampleResponse,
    ScrapedIdiomProverbResponse,
    ScrapedWordResponse
]

class TSearchCondition(TypedDict, total=False):
    query: str
    exclude: bool
    search_target: TSearchTarget
    target_language: TTargetLanguage
    search_method: TSearchMethod


def advanced_search(*,
    query: str = '',
    page: int = 1,
    per_page: int = 10,
    sort: TSortMethod = SortMethod.ALPHABETICAL,
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None,
    search_target: TSearchTarget = SearchTarget.HEADWORD,
    target_language: TTargetLanguage = TargetLanguage.ALL,
    search_method: TSearchMethod = SearchMethod.INCLUDE,
    classification: TClassification | Iterable[TClassification] = Classification.ALL,
    origin_type: TOriginType | Iterable[TOriginType] = OriginType.ALL,
    vocabulary_level: TVocabularyLevel | Iterable[TVocabularyLevel] = VocabularyLevel.ALL,
    part_of_speech: TPartOfSpeech | Iterable[TPartOfSpeech] = PartOfSpeech.ALL,
    multimedia_type: TMultimediaType | Iterable[TMultimediaType] = MultimediaType.ALL,
    min_syllables: int = 1,
    max_syllables: int = 0,
    semantic_category: TSemanticCategory = SemanticCategory.ALL,
    subject_category: TSubjectCategory | Iterable[TSubjectCategory] = SubjectCategory.ALL,
    search_conditions: Iterable[TSearchCondition] | None = None
) -> ScrapedWordResponse: ...

def fetch_semantic_category_words(*,
    category: TSemanticCategory,
    page: int = 1,
    per_page: int = 10,
    sort: TSortMethod = SortMethod.ALPHABETICAL,
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None
) -> ScrapedWordResponse: ...

def fetch_subject_category_words(*,
    category: TSubjectCategory | Iterable[TSubjectCategory] = SubjectCategory.ALL,
    page: int = 1,
    per_page: int = 10,
    sort: TSortMethod = SortMethod.ALPHABETICAL,
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None
) -> ScrapedWordResponse: ...

def fetch_word_of_the_day(*,
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None
) -> WordOfTheDayResponse: ...

@overload
def search(*,
    query: str,
    page: int = 1,
    per_page: int = 10,
    sort: TSortMethod = SortMethod.ALPHABETICAL,
    search_type: Literal[SearchType.WORD, 'word'],
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None
) -> ScrapedWordResponse: ...
@overload
def search(*,
    query: str,
    page: int = 1,
    per_page: int = 10,
    sort: TSortMethod = SortMethod.ALPHABETICAL,
    search_type: Literal[SearchType.DEFINITION, 'dfn', 'definition'],
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None
) -> ScrapedDefinitionResponse: ...
@overload
def search(*,
    query: str,
    page: int = 1,
    per_page: int = 10,
    sort: TSortMethod = SortMethod.ALPHABETICAL,
    search_type: Literal[SearchType.EXAMPLE, 'example', 'exam'],
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None
) -> ScrapedExampleResponse: ...
@overload
def search(*,
    query: str,
    page: int = 1,
    per_page: int = 10,
    sort: TSortMethod = SortMethod.ALPHABETICAL,
    search_type: Literal[SearchType.IDIOM_PROVERB, 'ip', 'idiom_proverb', 'idiom/proverb'],
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None
) -> ScrapedIdiomProverbResponse: ...
@overload
def search(*,
    query: str,
    page: int = 1,
    per_page: int = 10,
    sort: TSortMethod = SortMethod.ALPHABETICAL,
    search_type: TSearchType,
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None
) -> TScrapedResponse: ...

def view(*,
    target_code: int,
    fetch_multimedia: bool = False,
    translation_language: TScraperTranslationLanguage | Iterable[TScraperTranslationLanguage] | None = None
) -> ScrapedViewResponse: ...
