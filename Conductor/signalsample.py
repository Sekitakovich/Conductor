import signal
import time


def scheduler(arg1, args2):
    print(time.time())

signal.signal(signal.SIGINT, scheduler)
signal.setitimer(signal.ITIMER_REAL, 1, 1)

time.sleep(1000)