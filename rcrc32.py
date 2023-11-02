#!/usr/bin/env python3
import os
import sys
import string 
import itertools

table = []
table_reverse = []
permitted_characters = set(
    map(ord, string.ascii_letters + string.digits + '_')) 

class Matrix:
    def __init__(self, matrix):
        # column vectors
        self.matrix = matrix

    @staticmethod
    def identity():
        return Matrix(tuple(1 << i for i in range(32)))

    @staticmethod
    def zero_operator(poly):
        m = [poly]
        n = 1
        for _ in range(31):
            m.append(n)
            n <<= 1
        return Matrix(tuple(m))

    def multiply_vector(self, v, s = 0):
        for c in self.matrix:
            s ^= c & -(v & 1)
            v >>= 1
            if not v:
                break
        return s

    def mul(self, matrix):
        return Matrix(tuple(map(self.multiply_vector, matrix.matrix)))

def reciprocal(poly):
    ''' Return the reciprocal polynomial of a reversed (lsbit-first) polynomial. '''
    return poly << 1 & 0xffffffff | 1

def init_tables(poly = 0xEDB88320 , reverse=True):
    global table, table_reverse
    table = []
    # build CRC32 table
    for i in range(256):
        for j in range(8):
            i = (i >> 1) ^ (poly & -(i & 1))
        table.append(i)
    # build reverse table
    if reverse:
        table_reverse = []
        for i in range(256):
            found = []
            for j in range(256):
                if table[j] >> 24 == i:
                    found.append(j)
            table_reverse.append(tuple(found))


def calc(data, accum=0):
    if not all(map(lambda x : x in permitted_characters  , data )) : 
        raise ValueError("Invalid data - use only permitted_characters chars " ) 
    accum = ~accum
    for b in data:
        accum = table[(accum ^ b) & 0xFF] ^ ((accum >> 8) & 0x00FFFFFF)
    accum = ~accum
    return accum & 0xFFFFFFFF

def rewind(data ,accum = 0 ):
    if not data:
        return (accum,)
    stack = [(len(data), ~accum)]
    solutions = set()
    while stack:
        node = stack.pop()
        prev_offset = node[0] - 1
        for i in table_reverse[(node[1] >> 24) & 0xFF]:
            prevCRC = (((node[1] ^ table[i]) << 8) |
                       (i ^ data[prev_offset])) & 0xFFFFFFFF
            if prev_offset:
                stack.append((prev_offset, prevCRC))
            else:
                solutions.add((~prevCRC) & 0xFFFFFFFF)
    return solutions


def findReverse(desired, accum = 0 ):
    solutions = set()
    accum = ~accum
    stack = [(~desired,)]
    while stack:
        node = stack.pop()
        for j in table_reverse[(node[0] >> 24) & 0xFF]:
            if len(node) == 4:
                a = accum
                data = []
                node = node[1:] + (j,)
                for i in range(3, -1, -1):
                    data.append((a ^ node[i]) & 0xFF)
                    a >>= 8
                    a ^= table[node[i]]
                solutions.add(tuple(data))
            else:
                stack.append(((node[0] ^ table[j]) << 8,) + node[1:] + (j,))
    return list(map(bytearray , solutions)) 

def combine(c1, c2, l2, n, poly):
    m = Matrix.zero_operator(poly)
    m = m.mul(m)
    m = m.mul(m)
    M = Matrix.identity()
    while l2:
        m = m.mul(m)
        if l2 & 1:
            M = m.mul(M)
        l2 >>= 1
    b = c2
    while True:
        if n & 1:
            c1 = M.multiply_vector(c1, b)

        n >>= 1
        if not n:
            break

        b = M.multiply_vector(b, b)
        M = M.mul(M)

    return c1