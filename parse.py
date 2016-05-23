# coding=utf-8
from pascal_loader import PascalError
import pascal_loader.symbol_tables as symbol_tables
import tokenizer
from constants import OPCODE, CONDITIONALS, byte_packer, byte_unpacker


class Parser(object):
    def __init__(self, token_list, verbose=False):
        self.token_list = iter(token_list)
        self.current_token = None
        self.ip = 0
        self.dp = 0
        self.symbol_table = []
        self.byte_array = bytearray(5000)
        self.verbose = verbose

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
        # if self.current_token.type_of == tokenizer.TOKEN_COMMENT:
        #     try:
        #         self.current_token = self.token_list.next()
        #     except StopIteration:
        #         return
        if self.current_token.type_of == token_type:
            if self.verbose:
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
        # either we see var or begin or a comment
        if self.current_token.type_of == 'TK_VAR':
            self.variable_declaration()
        elif self.current_token.type_of == 'TK_PROCEDURE':
            while self.current_token.type_of == 'TK_PROCEDURE':
                self.procedure_declaration()
            self.begin()
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
        elif self.current_token.type_of == 'TK_ARRAY':
            self.match('TK_ARRAY')
            data_type = tokenizer.TOKEN_DATA_TYPE_ARRAY
        else:
            raise PascalError('%s data type is invalid (%i, %i)' % (self.current_token.type_of,
                                                                    self.current_token.row,
                                                                    self.current_token.column))
        if data_type == tokenizer.TOKEN_DATA_TYPE_ARRAY:
            # handle array declaration
            self.match(tokenizer.TOKEN_OPERATOR_LEFT_BRACKET)
            extractor = self.extract_ranges(self.current_token)
            self.match(tokenizer.TOKEN_DATA_TYPE_RANGE)
            self.match(tokenizer.TOKEN_OPERATOR_RIGHT_BRACKET)
            self.match('TK_OF')
            if self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_INT:
                self.match(tokenizer.TOKEN_DATA_TYPE_INT)
                assignment_type = tokenizer.TOKEN_DATA_TYPE_INT
            elif self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.match(tokenizer.TOKEN_DATA_TYPE_REAL)
                assignment_type = tokenizer.TOKEN_DATA_TYPE_REAL
            elif self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_CHAR:
                self.match(tokenizer.TOKEN_DATA_TYPE_CHAR)
                assignment_type = tokenizer.TOKEN_DATA_TYPE_CHAR
            elif self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_BOOL:
                self.match(tokenizer.TOKEN_DATA_TYPE_BOOL)
                assignment_type = tokenizer.TOKEN_DATA_TYPE_BOOL
            else:
                raise PascalError('Array of type <%s> is not valid.' % self.current_token.type_of)
            self.match(tokenizer.TOKEN_SEMICOLON)
            attributes = {
                'left': extractor['left'],
                'right': extractor['right'],
                'access_type': extractor['access_type'],
                'assignment_type': assignment_type
            }
            if extractor['access_type'] == tokenizer.TOKEN_DATA_TYPE_INT:
                for variable in declarations:
                    self.symbol_table.append(symbol_tables.SymbolObject(name=variable,
                                                                        type_of_object=symbol_tables.TYPE_ARRAY,
                                                                        data_type=tokenizer.TOKEN_DATA_TYPE_ARRAY,
                                                                        dp=self.dp,
                                                                        attribute=attributes))
                    self.dp += 4 * int(extractor['right']) - int(extractor['left'])
            elif extractor['access_type'] == tokenizer.TOKEN_DATA_TYPE_CHAR:
                pass
            else:
                raise PascalError('Array access type of %s is not allowed.' % extractor['access_type'])

        else:
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
        elif self.current_token.type_of == 'TK_PROCEDURE':
            self.procedure_declaration()
        else:
            # no more declarations; begins main procedure
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
        """
        E -> T | E + T | E - T
        T -> F | T * F | T/F
        T -> id | lit | +F | -F | €
        F -> ( E ) | +F | -F | not F | lit | id //lit: return type based on the constant, id: type from symbol table
        :return:
        """
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
            elif type_of == 'TK_IF':
                self.if_statement()
            elif type_of == 'TK_FOR':
                self.for_statement()
            elif type_of == 'TK_CASE':
                self.case_statement()
            elif type_of == tokenizer.TOKEN_SEMICOLON:
                self.match(tokenizer.TOKEN_SEMICOLON)
            elif type_of == tokenizer.TOKEN_COMMENT:
                self.match(tokenizer.TOKEN_COMMENT)
            else:
                if self.verbose:
                    print 'Parser: statements() can\'t match ', self.current_token
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
        if self.current_token.type_of == tokenizer.TOKEN_OPERATOR_LEFT_BRACKET:
            self.array_assignment(symbol)
            return
        self.match(tokenizer.TOKEN_OPERATOR_ASSIGNMENT)
        rhs_type = self.e()
        if rhs_type == tokenizer.TOKEN_CHARACTER:
            self.generate_op_code(OPCODE.POP_CHAR)
            self.generate_address(symbol.dp)
        elif lhs_type == tokenizer.TOKEN_DATA_TYPE_REAL and rhs_type == tokenizer.TOKEN_REAL_LIT:
            self.generate_op_code(OPCODE.POP_REAL_LIT)
            self.generate_address(symbol.dp)
        elif lhs_type == rhs_type:
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
                       self.current_token.type_of == tokenizer.TOKEN_OPERATOR_DIVISION or
                       self.current_token.type_of == 'TK_DIV'):
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
            if symbol.type_of_object == symbol_tables.TYPE_VARIABLE:
                self.generate_op_code(OPCODE.PUSH)
                self.generate_address(symbol.dp)
                self.match(tokenizer.TOKEN_ID)
                return symbol.data_type
            elif symbol.type_of_object == symbol_tables.TYPE_ARRAY:
                self.match(tokenizer.TOKEN_ID)
                self.access_array(symbol)
                self.generate_op_code(OPCODE.RETRIEVE)
                # return tokenizer.TOKEN_DATA_TYPE_ARRAY
                return symbol.assignment_type
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
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(self.current_token.value_of)
            self.match(tokenizer.TOKEN_DATA_TYPE_REAL)
            return tokenizer.TOKEN_DATA_TYPE_REAL
        elif token_type == tokenizer.TOKEN_REAL_LIT:
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(self.current_token.value_of)
            self.match(tokenizer.TOKEN_REAL_LIT)
            return tokenizer.TOKEN_REAL_LIT
        elif token_type == tokenizer.TOKEN_DATA_TYPE_BOOL:
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(self.current_token.value_of)
            self.match(tokenizer.TOKEN_DATA_TYPE_BOOL)
            return tokenizer.TOKEN_DATA_TYPE_BOOL
        elif token_type == tokenizer.TOKEN_DATA_TYPE_CHAR:
            return generate_pushi_and_address(tokenizer.TOKEN_DATA_TYPE_CHAR)
        elif token_type == tokenizer.TOKEN_CHARACTER:
            self.generate_op_code(OPCODE.PUSH_CHAR)
            self.generate_address(ord(self.current_token.value_of))
            self.match(tokenizer.TOKEN_CHARACTER)
            return tokenizer.TOKEN_CHARACTER
        elif token_type == 'TK_TRUE':
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(1)
            self.match('TK_TRUE')
            return tokenizer.TOKEN_DATA_TYPE_BOOL
        elif token_type == 'TK_FALSE':
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(0)
            self.match('TK_FALSE')
            return tokenizer.TOKEN_DATA_TYPE_BOOL
        else:
            raise PascalError('f() does not support %s, %s' % (self.current_token.value_of, token_type))

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
        """
        Based on lookup tables.
        +	I	R	B	C
            /I	/R	X	X

        -	I	    R	    B	C
            Neg/I	Fneg/R	X	X

        Not	I	            R	B	    C
            Bitwisenot/I	X	Not/B	X

        +	I	        R	                        B	C
        I	Add/I	    Xchg, cvr, xchg, fadd/R	    X	X
        R	CVR fadd/R	Add/R	X	X
        B	X	        X	                        X	X
        C	X	        X	                        X	X

        /	I	R
        I	/R	/R
        R	/R	/R

        Div	I
        I	/I

        Or	I	        B
        I	X or or/I	X
        B	X	        Or/B

        =	I	    R	B	C
        I	Eql/B		X	X
        R		Eql/B	X	X
        B	X	X	Eql/B	X
        C	X	X	X	Eql/B

        Abs	I	R	B	C
                    X	X


        :param op: OPCODE
        :param t1: data_type
        :param t2: data_type
        :return: data_type or None
        """

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
            elif t1 == 'TK_CHAR' and t2 == tokenizer.TOKEN_CHARACTER:
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
                return tokenizer.TOKEN_DATA_TYPE_REAL
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.FADD)
                return tokenizer.TOKEN_DATA_TYPE_REAL
            else:
                raise PascalError('Unable to match operation + with types: ' + t1 + ' and ' + t2)
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
                return tokenizer.TOKEN_DATA_TYPE_REAL
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.FSUB)
                return tokenizer.TOKEN_DATA_TYPE_REAL
            else:
                raise PascalError('Unable to match operation - with types: ' + t1 + ' and ' + t2)
        elif op == tokenizer.TOKEN_OPERATOR_DIVISION:
            if t1 == t2:
                if t1 == tokenizer.TOKEN_DATA_TYPE_INT:
                    self.generate_op_code(OPCODE.DIVIDE)
                elif t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                    self.generate_op_code(OPCODE.FDIVIDE)
                return t1
            elif t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_REAL:
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(OPCODE.XCHG)
                self.generate_op_code(OPCODE.DIVIDE)
                return tokenizer.TOKEN_DATA_TYPE_REAL
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.CVR)
                self.generate_op_code(OPCODE.DIVIDE)
                return tokenizer.TOKEN_DATA_TYPE_REAL
            elif t1 == tokenizer.TOKEN_DATA_TYPE_REAL and t2 == tokenizer.TOKEN_REAL_LIT:
                self.generate_op_code(OPCODE.FDIVIDE)
                return t1
            else:
                raise PascalError('Unable to match operation / with types: ' + t1 + ' and ' + t2)
        elif op == 'TK_DIV':
            if t1 == tokenizer.TOKEN_DATA_TYPE_INT and t2 == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.DIV)
                return tokenizer.TOKEN_DATA_TYPE_INT
            else:
                raise PascalError('Unable to match operation div with types: ' + t1 + ' and ' + t2)
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
            else:
                raise PascalError('Unable to match operation * with types: ' + t1 + ' and ' + t2)
        elif op == 'TK_OR':
            if t1 == tokenizer.TOKEN_DATA_TYPE_BOOL and t2 == tokenizer.TOKEN_DATA_TYPE_BOOL:
                self.generate_op_code(OPCODE.OR)
                return tokenizer.TOKEN_DATA_TYPE_BOOL
            else:
                raise PascalError('Unable to match operation or with types: ' + t1 + ' and ' + t2)
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
            if self.current_token.type_of == tokenizer.TOKEN_ID:
                symbol = self.find_name_or_error()
                if hasattr(symbol, 'assignment_type'):
                    self.match(tokenizer.TOKEN_ID)
                    self.access_array(symbol)
                    self.generate_op_code(OPCODE.RET_AND_PRINT)
                    continue
                else:
                    expression = self.e()
                if expression == tokenizer.TOKEN_DATA_TYPE_INT:
                    self.generate_op_code(OPCODE.PRINT_I)
                    self.generate_address(symbol.dp)
                elif expression == tokenizer.TOKEN_DATA_TYPE_CHAR:
                    self.generate_op_code(OPCODE.PRINT_C)
                    self.generate_address(symbol.dp)
                elif expression == tokenizer.TOKEN_DATA_TYPE_REAL:
                    self.generate_op_code(OPCODE.PRINT_R)
                    self.generate_address(symbol.dp)
                elif expression == tokenizer.TOKEN_DATA_TYPE_BOOL:
                    self.generate_op_code(OPCODE.PRINT_B)
                    self.generate_address(symbol.dp)
                elif expression == tokenizer.TOKEN_DATA_TYPE_ARRAY:
                    self.generate_op_code(OPCODE.RETRIEVE)
                else:
                    raise PascalError('writeln does not support ' + str(symbol))
            if self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_INT:
                self.generate_op_code(OPCODE.PRINT_ILIT)
                self.generate_address(int(self.current_token.value_of))
                self.match(tokenizer.TOKEN_DATA_TYPE_INT)
            elif self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_CHAR:
                self.generate_op_code(OPCODE.PRINT_C)
                self.generate_address(self.current_token.value_of)
                self.match(tokenizer.TOKEN_CHARACTER)
            elif self.current_token.type_of == tokenizer.TOKEN_STRING_LIT:
                self.generate_op_code(OPCODE.PUSHI)
                s = self.current_token.value_of
                s = s[1:-1]  # chop first and last quotes
                self.generate_address(len(s))
                self.generate_op_code(OPCODE.PRINT_STR_LIT)
                for byte in bytearray(s):
                    self.byte_array[self.ip] = byte
                    self.ip += 1
                self.match(tokenizer.TOKEN_STRING_LIT)

            # else:
            #     raise PascalError('writeln does not support %s', self.current_token.value_of)
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
        """
        <repeat-stat> -> repeat <statements>
        Until <cond>
        :return:
        """
        self.match('TK_REPEAT')
        target = self.ip
        self.statements()
        self.match('TK_UNTIL')
        self.condition()
        self.generate_op_code(OPCODE.JFALSE)
        self.generate_address(target)

    def while_statement(self):
        """
        While <cond> do <stat>;
        :return:
        """
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

    def if_statement(self):
        """
        If <cond> then <stat>
        If <cond> then <stat> else <stat>
        :return:
        """
        self.match('TK_IF')
        self.condition()
        self.match('TK_THEN')
        self.generate_op_code(OPCODE.JFALSE)
        hole = self.ip
        self.generate_address(0)
        self.statements()
        if self.current_token.type_of == 'TK_ELSE':
            self.generate_op_code(OPCODE.JMP)
            hole_2 = self.ip
            self.generate_address(0)
            save = self.ip
            self.ip = hole
            self.generate_address(save)
            self.ip = save
            hole = hole_2
            self.match('TK_ELSE')
            self.statements()
        save = self.ip
        self.ip = hole
        self.generate_address(save)
        self.ip = save

    def for_statement(self):
        self.match('TK_FOR')
        value_of = self.current_token.value_of
        self.assignment_statement()
        target = self.ip
        symbol = self.find_name_in_symbol_table(value_of)

        self.match('TK_TO')
        self.generate_op_code(OPCODE.PUSH)
        self.generate_address(symbol.dp)
        self.generate_op_code(OPCODE.PUSHI)
        self.generate_address(self.current_token.value_of)
        self.generate_op_code(OPCODE.LTE)
        self.match(tokenizer.TOKEN_DATA_TYPE_INT)
        self.match('TK_DO')
        self.generate_op_code(OPCODE.JFALSE)
        hole = self.ip
        self.generate_address(0)

        self.match('TK_BEGIN')
        self.statements()
        self.match('TK_END')
        self.match(tokenizer.TOKEN_SEMICOLON)

        self.generate_op_code(OPCODE.PUSH)
        self.generate_address(symbol.dp)
        self.generate_op_code(OPCODE.PUSHI)
        self.generate_address(1)
        self.generate_op_code(OPCODE.ADD)
        self.generate_op_code(OPCODE.POP)
        self.generate_address(symbol.dp)
        self.generate_op_code(OPCODE.JMP)
        self.generate_address(target)
        save = self.ip
        self.ip = hole
        self.generate_address(save)
        self.ip = save

    def case_statement(self):
        """
        Case E of
            [<tags> : <statement>] +
                else <statement>
            end

        <tags>	<single tag>	    10:
                <range>	            3..9:
                <list>	            3,5,6
                <list of ranges>	1..20, 30..40:
        :return:
        """
        self.match('TK_CASE')
        self.match(tokenizer.TOKEN_OPERATOR_LEFT_PAREN)
        checker = self.current_token
        e1 = self.e()
        if e1 == tokenizer.TOKEN_DATA_TYPE_REAL:
            raise PascalError('Real type not allowed for case: ' + e1)
        self.match(tokenizer.TOKEN_OPERATOR_RIGHT_PAREN)
        self.match('TK_OF')
        hole_list = []
        while (self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_INT or
                       self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_CHAR or
                       self.current_token.type_of == tokenizer.TOKEN_CHARACTER or
                       self.current_token.type_of == tokenizer.TOKEN_DATA_TYPE_BOOL):
            e2 = self.e()
            self.emit(tokenizer.TOKEN_OPERATOR_EQUALITY, e1, e2)
            self.match(tokenizer.TOKEN_OPERATOR_COLON)

            self.generate_op_code(OPCODE.JFALSE)
            hole = self.ip
            self.generate_address(0)
            self.statements()

            self.generate_op_code(OPCODE.JMP)
            hole_list.append(self.ip)
            self.generate_address(0)

            save = self.ip
            self.ip = hole
            self.generate_address(save)
            self.ip = save
            if self.current_token.type_of != 'TK_END':
                symbol = self.find_name_in_symbol_table(checker.value_of)
                if symbol is not None:
                    self.generate_op_code(OPCODE.PUSH)
                    self.generate_address(symbol.dp)

        self.match('TK_END')
        self.match(tokenizer.TOKEN_SEMICOLON)
        save = self.ip
        for hole in hole_list:
            self.ip = hole
            self.generate_address(save)
        self.ip = save

    def extract_ranges(self, token):
        """

        :param token: Token
        :return:
        """
        payload = {}
        split = token.value_of.split('..')
        if len(split) != 2:
            raise PascalError('Unexpected range for array, expected in form of 0..2, got ' + self.current_token)
        left, right = split[0], split[1]
        # figure out data type
        if left.isalpha():
            if right.isalpha():
                payload['access_type'] = tokenizer.TOKEN_DATA_TYPE_CHAR
            else:
                raise PascalError('Array range mismatch, %s %s' % (left, right))
        else:
            # check for float/int
            if left.__contains__('.'):
                if right.__contains__('.'):
                    left, right = float(left), float(right)
                    payload['data_type'] = tokenizer.TOKEN_DATA_TYPE_REAL
                else:
                    raise PascalError('Array range mismatch, %s %s' % (left, right))
            else:
                # assume int
                left, right = int(left), int(right)
                payload['access_type'] = tokenizer.TOKEN_DATA_TYPE_INT
        payload['left'], payload['right'], payload['token'] = left, right, token
        return payload

    def access_array(self, symbol):
        self.match(tokenizer.TOKEN_OPERATOR_LEFT_BRACKET)
        curr_symbol = self.find_name_or_error()
        self.generate_op_code(OPCODE.PUSH)
        self.generate_address(curr_symbol.dp)
        self.match(tokenizer.TOKEN_ID)
        self.match(tokenizer.TOKEN_OPERATOR_RIGHT_BRACKET)

        self.generate_op_code(OPCODE.PUSHI)

        if curr_symbol.data_type == tokenizer.TOKEN_DATA_TYPE_INT:
            self.generate_address(symbol.left)  # gives me the array in reverse
            self.generate_op_code(OPCODE.XCHG)
            self.generate_op_code(OPCODE.SUB)
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(4)
            self.generate_op_code(OPCODE.MULTIPLY)
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(symbol.dp)
            self.generate_op_code(OPCODE.ADD)
        elif curr_symbol.data_type == tokenizer.TOKEN_DATA_TYPE_CHAR:
            self.generate_address(symbol.left)
            self.generate_op_code(OPCODE.XCHG)
            self.generate_op_code(OPCODE.SUB)
            self.generate_op_code(OPCODE.PUSHI)
            self.generate_address(symbol.dp)
            self.generate_op_code(OPCODE.ADD)
        else:
            raise Parser('Array access with type %s not supported.' % curr_symbol.data_type)

    def array_assignment(self, symbol):
        self.access_array(symbol)
        self.match(tokenizer.TOKEN_OPERATOR_ASSIGNMENT)
        e1 = self.e()
        if e1 == symbol.assignment_type:
            self.generate_op_code(OPCODE.DUMP)
        else:
            raise PascalError('Array assignment type mismatch with ' + e1 + ' and ' + symbol.assignment_type)

    def procedure_declaration(self):
        self.match('TK_PROCEDURE')
        procedure = self.current_token
        self.match(tokenizer.TOKEN_ID)
        self.match(tokenizer.TOKEN_SEMICOLON)

        self.generate_op_code(OPCODE.JMP)
        hole = self.ip
        self.generate_address(0)

        symbol = symbol_tables.SymbolObject(name=procedure.value_of,
                                            type_of_object='TK_PROCEDURE',
                                            data_type=symbol_tables.TYPE_PROCEDURE,
                                            dp=self.dp,
                                            attribute={
                                                'ip': self.ip,
                                                'ret': -1
                                            })

        self.match('TK_BEGIN')
        self.statements()
        self.match('TK_END')
        self.match(tokenizer.TOKEN_SEMICOLON)

        self.generate_op_code(OPCODE.JMP)
        symbol.ret = self.ip
        self.generate_address(0)

        self.symbol_table.append(symbol)
        self.dp += 1

        save = self.ip
        self.ip = hole
        self.generate_address(save)
        self.ip = save
