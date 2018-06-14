import threading
import time

class OffShooter(threading.Thread):
    def __init__(self, event, name):
        super(OffShooter, self).__init__()
        self.name = name
        self.event = event

    def run(self):
        for counter in range(5):
            print("counter = %d" % counter)
            self.event.set()
            time.sleep(3)

if __name__ == '__main__':

    event = threading.Event()

    ooo = OffShooter(event, "tako").start()

    while True:
        if event.wait(1) == False:
            print("Timeout ...")
        else:
            event.clear()
            print("Hi")
