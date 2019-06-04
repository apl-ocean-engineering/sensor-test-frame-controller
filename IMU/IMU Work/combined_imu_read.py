#!/usr/bin/env python2

from fieldForce_TCM import FieldforceTCM
from vectorNav import VectorNav
from yost_module import Yost

import math
import threading
import csv
import time

def write_csv(filename, data):
    with open(filename, 'ab') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(data)


def runIMUs(TCM=None, VNav=None, Yost=None):
    if TCM != None:
        TCM.stopAll()
        TCM.startStreaming()
        write_csv("data/tcm.csv", [])
        write_csv("data/tcm.csv", ["Time", "ax", "ay", "az"])
        print("TCM Initialized")

    if VNav != None:
        VNav.flushPort()
        write_csv("data/vnav.csv", [])
        write_csv("data/vnav.csv", ["Time", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown"])
        print("VectorNav Initialized")
    
    if Yost != None:
        t = threading.Thread(target=Yost.start_stream_to_queue, args=(True,))
        t.start()
        write_csv("data/yost.csv", [])
        write_csv("data/yost.csv", ["Time", "quat 1", "quat 2", "quat 3", "quat 4"])
        print("YostLabs Initialized")

    while True:
        if TCM != None:
            TCM_datum = TCM.getData(2)
            ax = math.radians(TCM_datum.RAngle)
            ay = math.radians(TCM_datum.PAngle)
            az = -math.radians(TCM_datum.Heading)
            data = [time.time(), ax, ay, az]
            write_csv("data/tcm.csv", data)
            print("TCM: " + str(data))
        
        if VNav != None and VNav.hasData():
            data = VNav.getData()
            if data is None:
                print("Vnav read error")
            else:
                data.insert(0,time.time())
                print("Vnav: " + str(data))
                write_csv("data/vnav.csv", data)
                
        
        if Yost != None and Yost.q.qsize() > 0:
            data = Yost.q.get()
            while Yost.q.qsize() > 0:
                data = Yost.q.get()
            write_csv("data/yost.csv", data)
            print("Yost: " + str(data))

if __name__ == '__main__':
    imu1 = FieldforceTCM("COM23", 38400) #port, baud rate
    imu2 = VectorNav("COM22") #port
    imu3 = Yost("COM5", frequency=1000) #port, frequency
    runIMUs(TCM=imu1, VNav=imu2, Yost=imu3)
    # runIMUs(Yost=imu3)