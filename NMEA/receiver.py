import socket
from contextlib import closing
import threading
import time

import mc450analyzer

class RunningData:
    pos = {'lon': 0.0, 'lat': 0.0}

class UDPreceiver(threading.Thread):
    """ あまり好かんが日本語で書いてみよう """

    thisGroup = '0.0.0.0'  # multicast address group
    thisPort = 0
    thisIPV4 = '0.0.0.0'  # inaddr_any
    maxSize = (1024 * 4)

    analyzer = mc450analyzer.MC450Analyzer()
    database = None

    def __init__(self, group, port, database):
        super(UDPreceiver, self).__init__()
        self.thisGroup = group
        self.thisPort = port
        self.thisName = name
        self.database = database

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
                    print("from %s(%s): %s" % (tagblock['s'], tagblock['n'], sentence))

                    if sentence['type'] == "RMC":
                        self.database.pos['lon'] = sentence['lon']
                        self.database.pos['lat'] = sentence['lat']

                else:
                    print("Error %s at %s" % (result['error'], result))


if __name__ == '__main__':

    database = RunningData()

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
        UDPreceiver(address, port, database).start()

    counter = 0
    while True:
        print("#### %d %s" % (counter, database.pos))
        counter += 1
        time.sleep(1)



