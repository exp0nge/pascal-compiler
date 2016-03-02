# coding=utf-8
"""
Return tokens
"""

from pascal_loader import symbol_map, LETTER, RESERVED, SPACE, DIGIT, OPERATOR, EOL, QUOTE

TOKEN_NAME_PREFIX = 'TK_'
TOKEN_STRING_LIT = TOKEN_NAME_PREFIX + 'STRLIT'

string_store = set()


def token_name(suffix):
    return TOKEN_NAME_PREFIX + suffix.upper()

keyword_tokens = {}
for keyword, value in symbol_map.items():
    if value == 1:
        keyword_tokens[keyword.lower()] = TOKEN_NAME_PREFIX + keyword.upper()
        keyword_tokens[keyword.upper()] = TOKEN_NAME_PREFIX + keyword.upper()


def case_letter(text_segment):
    suffix = ''
    for character in text_segment:
        character_value = symbol_map.get(character, None)
        if character_value == LETTER or character_value == DIGIT:
            suffix += character
        else:
            return suffix


def case_quote(text_segment):
    suffix = ''
    first_quote = False
    escape_check = False
    for character in text_segment:
        character_value = symbol_map.get(character, None)
        if character_value == QUOTE:
            if first_quote:
                suffix += character
                string_store.add(suffix.replace('\'', ''))
                return suffix
            else:
                suffix += character
                first_quote = True
        else:
            suffix += character


def get_token(pascal_file):
    """

    :param pascal_file: PascalFile
    :return:
    """
    line_number = 0
    column_number = 0
    state = False, False
    index = 0
    while index < len(pascal_file.contents):
        symbol = symbol_map[pascal_file.contents[index]]
        print symbol
        if symbol == LETTER:
            word = case_letter(pascal_file.contents[index:])
            index += len(word)
            print token_name(word)
        elif symbol == DIGIT:
            index += 1
        elif symbol == SPACE:
            index += 1
        elif symbol == OPERATOR:
            index += 1
        elif symbol == QUOTE:
            word = case_quote(pascal_file.contents[index:])
            index += len(word)
            print TOKEN_STRING_LIT
        elif symbol == EOL:
            index += 1
            line_number += 1
        else:
            index += 1
            print symbol
