# coding=utf-8
from __future__ import absolute_import

import pprint

from tokenizer import get_token
from pascal_loader.main_io import PascalFile
from parse import Parser
from emulator import Emulator

if __name__ == '__main__':
    pretty_printer = pprint.PrettyPrinter()
    # tokens = get_token(PascalFile(input_file_location='simple_assignment.pas', output_location=''))
    # tokens = get_token(PascalFile(input_file_location='assignments.pas', output_location=''))
    # tokens = get_token(PascalFile(input_file_location='control_repeat.pas', output_location=''))
    # tokens = get_token(PascalFile(input_file_location='control_while.pas', output_location=''))
    # tokens = get_token(PascalFile(input_file_location='control_if.pas', output_location=''))
    # tokens = get_token(PascalFile(input_file_location='control_for.pas', output_location=''))
    # tokens = get_token(PascalFile(input_file_location='case_statement.pas', output_location=''))
    tokens = get_token(PascalFile(input_file_location='arrays.pas', output_location=''))
    # tokens = get_token(PascalFile(input_file_location='procedures.pas', output_location=''))

    pretty_printer.pprint(tokens)  # This prints tokens, comment it out to not see them
    print '----------------------------------'
    parser = Parser(token_list=tokens)
    byte_array = parser.parse()
    pretty_printer.pprint(byte_array)  # This prints the byte array
    print '----------------------------------'
    emulator = Emulator(byte_array)
    emulator.start()
