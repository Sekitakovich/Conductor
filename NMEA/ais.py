import base64
import numpy as np
import enum


class AISErrorCode(enum.Enum):
    noError = 0
    unknownMessage = 1
    badFormat = 2

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

    ais = "0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVW`abcdefghijklmnopqrstuvw"  # IEC61993-2
    b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"  # base64

    itu = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_ !\"#$%&'()*+,-./0123456789:;<=>?"  # ITU-R M.1371-5

    ''' see https://en.wikipedia.org/wiki/Six-bit_character_code '''

    tableD = str.maketrans(dict(zip(ais, b64)))
    tableE = str.maketrans(dict(zip(b64, ais)))

    def __init__(self):
        self.errorCode = AISErrorCode

    def __ascii6String(self, src):
        n6 = [src[p:p + 6] for p in range(0, len(src), 6)]
        nn = []
        for c in n6:
            nn.append(self.itu[int(c, 2)])

        return ''.join(nn)

    def decode(self, src):
        result = {}
        b64 = src.translate(self.tableD);

        for c in range(len(b64) % 4):  # padding ...
            b64 += '='

        #        print("ais(%s) = [%s](%d) b64(%s) = [%s](%d)" % (type(src), src, len(src), type(b64), b64, len(b64)))

        bits = ''.join([format(b, '08b') for b in np.frombuffer(base64.b64decode(b64), dtype=np.uint8)])  # print(bits)

        thisType = int(bits[0:0 + 6], 2)

        #        print("#### Message %d" % (thisType))

        if thisType in range(1, 27):

            result['error'] = self.errorCode.noError
            header = {
                'type': thisType,
                'repeat': int(bits[6:6 + 2], 2),
                'mmsi': int(bits[8:8 + 30], 2),
                'description': self.description[thisType],
            }
            result['header'] = header

            if thisType in (1, 2, 3):
                body = {'status': int(bits[38:38 + 4], 2), 'turn': int(bits[42:42 + 8], 2),
                        'speed': int(bits[50:50 + 10], 2), 'accuracy': int(bits[60:60 + 1], 2),
                        'lon': int(bits[61:61 + 28], 2), 'lat': int(bits[89:89 + 27], 2),
                        'course': int(bits[116:116 + 12], 2), 'heading': int(bits[128:128 + 9], 2),
                        'second': int(bits[137:137 + 6], 2), 'maneuver': int(bits[143:143 + 2], 2),
                        '(Spare)': int(bits[145:145 + 3], 2), 'raim': int(bits[148:148 + 1], 2),
                        'radioSync': int(bits[149:149 + 2], 2)}

                if thisType in (1, 2):
                    body['slotTimeout'] = int(bits[151:151 + 3], 2)
                    body['subMessage'] = int(bits[154:154 + 14], 2)

                else:
                    body['slotIncrement'] = int(bits[151:151 + 13], 2)
                    body['slots'] = int(bits[164:164 + 3], 2)
                    body['keepFlag'] = int(bits[167:167 + 1], 2)

                result['body'] = body;

            elif thisType in (4, 11):
                body = {
                    'year': int(bits[38:38 + 14], 2),
                    'month': int(bits[52:52 + 4], 2),
                    'day': int(bits[56:56 + 5], 2),
                }
                result['body'] = body;

            elif thisType == 21:
                body = {
                    'aidType': int(bits[38:38 + 5], 2),
                    'name': self.__ascii6String(bits[43:43 + 120]),
                    'accuracy': int(bits[163:163 + 1], 2),
                    'lon': int(bits[164:164 + 28], 2),
                    'lat': int(bits[192:192 + 27], 2),
                    'toBow': int(bits[219:219 + 9], 2),
                    'toStern': int(bits[228:228 + 9], 2),
                    'toPort': int(bits[237:237 + 6], 2),
                    'toStarboard': int(bits[243:243 + 6], 2),
                    'epfd': int(bits[249:249 + 4], 2),
                    'second': int(bits[253:253 + 6], 2),
                    'offPosition': int(bits[259:259 + 1], 2),
                    'regional': int(bits[260:260 + 8], 2),
                    'raim': int(bits[268:268 + 1], 2),
                    'virtualAid': int(bits[269:269 + 1], 2),
                    'assigned': int(bits[270:270 + 1], 2),
                    '(Spare)': int(bits[271:271 + 1], 2),
                    'nameExtension': self.__ascii6String(bits[272:]) if len(bits) > 272 else "",
                }
                result['body'] = body;

        else:
            result['error'] = self.errorCode.unknownMessage
            try:
                result['reason'] = {
                    'type': thisType,
                    'mmsi': int(bits[8:8 + 30], 2),
                }

            except ValueError:
                result['error'] = self.errorCode.badFormat
                print("!!!! ValueError at [%s]" % src)

            except IndexError:
                result['error'] = self.errorCode.badFormat
                print("!!!! IndexError at [%s]" % src)

        return result


if __name__ == '__main__':
    ooo = AISMessageDecoder()

    m21 = "E6<f`I00b7WHP000000000000004CmoF0dNMh000000000"
    print(ooo.decode(m21))

    m1 = "16<f`I0FQT8Wcfd1HtsbS8L00000"
    print(ooo.decode(m1))
