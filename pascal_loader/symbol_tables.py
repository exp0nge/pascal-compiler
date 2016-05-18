# coding=utf-8


# Notations from: http://www.cs.cornell.edu/courses/cs412/2008sp/lectures/lec12.pdf

TYPE_VARIABLE = 'var'  # var a;
TYPE_FUNCTION = 'func'  # (a + 1) == 2
TYPE_PROCEDURE = 'pro'
TYPE_EXPRESSIONS = 'expr'  # a = 1.0;
TYPE_STATEMENTS = 'stat'  # int pow(int n, int m)
TYPE_PARAMETER = 'par'


class SymbolObject(object):
    """
    Key for symbol table hashmap
    static int k;
    name: k
    data_type: int
    attribute: static
    kind: var
    """
    def __init__(self, name, type_of_object, data_type, dp=None, attribute=None, others=None):
        """

        :param name: str
        :param type_of_object: str
        :param data_type: str
        :param attribute: str
        :param others: list
        :return:
        """
        self.name = name
        self.type_of_object = type_of_object
        self.data_type = data_type
        self.attribute = attribute
        self.dp = dp
        if others is None:
            self.others = others
        else:
            self.others = []

    def __unicode__(self):
        return '<%s, %s, %i, %s>' % (self.name, self.type_of_object, self.dp, self.data_type)

    def __repr__(self):
        return '<%s, %s, %i, %s>' % (self.name, self.type_of_object, self.dp, self.data_type)

