import socket
from contextlib import closing
import threading
from datetime import datetime as dt

import mc450analyzer
import ais


class RunningData:
    JBGPS = {'lon': 0.0, 'lat': 0.0, 'ns': '', 'ew': '', 'utc': '', 'from': ''}
    JBHDG = {'heading': 0.0, 'from': ''}
    AIS = {
        'typeStatic': {},
        'typeDynamic': {},
        'typeMessage': {},
        'typeAtoN': {
            'mid': 0,
            'sid': 0,
            'type': 0,
            'name': "",
            'acc': 0,
            'lon': 0,
            'lat': 0,
            'fwd': 0,
            'bk': 0,
            'left': 0,
            'right': 0,
            'ts': "",
            'opi': 0,
            'status': 0,
            'vflg': 0,
            'exname': "",
        },
    }

    stampGPS = {'level': 0, 'last': dt.now()}


class UDPreceiver(threading.Thread):
    """ あまり好かんが日本語で書いてみよう """

    thisGroup = '0.0.0.0'  # multicast address group
    thisPort = 0
    thisIPV4 = '0.0.0.0'  # inaddr_any
    maxSize = (1024 * 4)

    analyzer = mc450analyzer.MC450Analyzer()
    aisDecorder = ais.AISMessageDecoder()

    database = None

    def __init__(self, name, group, port, database, ev):
        super(UDPreceiver, self).__init__()
        self.thisGroup = group
        self.thisPort = port
        self.name = name
        self.database = database
        self.ev = ev

    def run(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self.thisPort))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                            socket.inet_aton(self.thisGroup) + socket.inet_aton(UDPreceiver.thisIPV4))

            while True:
                udpPacket: object = sock.recv(self.maxSize)  # use blocking
                result = self.analyzer.parse(udpPacket)
                if result['error'] == self.analyzer.ErrorCode.noError:
                    tagblock = result['tagblock']
                    sentence = result['sentence']
                    #                    print("from %s: %s" % (tagblock['s'], sentence))

                    if sentence['type'] == "GGA":
                        if sentence['mode'] != '0':
                            self.database.JBGPS['lon'] = float(sentence['lon'])
                            self.database.JBGPS['lat'] = float(sentence['lat'])
                            self.database.JBGPS['ns'] = sentence['ns']
                            self.database.JBGPS['ew'] = sentence['ew']
                            self.database.JBGPS['from'] = sentence['prefix'] + sentence['type']
                            self.database.JBGPS['utc'] = sentence['utc']
                    #                           self.ev.set()

                    elif sentence['type'] == "RMC":
                        if sentence['va'] != 'V':
                            if sentence['mode'] != 'N':
                                self.database.JBGPS['lon'] = float(sentence['lon'])
                                self.database.JBGPS['lat'] = float(sentence['lat'])
                                self.database.JBGPS['ns'] = sentence['ns']
                                self.database.JBGPS['ew'] = sentence['ew']
                                self.database.JBGPS['from'] = sentence['prefix'] + sentence['type']
                                self.database.JBGPS['utc'] = sentence['utc']
                    #                                self.ev.set()

                    elif sentence['type'] in ("THS", "HDT"):
                        if sentence['va'] != 'V':
                            self.database.JBHDG['heading'] = float(sentence['heading'])
                            self.database.JBHDG['from'] = sentence['prefix'] + sentence['type']
                    #                            self.ev.set()

                    elif sentence['type'] in ("VDM", "VDO"):
                        ais = self.aisDecorder.decode(sentence['message'])
                        if ais['error'] != self.aisDecorder.errorCode.noError:
                            print(ais)

                else:
                    print("Error %s at %s" % (result['error'], result))


if __name__ == '__main__':

    database = RunningData()
    ev = threading.Event()

    member = [
        {'name': 'GPS1', 'address': '239.192.0.1', 'port': 60001},
        {'name': 'GPS2', 'address': '239.192.0.2', 'port': 60002},
        {'name': 'GYRO', 'address': '239.192.0.3', 'port': 60003},
        {'name': 'Weather', 'address': '239.192.0.4', 'port': 60004},
        {'name': 'Sonar', 'address': '239.192.0.5', 'port': 60005},
        {'name': 'NAVTEX', 'address': '239.192.0.6', 'port': 60006},
    ]

    for talker in member:
        name = talker['name']
        address = talker['address']
        port = talker['port']
        print("Start %s" % name)
        talker['thread'] = UDPreceiver(name, address, port, database, ev).start()

    counter = 0
    while True:
        if ev.wait(60) == False:
            print("--- Timeout ---")
        else:
            ev.clear()
            print("#### %d %s %s" % (counter, database.JBGPS, database.JBHDG))
            counter += 1
