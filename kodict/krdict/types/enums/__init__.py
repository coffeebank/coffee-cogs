"""
Contains KRDict enumeration helpers.
"""

from .base import IntEnum, StrEnum
from .semantic_category import SemanticCategory
from .subject_category import SubjectCategory

# main enumeration classes

class Classification(StrEnum):
    """Enumeration class that contains word classifications."""

    ALL = 'all'
    WORD = 'word'
    PHRASE = 'phrase'
    EXPRESSION = 'expression'

class MultimediaType(IntEnum):
    """Enumeration class that contains multimedia types."""

    __aliases__ = {
        'all': 0,
        'photo': 1,
        'illustration': 2,
        'video': 3,
        'animation': 4,
        'sound': 5,
        'none': 6
    }

    ALL = 0
    PHOTO = 1
    ILLUSTRATION = 2
    VIDEO = 3
    ANIMATION = 4
    SOUND = 5
    NONE = 6

class OriginType(StrEnum):
    """Enumeration class that contains word origin types."""

    __aliases__ = {
        'hanja': 'chinese'
    }

    ALL = 'all'
    NATIVE = 'native'
    HANJA = 'chinese'
    LOANWORD = 'loanword'
    HYBRID = 'hybrid'

class PartOfSpeech(IntEnum):
    """Enumeration class that contains parts of speech."""

    __aliases__ = {
        'all': 0,
        'noun': 1,
        'pronoun': 2,
        'numeral': 3,
        'particle': 4,
        'verb': 5,
        'adjective': 6,
        'determiner': 7,
        'adverb': 8,
        'interjection': 9,
        'affix': 10,
        'bound noun': 11,
        'bound_noun': 11,
        'auxiliary verb': 12,
        'auxiliary_verb': 12,
        'auxiliary adjective': 13,
        'auxiliary_adjective': 13,
        'ending': 14,
        'none': 15
    }

    ALL = 0
    NOUN = 1
    PRONOUN = 2
    NUMERAL = 3
    PARTICLE = 4
    VERB = 5
    ADJECTIVE = 6
    DETERMINER = 7
    ADVERB = 8
    INTERJECTION = 9
    AFFIX = 10
    BOUND_NOUN = 11
    AUXILIARY_VERB = 12
    AUXILIARY_ADJECTIVE = 13
    ENDING = 14
    NONE = 15

class ResponseType(StrEnum):
    """Enumeration class that contains response types."""

    DEFINITION = 'dfn'
    ERROR = 'error'
    EXAMPLE = 'exam'
    IDIOM_PROVERB = 'ip'
    VIEW = 'view'
    WORD = 'word'

class SearchMethod(StrEnum):
    """Enumeration class that contains search methods."""

    EXACT = 'exact'
    INCLUDE = 'include'
    START = 'start'
    END = 'end'

class SearchTarget(IntEnum):
    """Enumeration class that contains search targets."""

    __aliases__ = {
        'headword': 1,
        'definition': 2,
        'example': 3,
        'original language': 4,
        'original_language': 4,
        'pronunciation': 5,
        'application': 6,
        'application shorthand': 7,
        'application_shorthand': 7,
        'idiom': 8,
        'proverb': 9,
        'reference info': 10,
        'reference_info': 10
    }

    HEADWORD = 1
    DEFINITION = 2
    EXAMPLE = 3
    ORIGINAL_LANGUAGE = 4
    PRONUNCIATION = 5
    APPLICATION = 6
    APPLICATION_SHORTHAND = 7
    IDIOM = 8
    PROVERB = 9
    REFERENCE_INFO = 10

class SearchType(StrEnum):
    """Enumeration class that contains search types."""

    __aliases__ = {
        'idiom/proverb': 'ip',
        'idiom_proverb': 'ip',
        'definition': 'dfn',
        'example': 'exam'
    }

    IDIOM_PROVERB = 'ip'
    DEFINITION = 'dfn'
    EXAMPLE = 'exam'
    WORD = 'word'

class SortMethod(StrEnum):
    """Enumeration class that contains sort methods."""

    __aliases__ = {
        'alphabetical': 'dict'
    }

    ALPHABETICAL = 'dict'
    POPULAR = 'popular'

class TargetLanguage(IntEnum):
    """Enumeration class that contains target languages."""

    __aliases__ = {
        'all': 0,
        'native_word': 1,
        'sino-korean': 2,
        'sino_korean': 2,
        'unknown': 3,
        'english': 4,
        'greek': 5,
        'dutch': 6,
        'norwegian': 7,
        'german': 8,
        'latin': 9,
        'russian': 10,
        'romanian': 11,
        'maori': 12,
        'malay': 13,
        'mongolian': 14,
        'basque': 15,
        'burmese': 16,
        'vietnamese': 17,
        'bulgarian': 18,
        'sanskrit': 19,
        'serbo-croatian': 20,
        'serbo_croatian': 20,
        'swahili': 21,
        'swedish': 22,
        'arabic': 23,
        'irish': 24,
        'spanish': 25,
        'uzbek': 26,
        'ukrainian': 27,
        'italian': 28,
        'indonesian': 29,
        'japanese': 30,
        'chinese': 31,
        'czech': 32,
        'cambodian': 33,
        'quechua': 34,
        'tagalog': 35,
        'thai': 36,
        'turkish': 37,
        'tibetan': 38,
        'persian': 39,
        'portuguese': 40,
        'polish': 41,
        'french': 42,
        'provencal': 43,
        'finnish': 44,
        'hungarian': 45,
        'hebrew': 46,
        'hindi': 47,
        'other': 48,
        'danish': 49
    }

    ALL = 0
    NATIVE_WORD = 1
    SINO_KOREAN = 2
    UNKNOWN = 3
    ENGLISH = 4
    GREEK = 5
    DUTCH = 6
    NORWEGIAN = 7
    GERMAN = 8
    LATIN = 9
    RUSSIAN = 10
    ROMANIAN = 11
    MAORI = 12
    MALAY = 13
    MONGOLIAN = 14
    BASQUE = 15
    BURMESE = 16
    VIETNAMESE = 17
    BULGARIAN = 18
    SANSKRIT = 19
    SERBO_CROATIAN = 20
    SWAHILI = 21
    SWEDISH = 22
    ARABIC = 23
    IRISH = 24
    SPANISH = 25
    UZBEK = 26
    UKRAINIAN = 27
    ITALIAN = 28
    INDONESIAN = 29
    JAPANESE = 30
    CHINESE = 31
    CZECH = 32
    CAMBODIAN = 33
    QUECHUA = 34
    TAGALOG = 35
    THAI = 36
    TURKISH = 37
    TIBETAN = 38
    PERSIAN = 39
    PORTUGUESE = 40
    POLISH = 41
    FRENCH = 42
    PROVENCAL = 43
    FINNISH = 44
    HUNGARIAN = 45
    HEBREW = 46
    HINDI = 47
    OTHER = 48
    DANISH = 49

class TranslationLanguage(IntEnum):
    """Enumeration class that contains translation languages."""

    __aliases__ = {
        'all': 0,
        'english': 1,
        'japanese': 2,
        'french': 3,
        'spanish': 4,
        'arabic': 5,
        'mongolian': 6,
        'vietnamese': 7,
        'thai': 8,
        'indonesian': 9,
        'russian': 10
    }

    ALL = 0
    ENGLISH = 1
    JAPANESE = 2
    FRENCH = 3
    SPANISH = 4
    ARABIC = 5
    MONGOLIAN = 6
    VIETNAMESE = 7
    THAI = 8
    INDONESIAN = 9
    RUSSIAN = 10

class VocabularyLevel(StrEnum):
    """Enumeration class that contains vocabulary levels."""

    __aliases__ = {
        'beginner': 'level1',
        'intermediate': 'level2',
        'advanced': 'level3'
    }

    ALL = 'all'
    BEGINNER = 'level1'
    INTERMEDIATE = 'level2'
    ADVANCED = 'level3'


# scraper enumeration classes

class ScrapedResponseType(StrEnum):
    """Enumeration class that contains scraped response types."""

    DEFINITION = 'scraped_dfn'
    EXAMPLE = 'scraped_exam'
    IDIOM_PROVERB = 'scraped_ip'
    VIEW = 'scraped_view'
    WORD = 'scraped_word'
    WORD_OF_THE_DAY = 'word_of_the_day'

class ScraperSearchTarget(IntEnum):
    """Enumeration class that contains scraper search targets."""

    __aliases__ = {
        'headword': 1,
        'definition': 2,
        'example': 3,
        'original language': 4,
        'original_language': 4,
        'pronunciation': 5,
        'application': 6,
        'application shorthand': 7,
        'application_shorthand': 7,
        'idiom': 8,
        'proverb': 9,
        'reference info': 10,
        'reference_info': 10,
        'translation_headword': 11,
        'translation_definition': 12,
        'translation_idiom_proverb': 13
    }

    HEADWORD = 1
    DEFINITION = 2
    EXAMPLE = 3
    ORIGINAL_LANGUAGE = 4
    PRONUNCIATION = 5
    APPLICATION = 6
    APPLICATION_SHORTHAND = 7
    IDIOM = 8
    PROVERB = 9
    REFERENCE_INFO = 10
    TRANSLATION_HEADWORD = 11
    TRANSLATION_DEFINITION = 12
    TRANSLATION_IDIOM_PROVERB= 13

class ScraperTargetLanguage(IntEnum):
    """Enumeration class that contains scraper target languages."""

    __aliases__ = {
        'all': 0,
        'native_word': 1,
        'sino-korean': 2,
        'sino_korean': 2,
        'unknown': 3,
        'english': 4,
        'greek': 5,
        'dutch': 6,
        'norwegian': 7,
        'german': 8,
        'latin': 9,
        'russian': 10,
        'romanian': 11,
        'malay': 13,
        'mongolian': 14,
        'vietnamese': 17,
        'bulgarian': 18,
        'sanskrit': 19,
        'serbo-croatian': 20,
        'serbo_croatian': 20,
        'swedish': 22,
        'arabic': 23,
        'spanish': 25,
        'italian': 28,
        'indonesian': 29,
        'japanese': 30,
        'chinese': 31,
        'czech': 32,
        'thai': 36,
        'turkish': 37,
        'persian': 39,
        'portuguese': 40,
        'polish': 41,
        'french': 42,
        'hungarian': 45,
        'hebrew': 46,
        'hindi': 47,
        'other': 48
    }

    ALL = 0
    NATIVE_WORD = 1
    SINO_KOREAN = 2
    UNKNOWN = 3
    ENGLISH = 4
    GREEK = 5
    DUTCH = 6
    NORWEGIAN = 7
    GERMAN = 8
    LATIN = 9
    RUSSIAN = 10
    ROMANIAN = 11
    MALAY = 13
    MONGOLIAN = 14
    VIETNAMESE = 17
    BULGARIAN = 18
    SANSKRIT = 19
    SERBO_CROATIAN = 20
    SWEDISH = 22
    ARABIC = 23
    SPANISH = 25
    ITALIAN = 28
    INDONESIAN = 29
    JAPANESE = 30
    CHINESE = 31
    CZECH = 32
    THAI = 36
    TURKISH = 37
    PERSIAN = 39
    PORTUGUESE = 40
    POLISH = 41
    FRENCH = 42
    HUNGARIAN = 45
    HEBREW = 46
    HINDI = 47
    OTHER = 48

class ScraperTranslationLanguage(IntEnum):
    """Enumeration class that contains translation languages that can be used by the scraper."""

    __aliases__ = {
        'all': 0,
        'english': 1,
        'japanese': 2,
        'french': 3,
        'spanish': 4,
        'arabic': 5,
        'mongolian': 6,
        'vietnamese': 7,
        'thai': 8,
        'indonesian': 9,
        'russian': 10,
        'chinese': 11
    }

    ALL = 0
    ENGLISH = 1
    JAPANESE = 2
    FRENCH = 3
    SPANISH = 4
    ARABIC = 5
    MONGOLIAN = 6
    VIETNAMESE = 7
    THAI = 8
    INDONESIAN = 9
    RUSSIAN = 10
    CHINESE = 11

class ScraperVocabularyLevel(StrEnum):
    """Enumeration class that contains scraper vocabulary levels."""

    __aliases__ = {
        'beginner': 'level1',
        'intermediate': 'level2',
        'advanced': 'level3'
    }

    ALL = 'all'
    BEGINNER = 'level1'
    INTERMEDIATE = 'level2'
    ADVANCED = 'level3'
    NONE = 'none'

__all__ = [
    'Classification',
    'MultimediaType',
    'OriginType',
    'PartOfSpeech',
    'ResponseType',
    'SearchMethod',
    'SearchTarget',
    'SearchType',
    'SortMethod',
    'TargetLanguage',
    'TranslationLanguage',
    'VocabularyLevel',
    'SemanticCategory',
    'SubjectCategory',
    'ScrapedResponseType',
    'ScraperSearchTarget',
    'ScraperTargetLanguage',
    'ScraperTranslationLanguage',
    'ScraperVocabularyLevel'
]
