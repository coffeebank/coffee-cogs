"""
Transforms input parameters into API-compliant dicts.
"""

from os import path
import requests

from .types import (
    isiterable,
    Classification,
    SemanticCategory,
    MultimediaType,
    PartOfSpeech,
    SearchMethod,
    SearchTarget,
    SearchType,
    SortMethod,
    SubjectCategory,
    TargetLanguage,
    TranslationLanguage,
    OriginType,
    VocabularyLevel
)

_SEARCH_URL = 'https://krdict.korean.go.kr/api/search'
_VIEW_URL = 'https://krdict.korean.go.kr/api/view'
_PARAM_MAPS = {
    'query': {
        'name': 'q'
    },
    'page': {
        'name': 'start'
    },
    'per_page': {
        'name': 'num'
    },
    'sort': {
        'name': 'sort',
        'type': SortMethod
    },
    'search_type': {
        'name': 'part',
        'type': SearchType
    },
    'translation_language': {
        'name': 'trans_lang',
        'type': TranslationLanguage
    },
    'search_target': {
        'name': 'target',
        'type': SearchTarget
    },
    'target_language': {
        'name': 'lang',
        'type': TargetLanguage
    },
    'search_method': {
        'name': 'method',
        'type': SearchMethod
    },
    'classification': {
        'name': 'type1',
        'type': Classification
    },
    'origin_type': {
        'name': 'type2',
        'type': OriginType
    },
    'vocabulary_level': {
        'name': 'level',
        'type': VocabularyLevel
    },
    'part_of_speech': {
        'name': 'pos',
        'type': PartOfSpeech
    },
    'multimedia_type': {
        'name': 'multimedia',
        'type': MultimediaType
    },
    'min_syllables': {
        'name': 'letter_s'
    },
    'max_syllables': {
        'name': 'letter_e'
    },
    'semantic_category': {
        'name': 'sense_cat',
        'type': SemanticCategory
    },
    'subject_category': {
        'name': 'subject_cat',
        'type': SubjectCategory
    },
    'target_code': {
        'name': 'q'
    }
}
_DEFAULTS = { 'API_KEY': '' }
_PEM_PATH = path.join(path.dirname(path.realpath(__file__)), 'korean-go-kr-chain.pem')


def _map_value(mapper, value):
    if isiterable(value, exclude=(str,)):
        return ','.join(map(lambda x: _map_value(mapper, x), value))

    if 'type' in mapper:
        return str(mapper['type'].get_value(value, value))

    return str(value)

def _transform_params(params, search_type):
    params = params.copy()

    if 'key' not in params and _DEFAULTS['API_KEY']:
        params['key'] = _DEFAULTS['API_KEY']
    if 'raise_api_errors' in params:
        del params['raise_api_errors']

    if search_type == 'view':
        transform_view_params(params)
    else:
        transform_search_params(params)

    return params


def send_request(kwargs, advanced=False, search_type=None):
    """
    Sends a request to the API endpoint matching ``search_type``.
    Returns a tuple that contains the response object, the transformed
    parameters which were sent to the API, and the search type.

    - ``kwargs``: The provided input keyword arguments.
    - ``advanced``: Whether or not this is an advanced search.
    - ``search_type``: The type of search which should be performed.
    """

    search_type = SearchType.get_value(
        search_type or kwargs.get('search_type', 'word'),
        search_type
    )

    url = _VIEW_URL if search_type == 'view' else _SEARCH_URL

    params = _transform_params(kwargs, search_type)
    if advanced:
        params['advanced'] = 'y'

    try:
        response = requests.get(url, params, verify=_PEM_PATH)
        response.raise_for_status()
        return (response, params, search_type)
    except requests.exceptions.RequestException as exc:
        raise exc

def set_key(key):
    """
    Sets the API key to use when a key is not specified in a request.

    - ``key``: The API key to use, or None to unset the key.
    """

    _DEFAULTS['API_KEY'] = '' if key is None else key

def transform_search_params(params):
    """
    Transforms input search parameters into an API-compliant dict.

    - ``params``: The provided input parameters.
    """

    for key in list(params.keys()):
        if params[key] is None:
            del params[key]
            continue
        if key not in _PARAM_MAPS:
            continue

        mapper = _PARAM_MAPS[key]
        new_key = mapper['name']
        new_value = _map_value(mapper, params[key])

        params[new_key] = new_value

        if key != new_key:
            del params[key]

    if 'trans_lang' in params and 'translated' not in params:
        params['translated'] = 'y'
    if 'letter_s' in params and 'letter_e' not in params:
        params['letter_e'] = '0'
    if 'letter_e' in params and 'letter_s' not in params:
        params['letter_s'] = '1'

def transform_view_params(params):
    """
    Transforms input view parameters into an API-compliant dict.

    - ``params``: The provided input parameters.
    """

    if 'target_code' in params:
        params['method'] = 'target_code'
    elif 'query' in params:
        if 'homograph_num' in params:
            params['query'] += str(params['homograph_num'])
            del params['homograph_num']
        else:
            params['query'] += '0'

    transform_search_params(params)
