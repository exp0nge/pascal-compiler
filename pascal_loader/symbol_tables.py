# coding=utf-8


# Notations from: http://www.cs.cornell.edu/courses/cs412/2008sp/lectures/lec12.pdf

VARIABLE = 'var'  # var a;
FUNCTION = 'func'  # (a + 1) == 2
EXPRESSIONS = 'expr'  # a = 1.0;
STATEMENTS = 'stat'  # int pow(int n, int m)
PARAMETER = 'par'


class SymbolObject(object):
    """
    Key for symbol table hashmap
    static int k;
    name: k
    data_type: int
    attribute: static
    kind: var
    """
    def __init__(self, name, data_type, kind, attribute=None, others=None):
        """

        :param name: str
        :param data_type: str
        :param kind: str
        :param attribute: str
        :param others: list
        :return:
        """
        self.name = name
        self.data_type = data_type
        self.kind = kind
        self.attribute = attribute
        if others is None:
            self.others = others
        else:
            self.others = []

    def __unicode__(self):
        return '<%s, %s, %s>' % (self.name, self.data_type, self.kind)
