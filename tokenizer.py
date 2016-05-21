# coding=utf-8
"""
Return tokens
"""

from pascal_loader import symbol_map, LETTER, RESERVED, SPACE, DIGIT, OPERATOR, EOL, QUOTE
from pascal_loader import PascalError, DOT, SEMICOLON, COMMENT, COMMENT_TYPES

TOKEN_NAME_PREFIX = 'TK_'
TOKEN_STRING_LIT = TOKEN_NAME_PREFIX + 'STRLIT'
TOKEN_ID = TOKEN_NAME_PREFIX + 'ID'
TOKEN_DOT = TOKEN_NAME_PREFIX + 'DOT'
TOKEN_EOF = TOKEN_NAME_PREFIX + 'EOF'
TOKEN_SEMICOLON = TOKEN_NAME_PREFIX + 'SEMICOLON'
TOKEN_COMMENT = TOKEN_NAME_PREFIX + 'COMMENT'
TOKEN_OPERATOR = TOKEN_NAME_PREFIX + 'OPERATOR'
TOKEN_OPERATOR_ASSIGNMENT = TOKEN_NAME_PREFIX + 'ASSIGNMENT'
TOKEN_OPERATOR_LEFT_PAREN = TOKEN_NAME_PREFIX + 'LPAREN'
TOKEN_OPERATOR_RIGHT_PAREN = TOKEN_NAME_PREFIX + 'RPAREN'
TOKEN_OPERATOR_PLUS = TOKEN_NAME_PREFIX + '+'
TOKEN_OPERATOR_MINUS = TOKEN_NAME_PREFIX + '-'
TOKEN_OPERATOR_DIVISION = TOKEN_NAME_PREFIX + '/'
TOKEN_OPERATOR_MULTIPLICATION = TOKEN_NAME_PREFIX + '*'
TOKEN_OPERATOR_LEFT_CHEVRON = TOKEN_NAME_PREFIX + '<'
TOKEN_OPERATOR_GTE = TOKEN_NAME_PREFIX + '>='
TOKEN_OPERATOR_RIGHT_CHEVRON = TOKEN_NAME_PREFIX + '>'
TOKEN_OPERATOR_LTE = TOKEN_NAME_PREFIX + '<='
TOKEN_OPERATOR_COLON = TOKEN_NAME_PREFIX + 'COLON'
TOKEN_OPERATOR_COMMA = TOKEN_NAME_PREFIX + 'COMMA'
TOKEN_OPERATOR_EQUALITY = TOKEN_NAME_PREFIX + '='
TOKEN_OPERATOR_NOT_EQUAL = TOKEN_NAME_PREFIX + '<>'
TOKEN_OPERATOR_LEFT_BRACKET = TOKEN_NAME_PREFIX + '['
TOKEN_OPERATOR_RIGHT_BRACKET = TOKEN_NAME_PREFIX + ']'

TOKEN_CHARACTER = TOKEN_NAME_PREFIX + 'CHARACTER'

TOKEN_DATA_TYPE_INT = TOKEN_NAME_PREFIX + 'INTEGER'
TOKEN_DATA_TYPE_RANGE = TOKEN_NAME_PREFIX + 'RANGE'
TOKEN_DATA_TYPE_ARRAY = TOKEN_NAME_PREFIX + 'ARRAY'
TOKEN_DATA_TYPE_REAL = TOKEN_NAME_PREFIX + 'REAL'
TOKEN_DATA_TYPE_CHAR = TOKEN_NAME_PREFIX + 'CHAR'
TOKEN_DATA_TYPE_BOOL = TOKEN_NAME_PREFIX + 'BOOLEAN'

TOKEN_RESERVED = TOKEN_NAME_PREFIX + 'RESERVED'

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
    """
    Returns token prefix + given suffix
    """
    return TOKEN_NAME_PREFIX + suffix.upper()


# Store reserved words with some system variables
reserved_tokens = {'integer': TOKEN_DATA_TYPE_INT,
                   'real': TOKEN_DATA_TYPE_REAL,
                   'char': TOKEN_DATA_TYPE_CHAR,
                   'boolean': TOKEN_DATA_TYPE_BOOL}
for keyword, value in symbol_map.items():
    if value == RESERVED:
        reserved_tokens[keyword.lower()] = TOKEN_RESERVED
        reserved_tokens[keyword.upper()] = TOKEN_RESERVED

# Operators dictionary
operators_classifications = {
    ':=': TOKEN_OPERATOR_ASSIGNMENT,
    '(': TOKEN_OPERATOR_LEFT_PAREN,
    ')': TOKEN_OPERATOR_RIGHT_PAREN,
    '+': TOKEN_OPERATOR_PLUS,
    '-': TOKEN_OPERATOR_MINUS,
    '/': TOKEN_OPERATOR_DIVISION,
    '<': TOKEN_OPERATOR_LEFT_CHEVRON,
    '<=': TOKEN_OPERATOR_LTE,
    '>': TOKEN_OPERATOR_RIGHT_CHEVRON,
    '>=': TOKEN_OPERATOR_GTE,
    ',': TOKEN_OPERATOR_COMMA,
    ':': TOKEN_OPERATOR_COLON,
    '*': TOKEN_OPERATOR_MULTIPLICATION,
    '=': TOKEN_OPERATOR_EQUALITY,
    '<>': TOKEN_OPERATOR_NOT_EQUAL,
    '[': TOKEN_OPERATOR_LEFT_BRACKET,
    ']': TOKEN_OPERATOR_RIGHT_BRACKET
}


def case_letter(text_segment):
    """
    Handles case for letter
    """
    suffix = ''
    for character in text_segment:
        character_value = symbol_map.get(character, None)
        if character_value == LETTER or character_value == DIGIT:
            suffix += character
        else:
            return suffix


def case_quote(text_segment, row, column):
    """
    Handles case for quote
    """
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
    """
    Handles case comment
    """
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


def case_comment_inline(text_segment):
    """
    Handles inline comments
    """
    index = 0
    word = ''
    while index < len(text_segment):
        character = text_segment[index]
        if character == '\n':
            return word
        else:
            word += character
        index += 1


def case_digit(text_segment):
    """
    Handles case digit
    """
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
        elif character_value == '-':
            suffix += character
            index += 1
        elif character_value == DOT:
            if digit_seen:
                if suffix.__contains__('.') and symbol_map.get(text_segment[index + 1]) is DOT:
                    # Got a range number .. number
                    suffix += character
                    suffix += text_segment[index + 1]
                    index += 2
                else:
                    suffix += character
                    index += 1
            else:
                raise PascalError('Invalid literal.')
        elif character.lower() == 'e':
            if text_segment[index + 1] == '-' or text_segment[index + 1] == '+':
                suffix += character
                suffix += text_segment[index + 1]
                index += 2
            elif symbol_map.get(text_segment[index + 1]) is DIGIT:
                suffix += character
                index += 1
            else:
                raise PascalError('Invalid literal.')
        else:
            return suffix


def case_operator(text_segment):
    """
    Handles case operator
    """
    index = 0
    if text_segment[index] == '(' and text_segment[index + 1] == '*':
        # could be a comment, check it
        return case_comment(text_segment[index:])
    elif text_segment[index] == ':' and text_segment[index + 1] == '=':
        # check for assignment
        return text_segment[index] + text_segment[index + 1]
    elif text_segment[index] == '<' and (text_segment[index + 1] == '=' or text_segment[index + 1] == '>'):
        # check for LTE
        return text_segment[index] + text_segment[index + 1]
    elif text_segment[index] == '>' and text_segment[index + 1] == '=':
        # check for GTE
        return text_segment[index] + text_segment[index + 1]
    elif text_segment[index] == '/' and text_segment[index + 1] == '/':
        # got a inline comment
        return case_comment_inline(text_segment[index:])
    else:
        return text_segment[index]


def get_token(pascal_file):
    """

    :param pascal_file: PascalFile
    :return:
    """
    row, column, index = 1, 1, 0
    token_list = []
    while index < len(pascal_file.contents):
        symbol = symbol_map.get(pascal_file.contents[index])
        if symbol == LETTER:
            word = case_letter(pascal_file.contents[index:])
            index += len(word)
            if reserved_tokens.get(word) is None:
                token_list.append(Token(word, TOKEN_ID, row, column))
            else:
                token_list.append(Token(word, token_name(word), row, column))
            column += len(word)
        elif symbol == DIGIT:
            word = case_digit(pascal_file.contents[index:])
            index += len(word)
            if word.count('.') == 2:
                token_list.append(Token(word, TOKEN_DATA_TYPE_RANGE, row, column))
            else:
                token_list.append(Token(word, TOKEN_DATA_TYPE_INT, row, column))
            column += len(word)
        elif symbol == SPACE:
            column += 1
            index += 1
        elif symbol == OPERATOR:
            word = case_operator(pascal_file.contents[index:])
            index += len(word)
            if word[:2] in COMMENT_TYPES:
                # checks for cases such as '//' or '(*'
                token_list.append(Token(word, TOKEN_COMMENT, row, column))
            # elif word == '-' and pascal_file.contents[index:index + 1].isdigit():
            #     # a negative number
            #     number_part = case_digit(pascal_file.contents[index:])
            #     word = word + number_part
            #     index += len(number_part)
            #     token_list.append(Token(word, TOKEN_DATA_TYPE_INT, row, column))
            else:
                token_list.append(Token(word, operators_classifications[word], row, column))
            column += len(word)
        elif symbol == QUOTE:
            word = case_quote(pascal_file.contents[index:], row, column)
            index += len(word)
            if len(word) == 3:
                token_list.append(Token(str(word.replace("'", '')), TOKEN_CHARACTER, row, column))
            else:
                token_list.append(Token(word, TOKEN_STRING_LIT, row, column))
            column += len(word)
        elif symbol == EOL:
            index += 1
            row += 1
            # reset column
            column = 1
        elif symbol == DOT:
            index += 1
            token_list.append(Token('.', TOKEN_DOT, row, column))
            column += 1
        elif symbol == SEMICOLON:
            index += 1
            token_list.append(Token(';', TOKEN_SEMICOLON, row, column))
            column += 1
        elif symbol == COMMENT:
            word = case_comment(pascal_file.contents[index:])
            index += len(word)
            token_list.append(Token(word, TOKEN_COMMENT, row, column))
            column += len(word)
        else:
            raise PascalError('Unknown symbol: %s (ln %i, col %i)' % (pascal_file.contents[index], row, column))
    token_list.append(Token('EOF', TOKEN_EOF, row, column))
    return token_list
