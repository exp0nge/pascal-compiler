# coding=utf-8
"""
Return tokens
"""

from pascal_loader import keyword_map

TOKEN_NAME_PREFIX = 'TK_'

keyword_tokens = {}
for keyword in keyword_map.keys():
    keyword_map[keyword] = TOKEN_NAME_PREFIX + keyword.upper()

