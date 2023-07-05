"""
Handles processing of search results, including key remapping,
type conversion, and restructuring.
"""

from collections import deque
from lxml import etree
from .types import (
    DefinitionResponse,
    ErrorResponse,
    ExampleResponse,
    IdiomProverbResponse,
    KRDictException,
    WordResponse,
    ViewResponse
)


_CONVERT_LIST = [
    'category_info',
    'conju_info',
    'sense',
    'sense_info',
    'der_info',
    'example_info',
    'multimedia_info',
    'original_language_info',
    'pattern_info',
    'pronunciation_info',
    'ref_info',
    'rel_info',
    'item',
    'subword_info',
    'subsense_info',
    'translation'
]
_CONVERT_NUM = [
    'error_code',
    'sense_order',
    'start',
    'num',
    'sup_no',
    'target_code',
    'link_target_code',
    'total'
]


def _parse_xml(xml):
    result = {}
    root = etree.fromstring(xml.encode('utf-8'), None) # pylint: disable=c-extension-no-member

    stack = deque()
    stack.append((root, result))

    while len(stack) > 0:
        node, children = stack.pop()

        for child in node.iterchildren():
            key = child.tag
            value = child.text and child.text.strip()

            # add the node to the stack if it has children
            if len(child):
                value = {}
                stack.append((child, value))
            elif not value:
                # skip empty elements with no children
                continue

            # convert expected lists to lists
            if key in _CONVERT_LIST and key not in children:
                children[key] = []

            # convert expected numbers to numbers
            if key in _CONVERT_NUM and isinstance(value, str):
                value = int(value)

            if isinstance(children.get(key), list):
                children[key].append(value)
            else:
                children[key] = value

    return {root.tag: result}

def _build_response(raw_response, request_params, search_type):
    if 'error' in raw_response:
        return ErrorResponse(raw_response, request_params)

    if search_type == 'dfn':
        return DefinitionResponse(raw_response, request_params)

    if search_type == 'exam':
        return ExampleResponse(raw_response, request_params)

    if search_type == 'ip':
        return IdiomProverbResponse(raw_response, request_params)

    if search_type == 'view':
        return ViewResponse(raw_response, request_params)

    return WordResponse(raw_response, request_params)


def parse_response(kwargs, api_response, request_params, search_type):
    """
    Transforms an HTTP response to a response object.

    - ``kwargs``: The provided input keyword arguments.
    - ``api_response``: The response returned by the API.
    - ``request_params``: The request parameters which were sent to the API.
    - ``search_type``: The type of search which was performed.
    """

    raw_response = _parse_xml(api_response)

    if kwargs.get('raise_api_errors', False) and 'error' in raw_response:
        error = raw_response['error']
        raise KRDictException(error['message'], error['error_code'], request_params)

    return _build_response(raw_response, request_params, search_type)
