#!/usr/bin/env python

"""
Python snippet for bithacks [1] problem in order to compute without branching. It
means without using any carry flags and jump instructions. In python bytecode it
means without COMPARE_OP [2] opcode instruction defined in opcode.py in L.144
def_op('COMPARE_OP', 107)

[1] https://graphics.stanford.edu/~seander/bithacks.html
[2] http://hg.python.org/cpython/file/659c1ce8ed2f/Include/opcode.h#l93
"""

import unittest
import random
import sys
import timeit

CHAR_BIT = 8
try:
    from ctypes import c_int, sizeof
    SIZEOF_INT = sizeof(c_int)
    # remove c_int from globals()
    del c_int
except:
    import struct
    SIZEOF_INT = struct.calcsize("i")

def signof_int(v):
    return (v >> SIZEOF_INT * CHAR_BIT - 1)

def abs_int(v):
    mask = (v >> SIZEOF_INT * CHAR_BIT - 1)
    return (v + mask) ^ mask

def min_int(x, y):
    return y + ((x - y) & ((x - y) >> (SIZEOF_INT * CHAR_BIT - 1)))

def max_int(x, y):
    return x - ((x - y) & ((x - y) >> (SIZEOF_INT * CHAR_BIT - 1)))

def powerof2_int(x):
    return x and not (x & (x - 1))

def negate_int(v):
    return (v ^ -1) + 1

def nb_bits_int(v):
    nb_bits = 0
    for i in range(0, 32):
        nb_bits &= i - 1

    return nb_bits


class BitHacksTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_1_signof_int(self):
        self.assertEqual(signof_int(-42), -1)
        self.assertEqual(signof_int(13), 0)

    def test_2_abs_int(self):
        self.assertEqual(abs_int(-42), abs(-42))
        self.assertEqual(abs_int(13), abs(13))

    def test_3_max_int(self):
        self.assertEqual(max_int(-20, 20), 20)
        self.assertEqual(max_int(20, 0), 20)

    def test_4_min_int(self):
        self.assertEqual(min_int(-20, 20), -20)
        self.assertEqual(min_int(-20, -10), -20)

    def test_5_hascomp_opcode(self):
        self.assertTrue(hascomp_opcode(eval("lambda x: x>0").__code__))
        self.assertFalse(hascomp_opcode(eval("lambda x: x*0").__code__))

        for func in sorted([f for f in globals() if f.endswith('_int')]):
            self.assertFalse(hascomp_opcode(get_code(func)))

    def test_6_powerof2_int(self):
        for x in [2, 4, 8, 16, 32, 64, 128, 256, 512]:
            self.assertTrue(powerof2_int(x))

    def test_7_negate_int(self):
        for x in range(-10, 0):
            self.assertTrue(negate_int(x), x * -1)

def t():
    for i in range(0, 9):
        r = random.randint(-1000, 1000)
        s = ("unsigned", "signed")[signof_int(r)]
        print("i=%d r=%d s=%s" % (i, r, s))

def bench_it(func_str, param_str, number=10000):
    t = timeit.timeit("{0}{1}".format(func_str, param_str), number=10000)
    sys.stdout.write("builtin {0:>14} {1:.16f}".format(func_str, t))
    sys.stdout.write("\n")
    t = timeit.timeit("{0}{1}".format(func_str, param_str), number=10000)
    sys.stdout.write("without branch {0:>7} {1:.16f}".format(func_str, t))
    sys.stdout.write("\n")

def bench():
    funcs = ['abs_int', 'min_int', 'max_int']

    # register _int functions in builtins, it's required to use timeit.timeit()
    for func in funcs:
        setattr(globals()['__builtins__'], func, globals()[func])

    bench_it("abs", "(-42)")
    bench_it("abs_int", "(-42)")

    for func in ['min_int', 'max_int']:
        bench_it(func, "(-42, 10)")
        bench_it(func[0:func.find('_')], "(-42, 10)")

def get_code(func):
    code_attr = ('func_code', '__code__')[sys.version_info.major==3]
    return getattr(globals()[func], code_attr)

def hascomp_opcode(co):
    from opcode import opmap
    co_code = co.co_code
    co_len = len(co_code)
    i = 0
    while i < co_len:
        c = co_code[i]
        if sys.version_info.major==3:
            op = c
        else:
            op = ord(c)
        if op == opmap['COMPARE_OP']:
            return True
        i += 1

    return False

def dis():
    import dis
    funcs = sorted([f for f in globals() if f.endswith('_int')])
    co = get_code('max_int')
    for f in funcs:
        print("dis func {0}:\n".format(f))
        dis.disassemble(get_code(f))

if __name__ == '__main__':
    t()
    bench()
    dis()
    unittest.main()
