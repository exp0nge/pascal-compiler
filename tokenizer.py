# coding=utf-8
"""
Return tokens
"""

from pascal_loader import symbol_map, LETTER, RESERVED, SPACE, DIGIT, OPERATOR, EOL, QUOTE
from pascal_loader import PascalError, DOT, SEMICOLON, COMMENT

TOKEN_NAME_PREFIX = 'TK_'
TOKEN_STRING_LIT = TOKEN_NAME_PREFIX + 'STRLIT'
TOKEN_INT_LIT = TOKEN_NAME_PREFIX + 'INTLIT'
TOKEN_EOF = TOKEN_NAME_PREFIX + 'DOT'
TOKEN_SEMICOLON = TOKEN_NAME_PREFIX + ';'
TOKEN_COMMENT = TOKEN_NAME_PREFIX + 'COMMENT'
TOKEN_ASSIGNMENT = TOKEN_NAME_PREFIX + 'ASSIGNMENT'

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


def case_comment(text_segment):
    index = 0
    word = ''
    while index < len(text_segment):
        character = text_segment[index]
        if character == '}':
            return word + character
        elif character == '*' and text_segment[index + 1] == ')':
            # handle (* *) style comments
            return word + character + text_segment[index + 1]
        else:
            word += character
            index += 1


def case_digit(text_segment):
    suffix = ''
    digit_seen = False
    index = 0
    while index < len(text_segment):
        character = text_segment[index]
        character_value = symbol_map.get(character, None)
        if character_value == DIGIT:
            suffix += character
            digit_seen = True
            index += 1
        elif character_value == DOT:
            if digit_seen:
                # TODO: handle 3..2, 3 tokens
                if suffix.__contains__('.') and symbol_map.get(text_segment[index + 1]) is DOT:
                    # Got a range number .. number
                    pass
                else:
                    suffix += character
                    index += 1
            else:
                raise PascalError('')
        elif character.lower() == 'e':
            if text_segment[index + 1] == '-':
                suffix += character
                suffix += text_segment[index + 1]
                index += 2
            elif symbol_map.get(text_segment[index + 1]) is DIGIT:
                suffix += character
                index += 1
            else:
                raise PascalError('Not a valid float.')
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
        symbol = symbol_map.get(pascal_file.contents[index])
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
            column_number += 1
            index += 1
        elif symbol == OPERATOR:
            if pascal_file.contents[index] == '(' and pascal_file.contents[index + 1] == '*':
                # could be a comment, check it
                word = case_comment(pascal_file.contents[index:])
                print TOKEN_COMMENT, word
                index += len(word)
            elif pascal_file.contents[index] == ':' and pascal_file.contents[index + 1] == '=':
                word = pascal_file.contents[index] + pascal_file.contents[index + 1]
                print TOKEN_ASSIGNMENT, word
                index += len(word)
            else:
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
        elif symbol == COMMENT:
            word = case_comment(pascal_file.contents[index:])
            index += len(word)
            print TOKEN_COMMENT, word
        else:
            index += 1
            print symbol
    print token_name('EOF')
    print 'string store:', string_store
