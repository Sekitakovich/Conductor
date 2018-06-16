import numpy as np
import enum
from datetime import datetime as dt


class MC450Analyzer:
    ''' functions for 450/NMEA '''

    modelDT = dt.utcnow()

    class ErrorCode(enum.Enum):
        noError = 0
        badFormat = 1
        badSum = 2

    def __init__(self):
        self.header450 = "UdPbC"

    def __analyzeNMEA(self, src):
        body = src.split(',')

        prefix = body[0][0:2]
        type = body[0][2:5]
        item = {'prefix': prefix, 'type': type}

        # -----------------------------------------------------------------
        if type == 'GGA':
            #            print(body)

            hhmmss = body[1]
            item['lat'] = body[2]
            item['ns'] = body[3]
            item['lon'] = body[4]
            item['ew'] = body[5]
            item['mode'] = body[6]

            item['utc'] = self.modelDT.replace(
                hour=int(hhmmss[0:2]),
                minute=int(hhmmss[2:4]),
                second=int(hhmmss[4:6]),
                microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

        # -----------------------------------------------------------------
        elif type == 'RMC':
            #            print(body)

            hhmmss = body[1]

            item['va'] = body[2]
            item['lat'] = body[3]
            item['ns'] = body[4]
            item['lon'] = body[5]
            item['ew'] = body[6]
            item['knot'] = body[7]
            item['head'] = body[8]

            ddmmyy = body[9]

            item['mode'] = body[12]

            item['utc'] = self.modelDT.replace(
                year=int(ddmmyy[4:6]) + 2000,
                month=int(ddmmyy[2:4]),
                day=int(ddmmyy[0:2]),
                hour=int(hhmmss[0:2]),
                minute=int(hhmmss[2:4]),
                second=int(hhmmss[4:6]),
                microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

        # -----------------------------------------------------------------
        elif type == 'ZDA':
            hhmmss = body[1]
            item['hh'] = hhmmss[0:2]
            item['mm'] = hhmmss[2:4]
            item['ss'] = hhmmss[4:6]
            # item['hhmmss'] = body[1]
            item['dd'] = body[2]
            item['mm'] = body[3]
            item['yyyy'] = body[4]


        # -----------------------------------------------------------------
        elif type == 'DTM':
            item['code'] = body[1]


        # -----------------------------------------------------------------
        elif type == 'ROT':
            item['rate'] = body[1]


        # -----------------------------------------------------------------
        elif type == 'VDM':
            item['tn'] = body[1]
            item['sn'] = body[2]
            item['si'] = body[3]
            item['ac'] = body[4]
            item['message'] = body[5]
            item['fb'] = body[6]

        # -----------------------------------------------------------------
        elif type == 'THS':
            item['heading'] = body[1]
            item['va'] = body[2]

        # -----------------------------------------------------------------
        elif type == 'HDT':
            item['heading'] = body[1]
            item['va'] = ''

        return item

    def __analyzeTagBlock(self, src):
        result = {}
        for c in src.split(','):
            ppp = c.split(':')
            result[ppp[0]] = ppp[1]

        return result

    def parse(self, body: object) -> object:

        result = {'error': self.ErrorCode.noError}

        if body[0:len(self.header450)].decode('utf-8') == self.header450:
            part = body[len(self.header450) + 1:-2].decode('utf-8').split('\\')  # drop CR+LF

            tagblock = part[1].split('*')
            if self.calcSum(tagblock[0]) == int(tagblock[1], 16):
                result['tagblock'] = self.__analyzeTagBlock(tagblock[0])
                if part[2][0] in ["$", "!"]:
                    sentence = part[2][1:-3]
                    if self.calcSum(sentence) == int(part[2][-2:], 16):
                        result['sentence'] = self.__analyzeNMEA(sentence)
                    else:
                        result['error'] = self.ErrorCode.badSum
                else:
                    result['error'] = self.ErrorCode.badFormat
            else:
                result['error'] = self.ErrorCode.badSum

        else:
            result['error'] = self.ErrorCode.badFormat

        return result

    def calcSum(self, body):

        ''' return checksum value  '''

        value = 0
        target = np.fromstring(body, dtype=np.uint8, sep='')
        for v in target:
            value ^= v

        return value


if __name__ == '__main__':
    f = MC450Analyzer()

    src = "UdPbC0\\s:AI0117,n:25*39\\!AIVDM,1,1,,A,D04757Q6aM6D,0*6A\r\n".encode('utf-8')

    print(type(src))
    print(src)

    result = f.parse(src)
    print(result)
