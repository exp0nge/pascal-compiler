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
        self.std_out = []
        self.ip = 0
        self.data_pointer = 0

    def flush(self):
        print '----------------------------------'
        for item in self.std_out:
            print item,

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
        elif op == OPCODE.NEW_LINE:
            self.print_new_line()
            self.start()
        elif op == OPCODE.ADD:
            self.add()
            self.start()
        elif op == OPCODE.SUB:
            self.sub()
            self.start()
        elif op == OPCODE.JFALSE:
            self.jfalse()
            self.start()
        elif op == OPCODE.GTE:
            self.gte()
            self.start()
        elif op == OPCODE.LTE:
            self.lte()
            self.start()
        elif op == OPCODE.LES:
            self.les()
            self.start()
        elif op == OPCODE.GTR:
            self.gtr()
            self.start()
        elif op == OPCODE.EQL:
            self.eql()
            self.start()
        elif op == OPCODE.NEQ:
            self.neq()
            self.start()
        elif op == OPCODE.XCHG:
            self.xchg()
            self.start()
        elif op == OPCODE.CVR:
            self.cvr()
            self.start()
        elif op == OPCODE.HALT:
            print 'End of program.'
            self.flush()
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
        return self.data_array[self.immediate_value()]

    def pop(self):
        self.ip += 1
        popped_value = self.stack.pop()
        self.data_pointer = self.immediate_value()
        self.data_array[self.data_pointer] = popped_value
        self.data_pointer += 1
        return popped_value

    def print_i(self):
        self.ip += 1
        self.std_out.append(self.immediate_data())

    def push(self):
        self.ip += 1
        self.stack.append(self.immediate_data())

    def print_new_line(self):
        self.ip += 1
        self.std_out.append('\n')

    def sub(self):
        self.ip += 1
        right = self.stack.pop()
        self.stack.append(self.stack.pop() - right)

    def add(self):
        self.ip += 1
        add = self.stack.pop() + self.stack.pop()
        self.stack.append(add)

    def jfalse(self):
        self.ip += 1
        if self.stack.pop():
            self.immediate_value()
        else:
            self.ip = self.immediate_value()

    def gte(self):
        self.ip += 1
        self.stack.append(self.stack.pop() <= self.stack.pop())

    def gtr(self):
        self.ip += 1
        self.stack.append(self.stack.pop() > self.stack.pop())

    def lte(self):
        self.ip += 1
        self.stack.append(self.stack.pop() >= self.stack.pop())

    def les(self):
        self.ip += 1
        self.stack.append(self.stack.pop() < self.stack.pop())

    def eql(self):
        self.ip += 1
        self.stack.append(self.stack.pop() == self.stack.pop())

    def neq(self):
        self.ip += 1
        self.stack.append(self.stack.pop() != self.stack.pop())

    def xchg(self):
        self.ip += 1
        print self.stack
        top = self.stack.pop()
        bottom = self.stack.pop()
        self.stack.append(top)
        self.stack.append(bottom)

    def cvr(self):
        self.ip += 1
        self.stack.append(float(self.stack.pop()))
