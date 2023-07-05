"""
Handles making requests to the dictionary website.
"""

from os import path
import aiohttp
import asyncio
from lxml import html
from .constants import _VIEW_URL
from ..types import (
    isiterable,
    Classification,
    SemanticCategory,
    MultimediaType,
    OriginType,
    PartOfSpeech,
    SearchMethod,
    SearchType,
    SortMethod,
    ScraperSearchTarget,
    ScraperTargetLanguage,
    ScraperTranslationLanguage,
    ScraperVocabularyLevel,
    SubjectCategory
)

_ADVANCED_SEARCH_URL = (
    'https://krdict.korean.go.kr{}/dicSearchDetail/searchDetailWordsResult?'
    '{}searchFlag=Y&syllablePosition={}'
)
_BASE_URL = 'https://krdict.korean.go.kr{}/mainAction'
_CAT_MEANING_URL = (
    'https://krdict.korean.go.kr{}/dicSearchDetail/searchDetailSenseCategoryResult?'
    '{}searchFlag=Y&currentPage={}&blockCount={}&sort={}{}'
)
_CAT_SUBJECT_URL = (
    'https://krdict.korean.go.kr{}/dicSearchDetail/searchDetailActCategoryResult?'
    '{}searchFlag=Y&currentPage={}&blockCount={}&sort={}{}'
)
_DEFAULT_ADVANCED_CONDITION = (
    '&searchOp=AND&searchTarget=word&searchOrglanguage=all&wordCondition=wordAll&query='
)
_SEARCH_URL = (
    'https://krdict.korean.go.kr{}/dicSearch/search?'
    '{}mainSearchWord={}&currentPage={}&blockCount={}&sort={}&searchType={}'
)
_SEARCH_REQUEST_URL = (
    'https://krdict.korean.go.kr{}/smallDic/searchResult?'
    '{}mainSearchWord={}&currentPage={}&blockCount={}&sort={}&searchType={}'
)
_IMAGE_URL = (
    'https://krdict.korean.go.kr/dicSearch/viewImageConfirm?'
    'searchKindValue=image&ParaWordNo={}&ParaSenseSeq={}&multiMediaSeq={}'
)
_VIDEO_URL = (
    'https://krdict.korean.go.kr/dicSearch/viewMovieConfirm?'
    'searchKindValue=video&ParaWordNo={}&ParaSenseSeq={}&multiMediaSeq={}'
)

_LANG_INFO = (
    ('all', None, None),
    ('eng', 6, '영어'),
    ('jpn', 7, '일본어'),
    ('fra', 8, '프랑스어'),
    ('spa', 9, '스페인어'),
    ('ara', 10, '아랍어'),
    ('mon', 1, '몽골어'),
    ('vie', 2, '베트남어'),
    ('tha', 3, '타이어'),
    ('ind', 4, '인도네시아어'),
    ('rus', 5, '러시아어'),
    ('chn', 11, '중국어')
)

_ADVANCED_CONDITION_MAP = {
    'query': {
        'name': 'query',
        'default': ''
    },
    'search_target': {
        'name': 'searchTarget',
        'type': ScraperSearchTarget,
        'default': '1',
        'value': {
            '1': 'word',
            '2': 'definition',
            '3': 'example',
            '4': 'org_language',
            '5': 'pronunciation',
            '6': 'conjugation',
            '7': 'shorten',
            '8': 'idiom',
            '9': 'proverb',
            '10': 'reference',
            '11': 'trans_word',
            '12': 'trans_word_def',
            '13': 'trans_subword'
        }
    },
    'target_language': {
        'name': 'searchOrglanguage',
        'type': ScraperTargetLanguage,
        'default': '0',
        'value': {
            '0': 'all',
            '1': '0',
            '2': '32',
            '3': '97',
            '4': '17',
            '5': '1',
            '6': '2',
            '7': '3',
            '8': '4',
            '9': '5',
            '10': '6',
            '11': '7',
            '12': '99',
            '13': '8',
            '14': '9',
            '15': '99',
            '16': '99',
            '17': '10',
            '18': '11',
            '19': '12',
            '20': '13',
            '21': '99',
            '22': '14',
            '23': '15',
            '24': '99',
            '25': '16',
            '26': '99',
            '27': '99',
            '28': '16',
            '29': '17',
            '30': '18',
            '31': '19',
            '32': '20',
            '33': '99',
            '34': '99',
            '35': '99',
            '36': '21',
            '37': '22',
            '38': '99',
            '39': '23',
            '40': '24',
            '41': '25',
            '42': '26',
            '43': '99',
            '44': '99',
            '45': '27',
            '46': '28',
            '47': '29',
            '48': '99',
            '49': '99'
        }
    },
    'search_method': {
        'name': 'wordCondition',
        'type': SearchMethod,
        'default': 'include',
        'value': {
            'exact': 'wordSame',
            'include': 'wordAll',
            'start': 'wordStart',
            'end': 'wordEnd'
        }
    }
}
_ADVANCED_PARAM_MAP = {
    'page': {
        'name': 'currentPage'
    },
    'per_page': {
        'name': 'blockCount'
    },
    'sort': {
        'name': 'sort',
        'type': SortMethod,
        'value': {
            'dict': 'W',
            'popular': 'C'
        }
    },
    'classification': {
        'name': 'gubun',
        'type': Classification,
        'default': 'all',
        'value': {
            'word': 'W',
            'phrase': 'P',
            'expression': 'E'
        }
    },
    'origin_type': {
        'name': 'wordNativeCode',
        'type': OriginType,
        'default': 'all',
        'value': {
            'native': '1',
            'chinese': '2',
            'loanword': '3',
            'hybrid': '0'
        }
    },
    'vocabulary_level': {
        'name': 'imcnt',
        'type': ScraperVocabularyLevel,
        'default': 'all',
        'value': {
            'level1': '1',
            'level2': '2',
            'level3': '3',
            'none': '0'
        }
    },
    'part_of_speech': {
        'name': 'sp_code',
        'type': PartOfSpeech,
        'all_value': '0',
        'default': '0',
        'value': {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '27'
        }
    },
    'multimedia_type': {
        'name': 'multimedia',
        'type': MultimediaType,
        'all_value': '0',
        'default': '0',
        'value': {
            '1': 'P',
            '2': 'I',
            '3': 'V',
            '4': 'S',
            '5': 'A',
            '6': 'N'
        }
    },
    'min_syllables': {
        'name': 'searchSyllableStart'
    },
    'max_syllables': {
        'name': 'searchSyllableEnd',
        'value': {
            '0': '80'
        }
    },
    'semantic_category': {
        'type': SemanticCategory,
        'default': '0',
        'convert': lambda tup: f'&senseCategoryTop={tup[0]}&senseCategoryMiddle={tup[1]}',
        'value': {
            '0': ('0', '1000'),
            '1': ('1', '1001'),
            '2': ('1', '1002'),
            '3': ('1', '1003'),
            '4': ('1', '1004'),
            '5': ('1', '1005'),
            '6': ('1', '1006'),
            '7': ('1', '1007'),
            '8': ('1', '1008'),
            '9': ('1', '1009'),
            '10': ('1', '1010'),
            '11': ('1', '1011'),
            '12': ('1', '1012'),
            '13': ('1', '1013'),
            '14': ('1', '1014'),
            '15': ('1', '1015'),
            '16': ('1', '1016'),
            '17': ('1', '1017'),
            '18': ('2', '1018'),
            '19': ('2', '1019'),
            '20': ('2', '1020'),
            '21': ('2', '1021'),
            '22': ('2', '1022'),
            '23': ('2', '1023'),
            '24': ('2', '1024'),
            '25': ('2', '1025'),
            '26': ('2', '1026'),
            '27': ('2', '1027'),
            '28': ('2', '1028'),
            '29': ('2', '1029'),
            '30': ('2', '1030'),
            '31': ('3', '1031'),
            '32': ('3', '1032'),
            '33': ('3', '1033'),
            '34': ('3', '1034'),
            '35': ('3', '1035'),
            '36': ('3', '1036'),
            '37': ('3', '1037'),
            '38': ('3', '1038'),
            '39': ('3', '1039'),
            '40': ('3', '1040'),
            '41': ('3', '1041'),
            '42': ('4', '1042'),
            '43': ('4', '1043'),
            '44': ('4', '1044'),
            '45': ('4', '1045'),
            '46': ('4', '1046'),
            '47': ('4', '1047'),
            '48': ('4', '1048'),
            '49': ('4', '1049'),
            '50': ('4', '1050'),
            '51': ('5', '1051'),
            '52': ('5', '1052'),
            '53': ('5', '1053'),
            '54': ('5', '1054'),
            '55': ('5', '1055'),
            '56': ('5', '1056'),
            '57': ('5', '1057'),
            '58': ('5', '1058'),
            '59': ('5', '1059'),
            '60': ('6', '1060'),
            '61': ('6', '1061'),
            '62': ('6', '1062'),
            '63': ('6', '1063'),
            '64': ('6', '1064'),
            '65': ('6', '1065'),
            '66': ('6', '1066'),
            '67': ('6', '1067'),
            '68': ('6', '1068'),
            '69': ('6', '1069'),
            '70': ('6', '1070'),
            '71': ('6', '1071'),
            '72': ('6', '1072'),
            '73': ('6', '1073'),
            '74': ('6', '1074'),
            '75': ('6', '1075'),
            '76': ('6', '1076'),
            '77': ('7', '1077'),
            '78': ('7', '1078'),
            '79': ('7', '1079'),
            '80': ('7', '1080'),
            '81': ('7', '1081'),
            '82': ('7', '1082'),
            '83': ('7', '1083'),
            '84': ('8', '1084'),
            '85': ('8', '1085'),
            '86': ('8', '1086'),
            '87': ('8', '1087'),
            '88': ('8', '1088'),
            '89': ('8', '1089'),
            '90': ('8', '1090'),
            '91': ('8', '1091'),
            '92': ('8', '1092'),
            '93': ('9', '1093'),
            '94': ('9', '1094'),
            '95': ('9', '1095'),
            '96': ('9', '1096'),
            '97': ('9', '1097'),
            '98': ('9', '1098'),
            '99': ('9', '1099'),
            '100': ('9', '1100'),
            '101': ('10', '1101'),
            '102': ('10', '1102'),
            '103': ('10', '1103'),
            '104': ('10', '1104'),
            '105': ('10', '1105'),
            '106': ('10', '1106'),
            '107': ('10', '1107'),
            '108': ('10', '1108'),
            '109': ('10', '1109'),
            '110': ('10', '1110'),
            '111': ('11', '1111'),
            '112': ('11', '1112'),
            '113': ('11', '1113'),
            '114': ('11', '1114'),
            '115': ('11', '1115'),
            '116': ('11', '1116'),
            '117': ('11', '1117'),
            '118': ('11', '1118'),
            '119': ('12', '1119'),
            '120': ('12', '1120'),
            '121': ('12', '1121'),
            '122': ('12', '1122'),
            '123': ('12', '1123'),
            '124': ('12', '1124'),
            '125': ('12', '1125'),
            '126': ('13', '1126'),
            '127': ('13', '1127'),
            '128': ('13', '1128'),
            '129': ('13', '1229'),
            '130': ('13', '1230'),
            '131': ('13', '1231'),
            '132': ('13', '1232'),
            '133': ('13', '1233'),
            '134': ('14', '1234'),
            '135': ('14', '1235'),
            '136': ('14', '1236'),
            '137': ('14', '1237'),
            '138': ('14', '1238'),
            '139': ('14', '1239'),
            '140': ('14', '1240'),
            '141': ('14', '1241'),
            '142': ('14', '1242'),
            '143': ('14', '1243'),
            '144': ('14', '1244'),
            '145': ('14', '1245'),
            '146': ('14', '1246'),
            '147': ('14', '1247'),
            '148': ('14', '1248'),
            '149': ('14', '1249'),
            '150': ('14', '1250'),
            '151': ('14', '1251'),
            '152': ('14', '1252'),
            '153': ('14', '1253')
        }
    },
    'subject_category': {
        'name': 'actCategoryList',
        'type': SubjectCategory,
        'all_value': '0',
        'all_flag': False,
        'value': {
            '1': '20001',
            '2': '20002',
            '3': '20003',
            '4': '20004',
            '5': '20005',
            '6': '20006',
            '7': '20007',
            '8': '20008',
            '9': '20009',
            '10': '20010',
            '11': '20011',
            '12': '20012',
            '13': '20013',
            '14': '20014',
            '15': '20015',
            '16': '20016',
            '17': '20017',
            '18': '20018',
            '19': '20019',
            '20': '20020',
            '21': '20021',
            '22': '20022',
            '23': '20023',
            '24': '20024',
            '25': '20025',
            '26': '20026',
            '27': '20027',
            '28': '20028',
            '29': '20029',
            '30': '20030',
            '31': '20031',
            '32': '20032',
            '33': '20033',
            '34': '20034',
            '35': '20035',
            '36': '20036',
            '37': '20037',
            '38': '20038',
            '39': '20039',
            '40': '30001',
            '41': '30002',
            '42': '30003',
            '43': '30004',
            '44': '30005',
            '45': '30006',
            '46': '30007',
            '47': '30008',
            '48': '30009',
            '49': '30010',
            '50': '30011',
            '51': '30012',
            '52': '30013',
            '53': '30014',
            '54': '30015',
            '55': '30016',
            '56': '30017',
            '57': '30018',
            '58': '30019',
            '59': '30020',
            '60': '30021',
            '61': '30022',
            '62': '30023',
            '63': '30024',
            '64': '30025',
            '65': '30026',
            '66': '30027',
            '67': '30028',
            '68': '30029',
            '69': '30030',
            '70': '30031',
            '71': '30032',
            '72': '30033',
            '73': '30034',
            '74': '30035',
            '75': '30036',
            '76': '30037',
            '77': '40001',
            '78': '40002',
            '79': '40003',
            '80': '40004',
            '81': '40005',
            '82': '40006',
            '83': '40007',
            '84': '40008',
            '85': '40009',
            '86': '40010',
            '87': '40011',
            '88': '40012',
            '89': '40013',
            '90': '40014',
            '91': '40015',
            '92': '40016',
            '93': '40017',
            '94': '40018',
            '95': '40019',
            '96': '40020',
            '97': '40021',
            '98': '40022',
            '99': '40023',
            '100': '40024',
            '101': '40025',
            '102': '40026',
            '103': '40027',
            '104': '40028',
            '105': '40029',
            '106': '40030'
        }
    }
}
_SEARCH_TYPE_MAP = {
    'word': 'W',
    'exam': 'E',
    'dfn': 'S',
    'ip': 'P'
}

_PEM_PATH = path.join(path.dirname(path.realpath(__file__)), path.pardir, 'korean-go-kr-chain.pem')

def _get_advanced_param(adv_mapper, value):
    if adv_mapper.get('name') != 'query' and ',' in value:
        params = []

        for val in value.split(','):
            param = _get_advanced_param(adv_mapper, val)
            if val is None:
                continue

            params.append(param)

        return ''.join(params)

    if 'value' in adv_mapper:
        value = adv_mapper['value'].get(value, value)

    if 'convert' in adv_mapper:
        return adv_mapper['convert'](value)

    return f'&{adv_mapper["name"]}={value}'

def _get_advanced_all_params(adv_mapper):
    if not 'all_params' in adv_mapper:
        all_query = []

        for value in adv_mapper['value'].values():
            all_query.append(f'&{adv_mapper["name"]}={value}')

        adv_mapper['all_params'] = ''.join(all_query)

    return adv_mapper['all_params']

def _convert_advanced_value(adv_key, adv_mapper, kwargs):
    param_value = kwargs.get(adv_key, adv_mapper.get('default'))

    if param_value is None:
        return None

    if 'type' in adv_mapper:
        return str(adv_mapper['type'].get_value(param_value, param_value))

    return str(param_value)

def _build_advanced_search_conditions(conditions):
    query = []

    for condition in conditions:
        exclude = 'exclude' in condition and condition['exclude']
        subquery = []
        subquery.append(f'&searchOp={"NOT" if exclude else "AND"}')
        empty = True

        for adv_key, adv_mapper in _ADVANCED_CONDITION_MAP.items():
            if condition.get(adv_key) is not None:
                empty = False

            param_value = _convert_advanced_value(adv_key, adv_mapper, condition)

            if param_value is None:
                continue

            param = _get_advanced_param(adv_mapper, param_value)
            if param is not None:
                subquery.append(param)

        if not empty:
            query.extend(subquery)

    return ''.join(query)

def _build_advanced_search_url(kwargs, lang_info):
    nation, code, _ = lang_info

    if 'min_syllables' in kwargs and 'max_syllables' not in kwargs:
        kwargs = kwargs.copy()
        kwargs['max_syllables'] = 80
    elif 'max_syllables' in kwargs and 'min_syllables' not in kwargs:
        kwargs = kwargs.copy()
        kwargs['min_syllables'] = 1

    query = []
    for adv_key, adv_mapper in _ADVANCED_PARAM_MAP.items():
        param_value = _convert_advanced_value(adv_key, adv_mapper, kwargs)

        if param_value is None:
            continue

        use_all = 'all_value' in adv_mapper or adv_mapper.get('default') == 'all'
        all_value = adv_mapper.get('all_value', 'all')

        if use_all and param_value == all_value:
            if adv_mapper.get('all_flag', True):
                query.append(f'&all_{adv_mapper["name"]}=ALL')
            query.append(_get_advanced_all_params(adv_mapper))
            continue

        param = _get_advanced_param(adv_mapper, param_value)
        if param is not None:
            query.append(param)

    base_condition = _build_advanced_search_conditions((kwargs,))
    conditions = _build_advanced_search_conditions(kwargs.get('search_conditions', ()))

    if base_condition or conditions:
        query.append(base_condition)
        query.append(conditions)
    else:
        query.append(_DEFAULT_ADVANCED_CONDITION)

    query = ''.join(query)
    return (
        _ADVANCED_SEARCH_URL.format(*get_language_query(nation, code), query),
        _ADVANCED_SEARCH_URL.format('', '', query)
    )

def _build_search_url(kwargs, lang_info, search_type):
    nation, code, _ = lang_info

    query = kwargs.get('query')
    page = kwargs.get('page', 1)
    per_page = kwargs.get('per_page', 10)

    sort = 'C' if SortMethod.get_value(kwargs.get('sort')) == 'popular' else 'W'
    search_type = _SEARCH_TYPE_MAP.get(search_type, 'W')

    lang_query = get_language_query(nation, code)

    url = _SEARCH_URL.format(
        *lang_query,
        query,
        page,
        per_page,
        sort,
        search_type
    )
    url_kr = _SEARCH_URL.format(
        '',
        '',
        query,
        page,
        per_page,
        sort,
        search_type
    )
    req_url = _SEARCH_REQUEST_URL.format(
        *lang_query,
        query,
        page,
        per_page,
        sort,
        search_type
    )

    return url, url_kr, req_url

def _build_sense_category_query(category):
    category = SemanticCategory.get_value(category, category)

    if category <= 0 or category > 153:
        return '&lgCategoryCode=0&miCategoryCode=-1'

    meaning_map = _ADVANCED_PARAM_MAP['semantic_category']['value']
    code_large, code_mid = meaning_map[str(category)]

    return f'&lgCategoryCode={code_large}&miCategoryCode={code_mid}'

def _build_subject_category_query(category):
    if not isiterable(category, exclude=(str,)):
        category = (category,)

    subject_map = _ADVANCED_PARAM_MAP['subject_category']['value']
    value = []

    for cat in category:
        cat_value = SubjectCategory.get_value(cat, cat)

        if cat_value == 0:
            value = []

            for i in range(1, 107):
                value.append(f'&actCategory={subject_map[str(i)]}')

            return ''.join(value)

        value.append(f'&actCategory={subject_map[str(cat_value)]}')

    return ''.join(value)

def _build_category_url(kwargs, lang_info, response_type):
    nation, code, _ = lang_info

    page = kwargs.get('page', 1)
    per_page = kwargs.get('per_page', 10)

    is_semantic = response_type == 'semantic_category'
    query_builder = (
        _build_sense_category_query if is_semantic else _build_subject_category_query
    )

    base_url = _CAT_MEANING_URL if is_semantic else _CAT_SUBJECT_URL
    sort = 'C' if SortMethod.get_value(kwargs.get('sort')) == 'popular' else 'W'
    category_query = query_builder(kwargs.get('category', 0))

    url = base_url.format(
        *get_language_query(nation, code),
        page,
        per_page,
        sort,
        category_query
    )

    url_kr = base_url.format('', '', page, per_page, sort, category_query)
    return url, url_kr

def _build_translation_language_info(trans_lang, kwargs, response_type):
    trans_language_info = []
    trans_urls = []

    info = get_language_info(trans_lang)

    if isiterable(trans_lang, exclude=(str,)):
        seen = set()

        for lang in trans_lang:
            info = get_language_info(lang)

            if info[0] == 'all':
                return _build_translation_language_info('all', kwargs, response_type)

            if not info[0] or info[2] in seen:
                continue

            seen.add(info[2])

            url_tuple = build_request_url(kwargs, response_type, info)
            trans_language_info.append({
                'lang_info': info,
                'req_url': url_tuple[2]
            })
            trans_urls.append({
                'url': url_tuple[0],
                'language': info[2]
            })

        trans_language_info = trans_language_info[1:]
        lang_info = get_language_info(trans_lang[0] if trans_lang else None)
    elif info[0] == 'all':
        lang_info = _LANG_INFO[1]
        for info in _LANG_INFO[2:]:
            url_tuple = build_request_url(kwargs, response_type, info)
            trans_language_info.append({
                'lang_info': info,
                'req_url': url_tuple[2]
            })
            trans_urls.append({
                'url': url_tuple[0],
                'language': info[2]
            })
    else:
        url_tuple = build_request_url(kwargs, response_type, info)
        lang_info = get_language_info(trans_lang)
        if lang_info[0] is not None:
            trans_urls.append({
                'url': url_tuple[0],
                'language': info[2]
            })

    return lang_info, trans_language_info, trans_urls

def build_request_url(kwargs, response_type, lang_info) -> tuple[str, str, str]:
    """
    Builds a Korean Learners' Dictionary URL and a request URL given
    request parameters.
    """

    url: str
    url_kr: str
    req_url = ''

    if response_type == 'advanced':
        url, url_kr = _build_advanced_search_url(kwargs, lang_info)

    elif response_type == 'view':
        nation, code, _ = lang_info
        target_code = kwargs.get('target_code')
        lang_query = get_language_query(nation, code)

        url_kr = _VIEW_URL.format('', '', target_code)
        url = _VIEW_URL.format(*lang_query, target_code)
        req_url = url

    elif response_type == 'word_of_the_day':
        nation, *_ = lang_info

        url_kr = _BASE_URL.format('')
        url = _BASE_URL.format(f'/{nation}' if nation else '')

    elif response_type in ('word', 'exam', 'dfn', 'ip'):
        url, url_kr, req_url = _build_search_url(kwargs, lang_info, response_type)

    elif response_type in ('semantic_category', 'subject_category'):
        url, url_kr = _build_category_url(kwargs, lang_info, response_type)

    else:
        raise ValueError

    return url, url_kr, req_url or url

def get_language_info(lang):
    """
    Returns a tuple with information about a scraper translation language.
    """

    lang = ScraperTranslationLanguage.get_value(lang)

    if lang is None:
        return (None, 0, None)

    return _LANG_INFO[lang]

def get_language_query(nation, code):
    """
    Returns query strings given a nation and nation code.
    """

    if not nation:
        return '', ''

    return f'/{nation}', f'nation={nation}&nationCode={code}&'

async def send_scrape_request(url):
    """
    Sends a request to a URL with the necessary headers for scraping,
    and returns an lxml node.
    """

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'Accept-Language': '*'}, ssl=False) as response:
                response.raise_for_status()
                return html.fromstring(await response.text())
    except Exception as exc:
        raise exc

async def send_request(kwargs, response_type):
    """
    Sends a request to a URL based on input parameters.
    """

    response_type = SearchType.get_value(response_type, response_type)

    trans_lang = kwargs.get('translation_language')

    lang_info, trans_language_info, trans_urls = _build_translation_language_info(
        trans_lang,
        kwargs,
        response_type
    )

    url, url_kr, req_url = build_request_url(kwargs, response_type, lang_info)

    return (
        await send_scrape_request(req_url),
        'word' if response_type == 'advanced' else response_type,
        url_kr,
        kwargs,
        lang_info,
        (
            trans_urls if trans_urls
            else ([{'url': url, 'language': lang_info[2]}] if lang_info[0] else [])
        ),
        trans_language_info
    )

async def send_multimedia_request(kwargs):
    """
    Sends a request to retrieve multimedia information.
    """

    media_type = MultimediaType.get_value(kwargs.get('multimedia_type'))

    if media_type not in (1, 2, 3, 4):
        raise ValueError

    url = (_IMAGE_URL if media_type in (1, 2) else _VIDEO_URL).format(
        kwargs.get('target_code'),
        kwargs.get('definition_order'),
        kwargs.get('media_order')
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'Accept-Language': '*'}, ssl=False) as response:
                response.raise_for_status()
                return html.fromstring(await response.text())
    except Exception as exc:
        raise exc
