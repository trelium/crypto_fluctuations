from multiprocessing import Process
import sys

rocket = 0

def func1():
    global rocket
    print ('start func1')
    while rocket < 300000:
        rocket += 1
    print ('end func1')

def func2():
    global rocket
    print ('start func2')
    while rocket < 30000:
        rocket += 1
    print ('end func2')

if __name__=='__main__':
    p1 = Process(target = func1)
    p1.start()
    p2 = Process(target = func2)
    p2.start()

###
from multiprocessing import Process
def func1:
     #does something

def func2:
     #does something

if __name__=='__main__':
     p1 = Process(target = func1)
     p1.start()
     p2 = Process(target = func2)
     p2.start()