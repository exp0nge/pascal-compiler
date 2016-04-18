# coding=utf-8
from pascal_loader import PascalError
import pascal_loader.symbol_tables as symbol_tables
import tokenizer
from constants import OPCODE


class Parser(object):
    def __init__(self, token_list):
        self.token_list = iter(token_list)
        self.current_token = None
        self.ip = 0
        self.symbol_table = []
        self.byte_array = bytearray()

    def find_name_in_symbol_table(self, name):
        """

        :param name: str
        :return: SymbolObject
        """
        for symbol in self.symbol_table:
            if symbol.name == name:
                return symbol
        return None

    def match(self, token_type):
        """
        :param token_type: str
        :return:
        """
        if self.current_token.type_of == token_type:
            print 'matched: ', token_type, self.current_token.value_of
            self.current_token = self.token_list.next()
        else:
            raise PascalError('Token mismatch with %s and %s (%i, %i)' % (str(token_type),
                                                                          str(self.current_token),
                                                                          self.current_token.row,
                                                                          self.current_token.column))

    def generate_op_code(self, op_code):
        self.byte_array.append(op_code)
        self.ip += 1

    def generate_address(self, targer):
        pass

    def variable_declaration(self):
        """

        :return:
        """
        self.match('TK_VAR')
        declarations = []
        data_type = None
        while self.current_token.type_of == tokenizer.TOKEN_ID:
            # should not be present in the current symbol table
            if self.current_token.value_of in declarations:
                raise PascalError('Variable already declared: %s (%i, %i)' % (self.current_token.value_of,
                                                                              self.current_token.row,
                                                                              self.current_token.column))
            declarations.append(self.current_token.value_of)
            self.match(tokenizer.TOKEN_ID)
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
        # store in symbol table
        for variable in declarations:
            self.symbol_table.append(symbol_tables.SymbolObject(name=variable,
                                                                type_of_object=symbol_tables.TYPE_VARIABLE,
                                                                kind=data_type))
            self.ip += 1
        # check for more var
        if self.current_token.type_of == 'TK_VAR':
            self.variable_declaration()
        else:
            # no more declarations
            self.begin()

    def begin(self):
        self.match('TK_BEGIN')
        if self.current_token.type_of == tokenizer.TOKEN_ID:
            self.statement()

    def statement(self):
        lhs_type, lhs_address = None, None
        if self.current_token.type_of == tokenizer.TOKEN_ID:
            symbol = self.find_name_in_symbol_table(self.current_token.value_of)
            if symbol is None:
                raise PascalError('Variable %s is not declared (%i, %i)' % (self.current_token.value_of,
                                                                            self.current_token.row,
                                                                            self.current_token.column))
            lhs_type = symbol.kind
            self.match(tokenizer.TOKEN_ID)
        else:
            lhs_type = tokenizer.TOKEN_DATA_TYPE_INT
            self.match(tokenizer.TOKEN_DATA_TYPE_INT)
        # check for assignment
        if self.current_token.type_of == tokenizer.TOKEN_OPERATOR_ASSIGNMENT:
            self.assignment(lhs_type, lhs_address)
        else:
            return lhs_type

    def assignment(self, lhs_type, lhs_address):
        self.match(tokenizer.TOKEN_OPERATOR_ASSIGNMENT)
        rhs_type = self.expression()
        if rhs_type == tokenizer.TOKEN_DATA_TYPE_INT:
            if lhs_type != tokenizer.TOKEN_DATA_TYPE_INT:
                raise PascalError('Type mismatch %s (%i, %i)' % (self.current_token.value_of,
                                                                 self.current_token.row,
                                                                 self.current_token.column))
        elif rhs_type == tokenizer.TOKEN_DATA_TYPE_REAL:
            pass
        elif rhs_type == tokenizer.TOKEN_DATA_TYPE_CHAR:
            pass
        elif rhs_type == 'TK_BOOL':
            pass
        else:
            # didn't find appropriate supported type on RHS
            raise PascalError('Type unsupported %s (%i, %i)' % (rhs_type,
                                                                self.current_token.row,
                                                                self.current_token.column))

    def parse(self):
        self.current_token = self.token_list.next()
        self.match('TK_PROGRAM')
        self.match(tokenizer.TOKEN_ID)
        self.match(tokenizer.TOKEN_SEMICOLON)
        # either we see var or begin
        if self.current_token.type_of == 'TK_VAR':
            self.variable_declaration()
        else:
            self.begin()

    def expression(self):
        tail_1 = self.t()
        while self.current_token.type_of == tokenizer.TOKEN_OPERATOR_PLUS or self.current_token.type_of == tokenizer.TOKEN_OPERATOR_MINUS:
            operator = self.current_token.type_of
            self.match(operator)
            tail_2 = self.t()
            tail_1 = self.emit(operator, tail_1, tail_2)

    def t(self):
        self.f()
        self.t_prime()

    def t_prime(self):
        token_type = self.current_token.type_of
        if token_type == tokenizer.TOKEN_OPERATOR_MULTIPLICATION:
            pass
        elif token_type == tokenizer.TOKEN_OPERATOR_DIVISION:
            pass
        else:
            return

    def f(self):
        token_type = self.current_token.type_of
        if token_type == tokenizer.TOKEN_ID:
            pass
        elif token_type == tokenizer.TOKEN_STRING_LIT:
            pass
        elif token_type == tokenizer.TOKEN_OPERATOR_PLUS:
            pass
        elif token_type == tokenizer.TOKEN_OPERATOR_MINUS:
            pass
        elif token_type == tokenizer.TOKEN_OPERATOR_LEFT_PAREN:
            pass
        else:
            raise PascalError('F() fails on %s' % token_type)
