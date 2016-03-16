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
TOKEN_SEMICOLON = TOKEN_NAME_PREFIX + 'SEMICOLON'
TOKEN_COMMENT = TOKEN_NAME_PREFIX + 'COMMENT'
TOKEN_ASSIGNMENT = TOKEN_NAME_PREFIX + 'ASSIGNMENT'
TOKEN_QUOTE = TOKEN_NAME_PREFIX + 'QUOTE'
TOKEN_COMMA = TOKEN_NAME_PREFIX + 'COMMA'
TOKEN_OPERATOR = TOKEN_NAME_PREFIX + 'OPERATOR'

string_store = set()


class Token(object):
    """
    Token object class
    """
    def __init__(self, value_of, type_of, row, column):
        self.value_of = value_of
        self.type_of = type_of
        self.row = row
        self.column = column

    def __unicode__(self):
        return '<%s, %s, %i, %i>' % (self.value_of, self.type_of, self.row, self.column)

    def __repr__(self):
        return self.__unicode__()


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


def case_quote(text_segment, row, column):
    suffix = ''
    first_quote = False
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
            if character == '\n':
                row += 1
            if character_value == EOL:
                column += len(suffix)
                raise PascalError('Not a valid string. (ln %i,col %i)' % (row, column))
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
                    suffix += character
                    suffix += text_segment[index + 1]
                    index += 2
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
    row, column, index = 1, 0, 0
    while index < len(pascal_file.contents):
        symbol = symbol_map.get(pascal_file.contents[index])
        if symbol == LETTER:
            word = case_letter(pascal_file.contents[index:])
            index += len(word)
            print Token(word, TOKEN_STRING_LIT, row, column)
            column += len(word)
        elif symbol == DIGIT:
            word = case_digit(pascal_file.contents[index:])
            index += len(word)
            print Token(word, TOKEN_INT_LIT, row, column)
            column += len(word)
        elif symbol == SPACE:
            column += 1
            index += 1
        elif symbol == OPERATOR:
            if pascal_file.contents[index] == '(' and pascal_file.contents[index + 1] == '*':
                # could be a comment, check it
                word = case_comment(pascal_file.contents[index:])
                index += len(word)
                print Token(word, TOKEN_COMMENT, row, column)
                column += len(word)
            elif pascal_file.contents[index] == ':' and pascal_file.contents[index + 1] == '=':
                # check for assignment
                word = pascal_file.contents[index] + pascal_file.contents[index + 1]
                index += len(word)
                print Token(word, TOKEN_ASSIGNMENT, row, column)
                column += len(word)
            else:
                word = pascal_file.contents[index]
                index += 1
                print Token(word, TOKEN_OPERATOR, row, column)
        elif symbol == QUOTE:
            word = case_quote(pascal_file.contents[index:], row, column)
            index += len(word)
            print Token(word, TOKEN_QUOTE, row, column)
            column += len(word)
        elif symbol == EOL:
            index += 1
            row += 1
            column = 0
        elif symbol == DOT:
            index += 1
            print Token('.', TOKEN_EOF, row, column)
            column += 1
        elif symbol == SEMICOLON:
            index += 1
            print Token(';', TOKEN_SEMICOLON, row, column)
            column += 1
        elif symbol == COMMENT:
            word = case_comment(pascal_file.contents[index:])
            index += len(word)
            print Token(word, TOKEN_COMMENT, row, column)
            column += len(word)
        else:
            index += 1
            raise PascalError('Unknown symbol: %s (ln %i, col %i)' % (symbol, row, column))
    print Token('EOF', TOKEN_EOF, row, column)
    print 'string store:', string_store
