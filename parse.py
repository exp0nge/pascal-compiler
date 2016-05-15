# coding=utf-8
from pascal_loader import PascalError
import pascal_loader.symbol_tables as symbol_tables
import tokenizer
from constants import OPCODE, CONDITIONALS, byte_packer, byte_unpacker


class Parser(object):
    def __init__(self, token_list):
        self.token_list = iter(token_list)
        self.current_token = None
        self.ip = 0
        self.dp = 0
        self.symbol_table = []
        self.byte_array = bytearray(500)

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
            try:
                self.current_token = self.token_list.next()
            except StopIteration:
                return
        else:
            raise PascalError('Token mismatch, got: %s and current: %s (%i, %i)' % (str(token_type),
                                                                                    str(self.current_token),
                                                                                    self.current_token.row,
                                                                                    self.current_token.column))

    def generate_op_code(self, op_code):
        """
        Appends op_code to byte array then increments IP
        :param op_code: int
        :return:
        """
        self.byte_array[self.ip] = op_code
        self.ip += 1

    def generate_address(self, target):
        """
        Packs target into four bytes and appends to bytearray and increments IP by 4
        :param target: number
        :return:
        """
        for byte in byte_packer(target):
            self.byte_array[self.ip] = byte
            self.ip += 1

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
        return self.byte_array

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
                                                                data_type=data_type,
                                                                dp=self.dp))
            self.dp += 1
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
        self.match('TK_END')
        self.match(tokenizer.TOKEN_DOT)
        self.match(tokenizer.TOKEN_EOF)
        self.generate_op_code(OPCODE.HALT)

    def statements(self):
        while self.current_token.type_of != 'TK_END':
            type_of = self.current_token.type_of
            if type_of == 'TK_WRITELN':
                self.write_line_statement()
            elif type_of == tokenizer.TOKEN_ID:
                self.assignment_statement()
            elif type_of == 'TK_WHILE':
                self.while_statement()
            elif type_of == 'TK_REPEAT':
                self.repeat_statement()
            elif type_of == tokenizer.TOKEN_SEMICOLON:
                self.match(tokenizer.TOKEN_SEMICOLON)
            elif type_of == tokenizer.TOKEN_COMMENT:
                self.match(tokenizer.TOKEN_COMMENT)
            else:
                print 'Statements can\'t match ', type_of
                return

    def find_name_or_error(self):
        symbol = self.find_name_in_symbol_table(self.current_token.value_of)
        if symbol is None:
            raise PascalError('Variable %s is not declared (%i, %i)' % (self.current_token.value_of,
                                                                        self.current_token.row,
                                                                        self.current_token.column))
        else:
            return symbol

    def assignment_statement(self):
        symbol = self.find_name_or_error()
        lhs_type = symbol.data_type
        self.match(tokenizer.TOKEN_ID)
        self.match(tokenizer.TOKEN_OPERATOR_ASSIGNMENT)
        rhs_type = self.e()
        if lhs_type == rhs_type:
            self.generate_op_code(OPCODE.POP)
            self.generate_address(symbol.dp)
        else:
            raise PascalError('Type mismatch %s != %s' % (lhs_type, rhs_type))

    def e(self):
        t1 = self.t()
        while (self.current_token.type_of == tokenizer.TOKEN_OPERATOR_PLUS or
                       self.current_token.type_of == tokenizer.TOKEN_OPERATOR_MINUS):
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

        def generate_pushi_and_address(to_match):
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(self.current_token.value_of)
            self.match(to_match)
            return to_match

        if token_type == tokenizer.TOKEN_ID:
            symbol = self.find_name_or_error()
            self.generate_op_code(OPCODE.PUSH)
            self.generate_address(symbol.dp)
            self.match(tokenizer.TOKEN_ID)
            return symbol.data_type
        elif token_type == 'TK_NOT':
            self.generate_op_code(OPCODE.NOT)
            self.match('TK_NOT')
            return self.f()
        elif token_type == tokenizer.TOKEN_OPERATOR_LEFT_PAREN:
            self.match(tokenizer.TOKEN_OPERATOR_LEFT_PAREN)
            t1 = self.e()
            self.match(tokenizer.TOKEN_OPERATOR_RIGHT_PAREN)
            return t1
        elif token_type == tokenizer.TOKEN_DATA_TYPE_INT:
            return generate_pushi_and_address(tokenizer.TOKEN_DATA_TYPE_INT)
        elif token_type == tokenizer.TOKEN_DATA_TYPE_REAL:
            return generate_pushi_and_address(tokenizer.TOKEN_DATA_TYPE_REAL)
        elif token_type == tokenizer.TOKEN_DATA_TYPE_BOOL:
            return generate_pushi_and_address(tokenizer.TOKEN_DATA_TYPE_BOOL)
        elif token_type == tokenizer.TOKEN_DATA_TYPE_CHAR:
            return generate_pushi_and_address(tokenizer.TOKEN_DATA_TYPE_CHAR)

    def condition(self):
        t1 = self.e()
        value_of = self.current_token.value_of
        if CONDITIONALS.get(value_of) is None:
            raise PascalError("Expected conditional, got: %s" % value_of)
        else:
            type_of = self.current_token.type_of
            self.match(type_of)
            t2 = self.t()
            t1 = self.emit(type_of, t1, t2)
        return t1

    def emit(self, op, t1, t2):
        def boolean(op, t1, t2):
            if t1 == t2:
                self.generate_op_code(op)
            elif t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(op)
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(op)
            else:
                return None
            return tokenizer.TOKEN_DATA_TYPE_BOOL

        if op == tokenizer.TOKEN_OPERATOR_PLUS:
            if t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.ADD)
                return tokenizer.TOKEN_DATA_TYPE_INT
            elif t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(OPCODE.FADD)
                return tokenizer.TOKEN_DATA_TYPE_REAL
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(OPCODE.FADD)
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.FADD)
                return tokenizer.TOKEN_DATA_TYPE_REAL
        elif op == tokenizer.TOKEN_OPERATOR_MINUS:
            if t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.SUB)
                return tokenizer.TOKEN_DATA_TYPE_INT
            elif t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(OPCODE.FSUB)
                return tokenizer.TOKEN_DATA_TYPE_REAL
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(OPCODE.FSUB)
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.FSUB)
                return tokenizer.TOKEN_DATA_TYPE_REAL
        elif op == tokenizer.TOKEN_OPERATOR_DIVISION:
            if (t1 == tokenizer.TOKEN_DATA_TYPE_INT or t1 == tokenizer.TOKEN_DATA_TYPE_REAL) and (
                            t2 == tokenizer.TOKEN_DATA_TYPE_INT or t2 == tokenizer.TOKEN_DATA_TYPE_REAL):
                self.generate_op_code(OPCODE.DIVIDE)
                return tokenizer.TOKEN_DATA_TYPE_REAL
        elif op == 'TK_DIV':
            if t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.DIV)
                return tokenizer.TOKEN_DATA_TYPE_INT
        elif op == tokenizer.TOKEN_OPERATOR_MULTIPLICATION:
            if t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.MULTIPLY)
                return tokenizer.TOKEN_DATA_TYPE_INT
            elif t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(OPCODE.FMULTIPLY)
                return tokenizer.TOKEN_DATA_TYPE_REAL
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(OPCODE.FMULTIPLY)
                return tokenizer.TOKEN_DATA_TYPE_REAL
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.FMULTIPLY)
                return tokenizer.TOKEN_DATA_TYPE_REAL
        elif op == 'TK_OR':
            if t1 == tokenizer.TOKEN_DATA_TYPE_BOOL and t2 == tokenizer.TOKEN_DATA_TYPE_BOOL:
                self.generate_op_code(OPCODE.OR)
                return tokenizer.TOKEN_DATA_TYPE_BOOL
        elif op == tokenizer.TOKEN_OPERATOR_GTE:
            return boolean(OPCODE.GTE, t1, t2)
        elif op == tokenizer.TOKEN_OPERATOR_LTE:
            return boolean(OPCODE.LTE, t1, t2)
        elif op == tokenizer.TOKEN_OPERATOR_EQUALITY:
            return boolean(OPCODE.EQL, t1, t2)
        elif op == tokenizer.TOKEN_OPERATOR_NOT_EQUAL:
            return boolean(OPCODE.NEQ, t1, t2)
        elif op == tokenizer.TOKEN_OPERATOR_LEFT_CHEVRON:
            return boolean(OPCODE.GTR, t1, t2)
        elif op == tokenizer.TOKEN_OPERATOR_RIGHT_CHEVRON:
            return boolean(OPCODE.LES, t1, t2)
        else:
            raise PascalError('Emit failed to match %s' % op)

    def write_line_statement(self):
        self.match('TK_WRITELN')
        self.match(tokenizer.TOKEN_OPERATOR_LEFT_PAREN)
        while True:
            symbol = self.find_name_or_error()
            t1 = self.e()
            if t1 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.PRINT_I)
                self.generate_address(symbol.dp)

            type_of = self.current_token.type_of
            if type_of == tokenizer.TOKEN_OPERATOR_COMMA:
                self.match(tokenizer.TOKEN_OPERATOR_COMMA)
            elif type_of == tokenizer.TOKEN_OPERATOR_RIGHT_PAREN:
                self.match(tokenizer.TOKEN_OPERATOR_RIGHT_PAREN)
                self.generate_op_code(OPCODE.NEW_LINE)
                return
            else:
                raise PascalError('Expected comma or right paren, found: %s' % self.current_token.type_of)

    def repeat_statement(self):
        self.match('TK_REPEAT')
        target = self.ip
        self.statements()
        self.match('TK_UNTIL')
        self.condition()
        self.generate_op_code(OPCODE.JFALSE)
        self.generate_address(target)

    def while_statement(self):
        self.match('TK_WHILE')
        target = self.ip
        self.condition()
        self.match('TK_DO')
        self.generate_op_code(OPCODE.JFALSE)
        hole = self.ip
        self.generate_address(0)
        self.match('TK_BEGIN')
        self.statements()
        self.match('TK_END')
        self.match(tokenizer.TOKEN_SEMICOLON)
        self.generate_op_code(OPCODE.JMP)
        self.generate_address(target)
        save = self.ip
        self.ip = hole
        self.generate_address(save)
        self.ip = save
