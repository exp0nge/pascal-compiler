# coding=utf-8
"""
Emulator for pascal compiled code
"""

from pascal_loader import PascalError

from constants import OPCODE, byte_unpacker, bits_to_float
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
        print 'Flushing standard out'
        print '----------------------------------'
        for item in self.std_out:
            print item,

    def start(self):
        op = self.byte_array[self.ip]
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
        elif op == OPCODE.PRINT_ILIT:
            self.print_ilit()
            self.start()
        elif op == OPCODE.PRINT_C:
            self.print_c()
            self.start()
        elif op == OPCODE.NEW_LINE:
            self.print_new_line()
            self.start()
        elif op == OPCODE.ADD:
            self.add()
            self.start()
        elif op == OPCODE.FADD:
            self.f_add()
            self.start()
        elif op == OPCODE.SUB:
            self.sub()
            self.start()
        elif op == OPCODE.FSUB:
            self.f_sub()
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
        elif op == OPCODE.JMP:
            self.jmp()
            self.start()
        elif op == OPCODE.POP_CHAR:
            self.pop_char()
            self.start()
        elif op == OPCODE.MULTIPLY:
            self.multiply()
            self.start()
        elif op == OPCODE.FMULTIPLY:
            self.f_multiply()
            self.start()
        elif op == OPCODE.HALT:
            print 'Finished simulating program.'
            self.flush()
            sys.exit()
        elif op == OPCODE.PUSH_CHAR:
            self.push_char()
            self.start()
        elif op == OPCODE.DIVIDE:
            self.divide()
            self.start()
        elif op == OPCODE.DUMP:
            self.dump()
            self.start()
        elif op == OPCODE.RETRIEVE:
            self.retrieve()
            self.start()
        elif op == OPCODE.PRINT_B:
            self.print_b()
            self.start()
        elif op == OPCODE.PRINT_R:
            self.print_r()
            self.start()
        else:
            print 'Stack', self.stack
            raise PascalError('Emulator lacks support for opcode %i' % op)

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
            imm = self.immediate_value()
            self.ip = imm

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
        top = self.stack.pop()
        bottom = self.stack.pop()
        self.stack.append(top)
        self.stack.append(bottom)

    def cvr(self):
        self.ip += 1
        self.stack.append(float(self.stack.pop()))

    def jmp(self):
        self.ip += 1
        self.ip = self.immediate_value()

    def print_ilit(self):
        self.ip += 1
        v = self.immediate_value()
        self.std_out.append(v)

    def pop_char(self):
        self.ip += 1
        popped_value = self.stack.pop()
        self.data_pointer = self.immediate_value()
        self.data_array[self.data_pointer] = popped_value
        self.data_pointer += 1
        return popped_value

    def push_char(self):
        self.ip += 1
        self.stack.append(chr(self.immediate_value()))

    def multiply(self):
        self.ip += 1
        self.stack.append(self.stack.pop() * self.stack.pop())

    def divide(self):
        self.ip += 1
        denom = bits_to_float(self.stack.pop())
        self.stack.append(self.stack.pop() / float(denom))

    def print_c(self):
        self.ip += 1
        self.std_out.append(self.data_array[self.immediate_value()])

    def f_multiply(self):
        self.ip += 1
        self.stack.append(float(self.stack.pop()) * float(self.stack.pop()))

    def f_add(self):
        self.ip += 1
        self.stack.append(float(self.stack.pop()) + float(self.stack.pop()))

    def f_sub(self):
        self.ip += 1
        right = float(self.stack.pop())
        self.stack.append(float(self.stack.pop()) - right)

    def dump(self):
        self.ip += 1
        assignment = self.stack.pop()
        self.data_pointer = self.stack.pop()
        self.data_array[self.data_pointer] = assignment
        self.data_pointer += 1

    def retrieve(self):
        self.ip += 1
        self.data_pointer = self.stack.pop()
        self.stack.append(self.data_array[self.data_pointer])
        # self.std_out.append(self.data_array[self.data_pointer])

    def print_b(self):
        self.ip += 1
        boolean = self.immediate_data()
        self.std_out.append('true' if boolean == 1 else 'false')

    def print_r(self):
        self.ip += 1
        # self.std_out.append('{0:.2f}'.format(bits_to_float(self.immediate_value())))
        self.std_out.append(self.immediate_data())
