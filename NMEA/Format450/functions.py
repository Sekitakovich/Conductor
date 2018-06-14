import numpy as np
import enum

from numpy.core.multiarray import ndarray


class Functions450:

    ''' functions for 450/NMEA '''

    class ErrorCode(enum.Enum):
        noError = 0
        badFormat = 1
        badSum = 2

    def __init__(self):
        self.header450 = "UdObC"

    def parse(self, body):

        result = {'error': self.ErrorCode.noError}

        if body[0:len(self.header450)].decode('utf-8') == self.header450:
            part = body[len(self.header450)+1:-2].decode('utf-8').split('\\') # drop CR+LF
            result['tagblock'] = part[1]
            result['sentence'] = part[2]

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

    f = Functions450()

    src = "UdObC0\\s:AI0117,n:25*39\\!AIVDM,1,1,,A,D04757Q6aM6D,0*6A\r\n".encode('utf-8')

    print(src)

    result = f.parse(src)
    print(result)
