# coding=utf-8
"""
Return tokens
"""

from pascal_loader import symbol_map, LETTER, RESERVED, SPACE, DIGIT, OPERATOR, EOL, QUOTE
from pascal_loader import PascalError, DOT, SEMICOLON

TOKEN_NAME_PREFIX = 'TK_'
TOKEN_STRING_LIT = TOKEN_NAME_PREFIX + 'STRLIT'
TOKEN_INT_LIT = TOKEN_NAME_PREFIX + 'INTLIT'
TOKEN_EOF = TOKEN_NAME_PREFIX + 'DOT'
TOKEN_SEMICOLON = TOKEN_NAME_PREFIX + ';'

string_store = set()


def token_name(suffix):
    return TOKEN_NAME_PREFIX + suffix.upper()

keyword_tokens = {}
for keyword, value in symbol_map.items():
    if value == RESERVED:
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
            if character_value == EOL:
                # TODO: row/column number
                raise PascalError('Not a valid string.')
            suffix += character


def case_digit(text_segment):
    suffix = ''
    valid_float = False
    for character in text_segment:
        character_value = symbol_map.get(character, None)
        if character_value == DIGIT:
            suffix += character
            valid_float = True
        elif character_value == DOT:
            if valid_float:
                if suffix.__contains__('.'):
                    # Does scanner throw error .5?
                    raise PascalError('Not a valid float.')
                else:
                    suffix += character
            else:
                raise PascalError('')
        else:
            return suffix


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
        if symbol == LETTER:
            word = case_letter(pascal_file.contents[index:])
            index += len(word)
            if keyword_tokens.get(word) is not None:
                print keyword_tokens.get(word)
            else:
                print token_name(word)
        elif symbol == DIGIT:
            word = case_digit(pascal_file.contents[index:])
            index += len(word)
            print TOKEN_INT_LIT, word.replace('\'', '')
        elif symbol == SPACE:
            index += 1
        elif symbol == OPERATOR:
            print token_name(pascal_file.contents[index])
            index += 1
        elif symbol == QUOTE:
            word = case_quote(pascal_file.contents[index:])
            index += len(word)
            print TOKEN_STRING_LIT, word
        elif symbol == EOL:
            index += 1
            line_number += 1
        elif symbol == DOT:
            print TOKEN_EOF
            index += 1
        elif symbol == SEMICOLON:
            print TOKEN_SEMICOLON
            index += 1
        else:
            index += 1
            print 'else %i' % symbol
    print token_name('EOF')
