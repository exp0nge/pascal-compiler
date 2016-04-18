# coding=utf-8
"""
http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
"""


class OPCODE(object):
    PUSHI, PUSH, POP, ADD, SUB, DIV, CVR, GTR = range(8)
