"""
This code is public domain. Everyone has the right to do whatever they want
with it for any purpose.

In case your jurisdiction does not consider the above disclaimer valid or 
enforceable, here's an MIT license for you:

The MIT License (MIT)

Copyright (c) 2013 Vitalik Buterin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


class JacobianCurve:
    def __init__(self, p, n, a, b, g):
        self.p = p
        self.n = n
        self.a = a
        self.b = b
        self.g = g


    def inv(self, a, n):
        if a == 0:
            return 0
        lm, hm = 1, 0
        low, high = a % n, n
        while low > 1:
            r = high // low
            nm, new = hm - lm * r, high - low * r
            lm, low, hm, high = nm, new, lm, low
        return lm % n


    def isinf(self, p):
        return p[0] == 0 and p[1] == 0


    def to_jacobian(self, p):
        return p[0], p[1], 1


    def jacobian_double(self, p):
        if not p[1]:
            return 0, 0, 0
        ysq = (p[1] ** 2) % self.p
        s = (4 * p[0] * ysq) % self.p
        m = (3 * p[0] ** 2 + self.a * p[2] ** 4) % self.p
        nx = (m ** 2 - 2 * s) % self.p
        ny = (m * (s - nx) - 8 * ysq ** 2) % self.p
        nz = (2 * p[1] * p[2]) % self.p
        return nx, ny, nz


    def jacobian_add(self, p, q):
        if not p[1]:
            return q
        if not q[1]:
            return p
        u1 = (p[0] * q[2] ** 2) % self.p
        u2 = (q[0] * p[2] ** 2) % self.p
        s1 = (p[1] * q[2] ** 3) % self.p
        s2 = (q[1] * p[2] ** 3) % self.p
        if u1 == u2:
            if s1 != s2:
                return (0, 0, 1)
            return self.jacobian_double(p)
        h = u2 - u1
        r = s2 - s1
        h2 = (h * h) % self.p
        h3 = (h * h2) % self.p
        u1h2 = (u1 * h2) % self.p
        nx = (r ** 2 - h3 - 2 * u1h2) % self.p
        ny = (r * (u1h2 - nx) - s1 * h3) % self.p
        nz = (h * p[2] * q[2]) % self.p
        return (nx, ny, nz)


    def from_jacobian(self, p):
        z = self.inv(p[2], self.p)
        return (p[0] * z ** 2) % self.p, (p[1] * z ** 3) % self.p


    def jacobian_multiply(self, a, n):
        if a[1] == 0 or n == 0:
            return 0, 0, 1
        if n == 1:
            return a
        if n < 0 or n >= self.n:
            return self.jacobian_multiply(a, n % self.n)
        half = self.jacobian_multiply(a, n // 2)
        half_sq = self.jacobian_double(half)
        if n % 2 == 0:
            return half_sq
        if n % 2 == 1:
            return self.jacobian_add(half_sq, a)


    def fast_multiply(self, a, n):
        return self.from_jacobian(self.jacobian_multiply(self.to_jacobian(a), n))


    def fast_add(self, a, b):
        return self.from_jacobian(self.jacobian_add(self.to_jacobian(a), self.to_jacobian(b)))
