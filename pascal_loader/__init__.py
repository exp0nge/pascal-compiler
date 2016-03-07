# coding=utf-8
"""
Initial setup for different dictionaries like symbol/reserved keywords
"""
import os

LETTER = 0
RESERVED = 1
SPACE = 2
DIGIT = 3
OPERATOR = 4
QUOTE = 5
EOL = 6
DOT = 7
COMMENT = 8
SEMICOLON = 9
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
OPERATORS = '+-,()<>'

symbol_map = {' ': SPACE,
              '\n': EOL,
              '\'': QUOTE,
              '.': DOT,
              '{*': COMMENT,
              ';': SEMICOLON}

for character in ALPHABET:
    symbol_map[character] = LETTER
    symbol_map[character.lower()] = LETTER

for operator in OPERATORS:
    symbol_map[operator] = OPERATOR

for digit in range(0, 10):
    symbol_map[digit] = DIGIT
    symbol_map[str(digit)] = DIGIT

with open(os.path.join(__name__, 'keywords.txt')) as keyword_file:
    for line in keyword_file.readlines():
        # Read every line while stripping whitespace and store reserved keywords
        symbol_map[line.strip()] = RESERVED


class PascalError(Exception):
    pass
