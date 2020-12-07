import sys, time, signal
def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    if len(sys.argv) == 3:
        print("\tadversary iit", sys.argv[2])
    elif len(sys.argv) == 2:
        print("\tpeer")

    time.sleep(10)