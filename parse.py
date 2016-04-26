# coding=utf-8
from pascal_loader import PascalError
import pascal_loader.symbol_tables as symbol_tables
import tokenizer
from constants import OPCODE, TYPE


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

    def byte_packer(self, value_to_pack):
        """
        Expands value to four bytes to be stored in bytearray
        :param value_to_pack: number
        :return: tuple
        """
        value_to_pack = int(value_to_pack)
        return (value_to_pack >> 24) & 0xFF, (value_to_pack >> 16) & 0xFF, (
            value_to_pack >> 8) & 0xFF, value_to_pack & 0xFF

    def byte_unpacker(self, byte_list):
        return (byte_list[0] << 24) | (byte_list[1] << 16) | (byte_list[2] << 8) | (byte_list[3])

    def generate_op_code(self, op_code):
        """
        Appends op_code to byte array then increments IP
        :param op_code: int
        :return:
        """
        self.byte_array.append(op_code)
        self.ip += 1

    def generate_address(self, target):
        """
        Packs target into four bytes and appends to bytearray and increments IP by 4
        :param target: number
        :return:
        """
        for byte in self.byte_packer(target):
            self.byte_array.append(byte)
        self.ip += 4

    def parse(self):
        """
        Starts the parser to generate instructions in byte_array
        :return:
        """
        self.current_token = self.token_list.next()
        self.match('TK_PROGRAM')
        self.match(tokenizer.TOKEN_ID)
        self.match(tokenizer.TOKEN_SEMICOLON)
        # either we see var or begin
        if self.current_token.type_of == 'TK_VAR':
            self.variable_declaration()
        else:
            self.begin()

    def variable_declaration(self):
        """
        Takes care of: var [a,b,] : [type];
        :return:
        """
        self.match('TK_VAR')
        declarations = []
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
                                                                data_type=data_type))
        # check for more var
        if self.current_token.type_of == 'TK_VAR':
            self.variable_declaration()
        else:
            # no more declarations
            self.begin()

    def begin(self):
        """
        Takes care of `begin`
        :return:
        """
        self.match('TK_BEGIN')
        self.statements()

    def statements(self):
        type_of = self.current_token.type_of
        if self.current_token.type_of == tokenizer.TOKEN_ID:
            self.assignment_statement()
        elif type_of == 'TK_WHILE':
            pass

    def find_name_or_error(self):
        symbol = self.find_name_in_symbol_table(self.current_token.value_of)
        if symbol is None:
            raise PascalError('Variable %s is not declared (%i, %i)' % (self.current_token.value_of,
                                                                        self.current_token.row,
                                                                        self.current_token.column))
        else:
            return symbol

    def assignment_statement(self):
        lhs_address = self.ip
        symbol = self.find_name_or_error()
        lhs_type = symbol.data_type
        self.match(tokenizer.TOKEN_ID)
        self.match(tokenizer.TOKEN_OPERATOR_ASSIGNMENT)
        rhs_type = self.e()
        if lhs_type == rhs_type:
            self.generate_address(lhs_address)
            print lhs_type, rhs_type
            for b in self.byte_array:
                print b
        else:
            raise PascalError('Type mismatch %s != %s' % (lhs_type, rhs_type))

    def e(self):
        t1 = self.t()
        while self.current_token.type_of == tokenizer.TOKEN_OPERATOR_PLUS or self.current_token.type_of == tokenizer.TOKEN_OPERATOR_MINUS:
            op = self.current_token.type_of
            self.match(op)
            t2 = self.t()
            t1 = self.emit(op, t1, t2)
        return t1

    def t(self):
        t1 = self.f()
        while (self.current_token.type_of == tokenizer.TOKEN_OPERATOR_MULTIPLICATION or
                       self.current_token.type_of == tokenizer.TOKEN_OPERATOR_DIVISION):
            op = self.current_token.type_of
            self.match(op)
            t2 = self.f()
            t1 = self.emit(op, t1, t2)
        return t1

    def f(self):
        token_type = self.current_token.type_of
        if token_type == tokenizer.TOKEN_ID:
            symbol = self.find_name_or_error()
            self.match(tokenizer.TOKEN_ID)
            return symbol.data_type
        elif token_type == tokenizer.TOKEN_DATA_TYPE_INT:
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(self.current_token.value_of)
            self.match(tokenizer.TOKEN_DATA_TYPE_INT)
            return tokenizer.TOKEN_DATA_TYPE_INT

    def emit(self, op, t1, t2):
        pass
