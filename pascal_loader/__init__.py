# coding=utf-8
# coding=utf-8

LETTER = 0
RESERVED = 1
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

symbol_map = {}
keyword_map = {}

for character in ALPHABET:
    symbol_map[character] = LETTER
    symbol_map[character.lower()] = LETTER

with open('keywords.txt') as keyword_file:
    for line in keyword_file.readlines():
        # Read every line while stripping whitespace and store reserved keywords
        keyword_map[line.split()] = RESERVED
