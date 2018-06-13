import base64
import numpy as np

class AISDecoder:

    ''' see https://en.wikipedia.org/wiki/Six-bit_character_code '''

    def __init__(self):
        itu = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_ !\"#$%&'()*+,-./0123456789:;<=>?"
        b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

        self.tableD = str.maketrans(dict(zip(itu, b64))); # print(self.tableD)
        self.tableE = str.maketrans(dict(zip(b64, itu)))

    def decode(self, src):
        b64 = bytes(src.translate(self.tableD), encoding='utf-8')
        print("itu = [%s] b64(%s) = [%s]" % (src, type(b64), b64))
        bin = np.frombuffer(base64.b64decode(b64), dtype=np.uint8)

        offset = 0
        bits = []
        for d in bin:
            print("%d %02x (%s)" % (offset, d, format(d, '08b')))
            bits.append(format(d, '08b'))
            offset += 1

        print(''.join(bits))

if __name__ == '__main__':

    ooo = AISDecoder()

    src = "377gg:002?aw@0ND29GR=AT<21r1"
    ooo.decode(src)