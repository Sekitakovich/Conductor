import numpy as np

class JRCnmea:
    '''
    ------------------------------------------------------------------------------
    Parse NMEA formated string to dict

        by K.Seki 2018-06-01
    ------------------------------------------------------------------------------
    '''

    noError = 0
    errorBadFormat = 1
    errorCheckSumNoMatch = 2
    errorUnkownType = 3

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def __init__(self):
        return super().__init__()

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def __calcSum(self, body):
        value = 0
        ooo = np.fromstring(body, dtype=np.uint8, sep='')
        for a in ooo:
            value ^= a

        return value

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def __analyze(self, body):
        prefix = body[0][0:2]
        type = body[0][2:5];
        item = {'prefix': prefix, 'type': type}

        if type == 'RMC':
            item['lon'] = body[1]
            item['lat'] = body[3]

        elif type == 'ZDA':
            hhmmss = body[1]
            item['hh'] = hhmmss[0:2]
            item['mm'] = hhmmss[2:4]
            item['ss'] = hhmmss[4:6]
            # item['hhmmss'] = body[1]
            item['dd'] = body[2]
            item['mm'] = body[3]
            item['yyyy'] = body[4]

        elif type == 'GGA':
            item['nn'] = body[7]

        elif type == 'DTM':
            item['code'] = body[1]

        elif type == 'ROT':
            item['rate'] = body[1]

        elif type == 'VDM':
            item['tn'] = body[1]
            item['sn'] = body[2]
            item['si'] = body[3]
            item['ac'] = body[4]
            item['message'] = body[5]
            item['fb'] = body[6]

        return item

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def parse(self, src, checkThisSum = True):
        result = {'status': self.noError}

        if src[0] in ['$', '!']:
            body = src[1:-3]
            if checkThisSum == True and int(src[-2:], 16) != self.__calcSum(body):
                result['status'] = self.errorCheckSumNoMatch
            else:
                result['body'] = self.__analyze(body.split(','))

        else:
            result['status'] = self.errorBadFormat

        return result
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


if __name__ == "__main__":

    nmea = JRCnmea()

    src = [
        "$GPRMC,085120.307,A,3541.1493,N,13945.3994,E,000.0,240.3,181211,,,A*6A",
        ]

    for s in src:
        result = nmea.parse(s, False)
        if (result['status'] == JRCnmea.noError):
            print(result['body'])

        else:
            print("Error %d" % result['status'])