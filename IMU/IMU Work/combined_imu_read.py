#!/usr/bin/env python2

from fieldForce_TCM import FieldforceTCM
from vectorNav import VectorNav
from yost_module import Yost

import datetime
import math
import csv
import time
'''
Orientation Conventions

Euler angles/(Roll-Pitch-Yaw):
    X-axis is positive forward, through the nose of the aircraft
    Y-axis is positive out the right wing
    Z-axis is positive down (so that right hand rule is obeyed)
    Rotation is clockwise, obeying right hand rule with thumb being positive direction
    Sequence of operations: ZYX or yaw-pitch-roll
'''


write = True # For debug purposes
directory = "data/"
curr_date_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

tcm_file = directory + curr_date_time + "tcm.csv"
vnav_file = directory + curr_date_time + "vnav.csv"
yost_file = directory + curr_date_time + "yost.csv"


def write_csv(filename, data):
    if write:
        with open(filename, 'ab') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(data)


def runIMUs(TCM=None, VNav=None, Yost=None):
    if TCM != None:
        TCM.stopAll()
        TCM.startStreaming()
        write_csv(tcm_file, ["Time", "ax", "ay", "az"])
        print("TCM Initialized")

    if VNav != None:
        VNav.flushPort()
        write_csv(vnav_file,  ["Time", "yaw","pitch","roll","magx","magy","magz","accelx","accely","accelz","gyrox","gyroy","gyroz"])
        VNav.start()
        print("VectorNav Initialized")
    
    if Yost != None:
        Yost.start()
        write_csv(yost_file, ["Time", "quat 1", "quat 2", "quat 3", "quat 4"])
        print("YostLabs Initialized")

    init_time = time.time()

    while True:
        if TCM != None:
            TCM_datum = TCM.getData(2)
            ax = math.radians(TCM_datum.RAngle)
            ay = math.radians(TCM_datum.PAngle)
            az = -math.radians(TCM_datum.Heading)
            data = [time.time() - init_time, ax, ay, az]
            write_csv(tcm_file, data)
            print("TCM: " + str(data))
        
        if VNav != None and VNav.q.qsize() > 0:
            data = VNav.q.get()
            while VNav.q.qsize() > 0:
                data = VNav.q.get()
            data.insert(0,time.time()-init_time)
            if len(data) != 13:
                print(data)
            print("VNav: " + str(data))
            write_csv(vnav_file, data)
                
        
        if Yost != None and Yost.q.qsize() > 0:
            data = list(Yost.q.get())
            while Yost.q.qsize() > 0:
                data = list(Yost.q.get())
            data.insert(0,time.time()-init_time)
            # data[0] = (time.time() - init_time) # Replacing yost timestamp instead of pre-pending
            write_csv(yost_file, data)
            print("Yost: " + str(data))

if __name__ == '__main__':
    imu1 = FieldforceTCM("COM23", 38400) #port, baud rate
    imu2 = VectorNav("COM22") #port
    imu3 = Yost("COM5", frequency=1000) #port, frequency
    runIMUs(TCM=imu1, VNav=imu2, Yost=imu3)
    # runIMUs(Yost=imu3)