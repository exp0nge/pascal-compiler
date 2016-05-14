# coding=utf-8
"""
Emulator for pascal compiled code
"""

from constants import OPCODE, byte_unpacker, byte_packer
import sys


class Emulator(object):
    """
    Emulator for Parser generated binary code
    """

    def __init__(self, byte_array):
        self.data_array = {}
        self.stack = []
        self.byte_array = byte_array
        self.ip = 0
        self.data_pointer = 0

    def start(self):
        print 'IP', self.ip
        op = self.byte_array[self.ip]
        print 'Matching', op
        if op == OPCODE.PUSHI:
            self.pushi()
            self.start()
        elif op == OPCODE.POP:
            self.pop()
            self.start()
        elif op == OPCODE.PUSH:
            self.push()
            self.start()
        elif op == OPCODE.PRINT_I:
            self.print_i()
            self.start()
        elif op == OPCODE.HALT:
            print 'End of program.'
            sys.exit()
        else:
            print 'Can\'t match', op
            print 'Stack', self.stack

    def pushi(self):
        self.ip += 1
        self.stack.append(self.immediate_value())

    def immediate_value(self):
        immediate = bytearray()
        for i in range(4):
            immediate.append(self.byte_array[self.ip])
            self.ip += 1
        return byte_unpacker(immediate)

    def immediate_data(self):
        # self.data_pointer = self.immediate_value()
        # print '-->', self.data_pointer
        # data = bytearray()
        # for i in range(4):
        #     data.append(self.data_array[self.data_pointer])
        #     self.data_pointer += 1
        # return byte_unpacker(data)
        return self.byte_array[self.immediate_value()]

    def pop(self):
        self.ip += 1
        popped_value = self.stack.pop()
        self.data_pointer = self.immediate_value()
        self.data_array[self.data_pointer] = popped_value
        self.data_pointer += 1
        return popped_value

    def print_i(self):
        self.ip += 1
        print 'stdout', self.immediate_data()

    def push(self):
        self.ip += 1
        self.stack.append(self.immediate_data())

