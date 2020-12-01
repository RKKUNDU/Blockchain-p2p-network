import threading
import time
import random
def mine(cv):
    while(True):
        print("Mining start...")
        waitingTime = random.randint(5, 30)
        cv.acquire()
        timeout = not cv.wait(waitingTime)
        if timeout:
            print(f"Mining took {waitingTime}!")
        else:
            print("received block from other peer")

        cv.release()
        
def receive_block(cv):
    while(True):
        waitingTime = random.randint(5, 30)
        time.sleep(waitingTime)
        cv.acquire()
        print(f"Created new block within {waitingTime}")
        cv.notify()
        cv.release()

cv = threading.Condition()
t = threading.Thread(target = mine, args = [cv])
c1 = threading.Thread(target = receive_block, args = [cv])
c2 = threading.Thread(target = receive_block, args = [cv])
t.start()
c1.start()
c2.start()
