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
    PUSHI, PUSH, POP, ADD, SUB, MULTIPLY, DIVIDE, DIV, CVR, GTR, DUP = range(11)
