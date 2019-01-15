#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 10:41:48 2019

@author: mitchell & stefan
"""
import serial
import struct
import io
import time
import argparse

class IMU:
    def __init__(self, port_num, frequency=1):
        """Example of docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1 (str): Description of `param1`.
            param2 (:obj:`int`, optional): Description of `param2`. Multiple
                lines are supported.
            param3 (:obj:`list` of :obj:`str`): Description of `param3`.

        """
        self.port_num = port_num
        #TODO what is this fuction doing? 
        self.port = serial.Serial(port_num, 115200, timeout=1.5)
        '''
        Init Port
        '''
        self._init_port(frequency)
        self.start_stream()
    
    def get_IMU_data(self):
        header = self.port.read(7)
        #TODO what is this function doing?
        header = struct.unpack(">cIcc", header)

        data = self.port.read(28)
        data = struct.unpack(">fffffff",data)
        return header, data
        
    def send_IMU_data(self, cmd):
        self.send_command_bytes_usb(cmd)
    
    def start_stream(self):
        # Start Streaming
        self.send_command_bytes_usb(chr(0x55), response_header=True)
        # Drain any residual bytes
        self.port.read(128)

    def send_command_bytes_usb(self, data, response_header = False):
        checksum = 0

        for d in data:
            checksum += ord(d)

        # Construct the packet.
        # NOTE: If you want the response header use 0xf9;  
        #       for no response header (see below) use 0xf7
        packet = chr(0xf7)

        if response_header:
            packet = chr(0xf9)

        packet += data+chr(checksum % 256)
        self.port.write(packet.encode('latin-1'))

    def stop_streaming(self):
        self.send_command_bytes_usb(chr(0x56))
        self.port.close()

    def _init_port(self, frequency):
        self.send_IMU_data(chr(0x56))
        #TODO make this friendly
        if frequency == 10:
            self.send_IMU_data(chr(0xdd)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x47))
        self.send_IMU_data(chr(0x52)+chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0))
        self.send_IMU_data(chr(0x50)+chr(0x0)+chr(0x01)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff))

        #self.send_command_bytes_usb(chr(0x56))
        #self.send_command_bytes_usb(chr(0xdd)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x47))
        #self.send_command_bytes_usb(chr(0x52)+chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0))
        #self.send_command_bytes_usb(chr(0x50)+chr(0x0)+chr(0x01)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff))
