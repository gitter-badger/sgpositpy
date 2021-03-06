# MIT License
#
# Copyright (c) 2018 SpeedGo Computing
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from sgposit import coder


"""
Provably correct posit number arithmetic.
"""
class PCPosit:

    def __init__(self, v=None, mode=None, nbits=None, es=None):
        nbits_given = True
        es_given = True
        if nbits is None:
            nbits_given = False
            nbits = 32
        if es is None:
            es_given = False
            es = 2

        if v is None:
            self.rep = coder.create_zero_positrep(nbits=nbits, es=es)
            return
        elif isinstance(v, PCPosit):
            if nbits_given and v.rep['nbits'] != nbits:
                raise NotImplementedError('Mismatched nbits posit conversion is not implemented.')
            if es_given and v.rep['es'] != es:
                raise NotImplementedError('Mismatched es posit conversion is not implemented.')
            self.rep = coder.copy_positrep(v.rep)
            return
        elif mode == 'bits':
            if isinstance(v, int):
                self.rep = coder.decode_posit_binary(v, nbits=nbits, es=es)
                return
            elif isinstance(v, str):
                raise NotImplementedError('Binary bit string posit conversion is not implemented.')

        raise ValueError('Input is not supported.')


    def __add__(self, other):
        if self.rep['t'] == 'z':
            return PCPosit(other)
        elif other.rep['t'] == 'z':
            return PCPosit(self)
        elif self.rep['t'] == 'c' or other.rep['t'] == 'c':
            ret = PCPosit(2**(self.rep['nbits']-1), mode='bits', nbits=self.rep['nbits'], es=self.rep['es'])
            return ret

        assert self.rep['t'] == 'n' and other.rep['t'] == 'n'

        xa = ( -1)**self.rep['s'] * ( 2**self.rep['h'] +  self.rep['f'])
        xb = (-1)**other.rep['s'] * (2**other.rep['h'] + other.rep['f'])
        ma =  2**self.rep['es'] *  self.rep['k'] +  self.rep['e'] -  self.rep['h']
        mb = 2**other.rep['es'] * other.rep['k'] + other.rep['e'] - other.rep['h']

        m = max(ma, mb)
        xc = xa*2**(m-mb) + xb*2**(m-ma)
        mc = ma + mb - m

        pc = PCPosit(self, nbits=self.rep['nbits'], es=self.rep['es'])
        pc.rep = coder.create_positrep(nbits=self.rep['nbits'], es=self.rep['es'])

        if xc == 0:
            pc.rep['t'] = 'z'
            return pc
        elif xc < 0:
            xc = -xc
            pc.rep['s'] = 1

        while xc != 0 and xc % 2 == 0:
            xc >>= 1
            mc += 1

        g = 0
        x = xc
        while x >= 2:
            x >>= 1
            g -= 1

        assert x >= 1 and x < 2, "x={}".format(x)

        pc.rep['e'] = (mc - g) % 2**pc.rep['es']
        pc.rep['k'] = (mc - g) // 2**pc.rep['es']

        pc.rep['h'] = -g
        pc.rep['f'] = xc - 2**pc.rep['h']

        bits = coder.encode_posit_binary(pc.rep)
        pc.rep = coder.decode_posit_binary(bits, nbits=pc.rep['nbits'], es=pc.rep['es'])

        return pc


    def __sub__(self, other):
        p = -PCPosit(other)
        return self + p


    def __neg__(self):
        p = PCPosit(self)
        if p.rep['t'] == 'n':
            p.rep['s'] = p.rep['s'] ^ 1
        return p


    def __mul__(self, other):
        if self.rep['t'] == 'c' or other.rep['t'] == 'c':
            p = PCPosit() # FIXME: Use constructor to directly initialized to posit zero.
            p.rep = coder.create_cinf_positrep(nbits=self.rep['nbits'], es=self.rep['es'])
            return p
        elif self.rep['t'] == 'z' or other.rep['t'] == 'z':
            p = PCPosit() # FIXME
            p.rep = coder.create_zero_positrep(nbits=self.rep['nbits'], es=self.rep['es'])
            return p

        assert self.rep['t'] == 'n' and other.rep['t'] == 'n'

        xa = ( -1)**self.rep['s'] * ( 2**self.rep['h'] +  self.rep['f'])
        xb = (-1)**other.rep['s'] * (2**other.rep['h'] + other.rep['f'])
        ma =  2**self.rep['es'] *  self.rep['k'] +  self.rep['e'] -  self.rep['h']
        mb = 2**other.rep['es'] * other.rep['k'] + other.rep['e'] - other.rep['h']

        xc = xa * xb
        mc = ma + mb

        pc = PCPosit() # FIXME
        pc.rep = coder.create_zero_positrep(nbits=self.rep['nbits'], es=self.rep['es'])
        pc.rep['t'] = 'n'

        if xc < 0:
            xc = -xc
            pc.rep['s'] = 1

        while xc != 0 and xc % 2 == 0:
            xc >>= 1
            mc += 1

        g = 0
        x = xc
        while x >= 2:
            x >>= 1
            g -= 1

        assert x >= 1 and x < 2, "x={}".format(x)

        pc.rep['e'] = (mc - g) % 2**pc.rep['es']
        pc.rep['k'] = (mc - g) // 2**pc.rep['es']

        pc.rep['h'] = -g
        pc.rep['f'] = xc - 2**pc.rep['h']

        bits = coder.encode_posit_binary(pc.rep)
        pc.rep = coder.decode_posit_binary(bits, nbits=pc.rep['nbits'], es=pc.rep['es'])

        return pc


    def __div__(self, other):
        return self.__truediv__(other)


    def __truediv__(self, other):
        if self.rep['t'] == 'c' or other.rep['t'] == 'z':
            p = PCPosit() # FIXME: Use constructor to directly initialized to posit zero.
            p.rep = coder.create_cinf_positrep(nbits=self.rep['nbits'], es=self.rep['es'])
            return p
        elif self.rep['t'] == 'z' or other.rep['t'] == 'c':
            p = PCPosit() # FIXME
            p.rep = coder.create_zero_positrep(nbits=self.rep['nbits'], es=self.rep['es'])
            return p

        assert self.rep['t'] == 'n' and other.rep['t'] == 'n'

        xa = ( -1)**self.rep['s'] * ( 2**self.rep['h'] +  self.rep['f'])
        xb = (-1)**other.rep['s'] * (2**other.rep['h'] + other.rep['f'])
        ma =  2**self.rep['es'] *  self.rep['k'] +  self.rep['e'] -  self.rep['h']
        mb = 2**other.rep['es'] * other.rep['k'] + other.rep['e'] - other.rep['h']

        pc = PCPosit() # FIXME
        pc.rep = coder.create_zero_positrep(nbits=self.rep['nbits'], es=self.rep['es'])
        pc.rep['t'] = 'n'

        if (xa < 0) ^ (xb < 0): pc.rep['s'] = 1
        if xa < 0: xa = -xa
        if xb < 0: xb = -xb

        g = ma - mb + (2**pc.rep['es'])*(pc.rep['nbits']-2) + pc.rep['nbits'] - 1
        g = max(0, g)
        xc = (xa * 2**g) // xb
        mc = ma - mb - g

        if xc != 0:
            while xc != 0 and xc % 2 == 0:
                xc >>= 1
                mc += 1

            g = 0
            x = xc
            while x >= 2:
                x >>= 1
                g -= 1

            assert x >= 1 and x < 2, "x={}".format(x)

            pc.rep['e'] = (mc - g) % 2**pc.rep['es']
            pc.rep['k'] = (mc - g) // 2**pc.rep['es']

            pc.rep['h'] = -g
            pc.rep['f'] = xc - 2**pc.rep['h']

        else:
            pc.rep = coder.create_zero_positrep(nbits=self.rep['nbits'], es=self.rep['es'])

        bits = coder.encode_posit_binary(pc.rep)
        pc.rep = coder.decode_posit_binary(bits, nbits=pc.rep['nbits'], es=pc.rep['es'])

        return pc


    def __floordiv__(self, other):
        raise NotImplementedError


    def __eq__(self, other):
        raise NotImplementedError


    def __ne__(self, other):
        raise NotImplementedError


    def __lt__(self, other):
        raise NotImplementedError


    def __le__(self, other):
        raise NotImplementedError


    def __gt__(self, other):
        raise NotImplementedError


    def __ge__(self, other):
        raise NotImplementedError


    def __str__(self):
        return coder.positrep_to_str(self.rep)
