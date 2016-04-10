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
            print 'matched: ', token_type
            self.current_token = self.token_list.next()
        else:
            raise PascalError('Token mismatch with %s and %s (%i, %i)' % (str(token_type),
                                                                          str(self.current_token),
                                                                          self.current_token.row,
                                                                          self.current_token.column))

    def variable_declarations(self):
        self.match('TK_VAR')
        declarations = []
        data_type = None
        while self.current_token.type_of == tokenizer.TOKEN_STRING_LIT:
            # should not be present in the current symbol table
            declarations.append(self.current_token.value_of)
            self.match(tokenizer.TOKEN_STRING_LIT)
            if self.current_token.type_of == tokenizer.TOKEN_OPERATOR_COMMA:
                # this allows multiple declarations in same line
                self.match(tokenizer.TOKEN_OPERATOR_COMMA)
        self.match(tokenizer.TOKEN_OPERATOR_COLON)
        # check what type of data type declarations are
        if self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_INT:
            self.match(tokenizer.TOKEN_DATA_TYPE_INT)
            data_type = tokenizer.TOKEN_DATA_TYPE_INT
        elif self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_REAL:
            self.match(tokenizer.TOKEN_DATA_TYPE_REAL)
            data_type = tokenizer.TOKEN_DATA_TYPE_REAL
        elif self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_CHAR:
            self.match(tokenizer.TOKEN_DATA_TYPE_CHAR)
            data_type = tokenizer.TOKEN_DATA_TYPE_CHAR
        elif self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_BOOL:
            self.match(tokenizer.TOKEN_DATA_TYPE_BOOL)
            data_type = tokenizer.TOKEN_DATA_TYPE_BOOL
        else:
            raise PascalError('%s data type is invalid' % self.current_token.value_of)
        self.match(tokenizer.TOKEN_SEMICOLON)
        # check for more var
        if self.current_token.type_of == 'TK_VAR':
            self.variable_declarations()

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
