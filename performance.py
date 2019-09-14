import random
from decimal import Decimal
from prettytable import PrettyTable
import time
import itertools


template = """
def inner(it, timer{init}):
    def empty():
        t0=timer()
        for i in it:
            continue
        t1=timer()
        return t1-t0
    t0 = timer()
    for i in it:
        {stmt}
    t1 = timer()
    return t1 - t0 - empty()
    """


class Timer:
    def __init__(self, expr, globals):
        self.timer = time.perf_counter
        local_ns = {}
        global_ns = globals
        src = template.format(stmt=expr, init="")
        code = compile(src, 'dummy', 'exec')
        exec(code, global_ns, local_ns)
        self.inner = local_ns['inner']

    def numtime(self, number=10 ** 6):
        it = itertools.repeat(None, number)
        timing = self.inner(it, self.timer)
        return timing

    def mintime(self, repeat=5, number=10 ** 6):
        m = 1
        for _ in range(repeat):
            n = self.numtime(number)
            if m > n:
                m = n
        return m / number


def timeit(expr, globals, number):
    return Timer(expr, globals).mintime(number=number)


def expression(x, y, operator, typeval):
    iterations = 0
    if typeval == 'int':
        a = int(x * 100)
        b = int(y * 100)
        iterations = 10 ** 6
    elif typeval == 'float':
        a = x * 100
        b = y * 100
        iterations = 10 ** 5
    elif typeval == 'str':
        iterations = 10 ** 3
        if operator == '+':
            a = str(round(x * 100, 3))
            b = str(round(y * 100, 3))
        elif operator == '*':
            a = str(round(x * 100, 3))
            b = int(y * 100)
    return timeit('a' + operator + 'b', locals(), iterations)


def create_table():
    res = []
    x = random.random()
    y = random.random()
    int_add = 1 / expression(x, y, '+', 'int')
    types = {'int': '+-*/', 'float': '+-*/', 'str': '+*'}
    for typeval in types.keys():
        for operator in types[typeval]:
            if typeval == 'int' and operator == '+':
                current_expr = int_add
            else:
                current_expr = 1 / expression(x, y, operator, typeval)
            percent = round(100 * current_expr / int_add)
            bar = 'X' * round(0.4 * percent)
            res.append([operator, typeval, '%6e' % Decimal(current_expr), bar, str(percent) + '%'])
    return res


random.seed(1234)
pt = PrettyTable()
pt.field_names = ['operator', 'operand type', 'times in one second', 'diagram', 'percent']
pt.align['diagram'] = 'l'
for row in create_table():
    pt.add_row(row)
print(pt)

