# coding=utf-8

LETTER = 0
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

symbol_map = {}

for character in ALPHABET:
    symbol_map[character] = LETTER
    symbol_map[character.lower()] = LETTER
