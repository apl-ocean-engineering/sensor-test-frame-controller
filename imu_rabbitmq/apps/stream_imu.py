#!/usr/bin/env python3

import argparse
from imu import Imu


def handle_imu_data( imu_data ):
    print("Got data from %f" % imu_data.system_timestamp )


import argparse

parser = argparse.ArgumentParser(description='Read data from Yostlabs IMU')
parser.add_argument('port_name',
                    help='Device file for serial port (e.g., /dev/ttyUSBS0)')

parser.add_argument('--output',
                    help='Save output to file')

parser.add_argument('--raw-output',
                    help='Save raw output to file')


args = parser.parse_args()

imu = Imu("imu", args.port_name)
imu.add_callback( handle_imu_data )

imu.run()
