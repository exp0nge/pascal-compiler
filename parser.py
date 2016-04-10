# coding=utf-8
from pascal_loader import PascalError
from pascal_loader.symbol_tables import SymbolObject
import tokenizer


class Parser(object):
    def __init__(self, token_list):
        self.token_list = iter(token_list)
        self.current_token = None
        self.symbol_table = []

    def match(self, token_type):
        """
        :param token_type: str
        :return:
        """
        if self.current_token.type_of == token_type:
            self.current_token = self.token_list.next()
        else:
            raise PascalError('Token mismatch with ' + str(token_type))

    def variable_declarations(self):
        self.match('TK_VAR')
        declarations = []
        while self.current_token.type_of == tokenizer.TOKEN_STRING_LIT:
            # should not be present in the current symbol table
            declarations.append(self.current_token.value_of)
            self.match(tokenizer.TOKEN_COMMA)
        self.match(tokenizer.TOKEN_OPERATOR_COLON)

    def begin(self):
        return

    def parse(self):
        self.current_token = self.token_list.next()
        self.match('TK_PROGRAM')
        self.match(tokenizer.TOKEN_STRING_LIT)
        self.match(tokenizer.TOKEN_SEMICOLON)
        # either we see var or begin
        if self.current_token.type_of == 'TK_VAR':
            self.variable_declarations()
        else:
            self.begin()
