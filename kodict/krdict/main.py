"""
Provides functions that query the Korean Learners' Dictionary API.
"""

from .request import send_request
from .response import parse_response

def advanced_search(**kwargs):
    """
    Performs an advanced search on the Korean Learners' Dictionary API.
    Returns an object with contents dependent on the value of the ``search_type``
    parameter and whether an error occurred.

    See the [documentation](https://krdictpy.readthedocs.io/en/stable/return_types) for details.

    - ``query``: The search query.
    - ``raise_api_errors``: Sets whether a ``KRDictException`` will be raised if an API error
    occurs. A value of ``True`` guarantees that the result is not an ``ErrorResponse``.
    - ``key``: The API key. If a key was set with ``set_key``, this can be omitted.
    - ``page``: The page at which the search should start ``[1, 1000]``.
    - ``per_page``: The maximum number of search results to return ``[10, 100]``.
    - ``sort``: The sort method that should be used.
    - ``search_type``: The type of search to perform
        - Note: Search types other than ``SearchType.WORD`` are unsupported and not
        recommended for use.
    - ``translation_language``: A language or list of languages for which translations
    should be included.
    - ``search_target``: The target field of the search query.
    - ``target_language``: The original language to search by. If ``search_target``
    is set to any value other than ``SearchTarget.ORIGINAL_LANGUAGE``, this parameter
    has no effect.
    - ``search_method``: The method used to match against the query.
    - ``classification``: An entry classification to filter by.
    - ``origin_type``: A word origin type to filter by.
    - ``vocabulary_level``: A vocabulary level to filter by.
    - ``part_of_speech``: A part of speech to filter by.
    - ``multimedia_type``: A multimedia type to filter by.
    - ``min_syllables``: The minimum number of syllables in result words ``[1, 80]``.
    - ``max_syllables``: The maximum number of syllables in result words. A value of ``0`` denotes
    no maximum ``[0, 80]``.
    - ``semantic_category``: The semantic category to filter by.
    - ``subject_category``: A subject category to filter by.
    """

    return parse_response(kwargs, *send_request(kwargs, True))

def search(**kwargs):
    """
    Performs a search on the Korean Learners' Dictionary API.
    Returns an object with contents dependent on the value of the ``search_type``
    parameter and whether an error occurred.

    See the [documentation](https://krdictpy.readthedocs.io/en/stable/return_types) for details.

    - ``query``: The search query.
    - ``raise_api_errors``: Sets whether a ``KRDictException`` will be raised if an API error
    occurs. A value of ``True`` guarantees that the result is not an ``ErrorResponse``.
    is included, including keys set by the scraper.
    - ``key``: The API key. If a key was set with ``set_key``, this can be omitted.
    - ``page``: The page at which the search should start ``[1, 1000]``.
    - ``per_page``: The maximum number of search results to return ``[10, 100]``.
    - ``sort``: The sort method that should be used.
    - ``search_type``: The type of search to perform.
    - ``translation_language``: A language or list of languages for which translations
    should be included.
    """

    return parse_response(kwargs, *send_request(kwargs, False))

def view(**kwargs):
    """
    Performs a view query on the Korean Learners' Dictionary API.
    Returns either an object with information about a dictionary entry, or an error object
    if an error occurred.

    See the [documentation](https://krdictpy.readthedocs.io/en/stable/return_types) for details.

    - ``query``: The search query.
    - ``homograph_num``: The superscript number used to distinguish homographs.
    - ``target_code``: The target code of the desired result.
    - ``raise_api_errors``: Sets whether a KRDictException will be raised if an API error occurs.
    A value of ``True`` guarantees that the result is not an ``ErrorResponse``.
    - ``key``: The API key. If a key was set with ``set_key``, this can be omitted.
    - ``translation_language``: A language or list of languages for which translations
    should be included.
    """

    return parse_response(kwargs, *send_request(kwargs, False, 'view'))
