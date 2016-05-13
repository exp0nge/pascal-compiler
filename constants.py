# coding=utf-8
"""
http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
"""


class OPCODE(object):
    """
    PUSHI: push immediate
    PUSH: push
    POP:
    ADD:
    SUB:
    MULTIPLY:
    DIVIDE:
    DIV:
    CVR:
    """
    PUSHI = 0
    PUSH = 1
    POP = 2
    ADD = 3
    SUB = 4
    MULTIPLY = 5
    DIVIDE = 6
    DIV = 7
    CVR = 8
    GTR = 9
    DUP = 10
    JMP = 11
    JFALSE = 12
    JTRUE = 13
    HALT = 14
    PRINT_I = 15
    PRINT_C = 16
    PRINT_B = 17
    PRINT_R = 18


class TYPE(object):
    I, R, B, C, S = range(5)
