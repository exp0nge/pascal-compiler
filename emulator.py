# coding=utf-8
"""
Emulator for pascal compiled code
"""


class Emulator(object):
    """
    Emulator for Parser generated binary code
    """
    def __init__(self, byte_array):
        self.byte_array = byte_array
