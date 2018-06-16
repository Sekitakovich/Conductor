import base64
import numpy as np

class AISMessageDecoder:
    description = [
        "",
        "Position Report Class A",
        "Position Report Class A (Assigned schedule)",
        "Position Report Class A (Response to interrogation)",
        "Base Station Report",
        "Static and Voyage Related Data",
        "Binary Addressed Message",
        "Binary Acknowledge",
        "Binary Broadcast Message",
        "Standard SAR Aircraft Position Report",
        "UTC and Date Inquiry",
        "UTC and Date Response",
        "Addressed Safety Related Message",
        "Safety Related Acknowledgement",
        "Safety Related Broadcast Message",
        "Interrogation",
        "Assignment Mode Command",
        "DGNSS Binary Broadcast Message",
        "Standard Class B CS Position Report",
        "Extended Class B Equipment Position Report",
        "Data Link Management",
        "Aid-to-Navigation Report",
        "Channel Management",
        "Group Assignment Command",
        "Static Data Report",
        "Single Slot Binary Message",
        "Multiple Slot Binary Message With Communications State",
        "Position Report For Long-Range Applications",
    ]
    ''' see https://en.wikipedia.org/wiki/Six-bit_character_code '''


    ais = "0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVW`abcdefghijklmnopqrstuvw"
    b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    ascii6 = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_ !\"#$%&'()*+,-./0123456789:;<=>?"

    tableD = str.maketrans(dict(zip(ais, b64)))
    tableE = str.maketrans(dict(zip(b64, ais)))

    #    def __init__(self):

    def __ascii6String(self, src):
        n6 = [src[p:p + 6] for p in range(0, len(src), 6)]
        nn = []
        for c in n6:
            nn.append(self.ascii6[int(c, 2)])

        return ''.join(nn)

    def decode(self, src):
        result = {}
        b64 = src.translate(self.tableD);

        for c in range(len(b64) % 4):  # padding ...
            b64 += '='

#        print("ais(%s) = [%s](%d) b64(%s) = [%s](%d)" % (type(src), src, len(src), type(b64), b64, len(b64)))

        bin = np.frombuffer(base64.b64decode(b64), dtype=np.uint8)

        bits = ''.join([format(b, '08b') for b in bin])  # print(bits)

        thisType = int(bits[0:5 + 1], 2)

        header = {'type': thisType, 'repeat': int(bits[6:7 + 1], 2), 'MMSI': int(bits[8:37 + 1], 2), 'desc': self.description[thisType]}
        result['header'] = header

        if thisType == 21:
            body = {
                'aid-type': int(bits[38:42 + 1], 2),
                'name': self.__ascii6String(bits[43:162 + 1]),
                'accuracy': int(bits[163:163 + 1], 2),
                'lon': int(bits[164:191 + 1], 2),
                'lat': int(bits[192:218 + 1], 2),
                'to-bow': int(bits[219:227+1], 2),
                'to-stern': int(bits[228:236 + 1], 2),
                'to-port': int(bits[237:242 + 1], 2),
                'to-starboard': int(bits[243:248 + 1], 2),
                'epfd': int(bits[249:252 + 1], 2),
                'second': int(bits[253:258 + 1], 2),
                'off-position': int(bits[259:259 + 1], 2),
                'regional': int(bits[260:267 + 1], 2),
                'raim': int(bits[268:268 + 1], 2),
                'virtual-aid': int(bits[268:268 + 1], 2),
                'assigned': int(bits[268:268 + 1], 2),
                '(Spare)': int(bits[271:271 + 1], 2),
#                '(Name Extension)': int(bits[272:360 + 1], 2),
            }
            result['body'] = body;

        print(result)


if __name__ == '__main__':
    ooo = AISMessageDecoder()
    m21 = "E6<f`I00b7WHP000000000000004CmoF0dNMh000000000"
    ooo.decode(m21)
