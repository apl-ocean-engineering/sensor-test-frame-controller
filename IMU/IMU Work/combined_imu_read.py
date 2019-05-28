#!/usr/bin/env python2

# from fieldForce_TCM import FieldforceTCM
from vectorNav import VectorNav
from yost_module import Yost

import math
import threading

def runIMUs(TCM=None, VNav=None, Yost=None):
    if TCM != None:
        TCM.stopAll()
        TCM.startStreaming() 
        print("TCM Initialized")

    if VNav != None:
        VNav.flushPort()
        print("VectorNav Initialized")
    
    if Yost != None:
        t = threading.Thread(target=Yost.start_stream_to_queue, args=(True,))
        t.start()
        print("YostLabs Initialized")

    while True:
        if TCM != None:
            TCM_datum = TCM.getData(2)
            ax = math.radians(TCM_datum.RAngle)
            ay = math.radians(TCM_datum.PAngle)
            az = -math.radians(TCM_datum.Heading)
            print(ax, ay, az)
        
        if VNav != None and VNav.hasData():
            print(VNav.getData())
        
        if Yost != None and Yost.q.qsize() > 0:
            Yost_datum = Yost.q.get()
            while Yost.q.qsize() > 0:
                Yost_datum = Yost.q.get()
            print(Yost_datum)

if __name__ == '__main__':
    # imu1 = FieldforceTCM("/dev/ttyUSB0", 38400) #port, baud rate
    imu2 = VectorNav("COM22")
    imu3 = Yost("COM5", frequency=1000)
    # runIMUs(TCM=imu1, VNav=imu2, Yost=imu3)
    runIMUs(VNav=imu2, Yost=imu3)