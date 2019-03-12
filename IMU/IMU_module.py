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
import queue

class IMU():
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
        self.q = queue.Queue()
        self.running = True

        self.port_num = port_num
        self.port = serial.Serial(port_num, 115200, timeout=1.5)
        '''
        Init Port
        '''
        self._init_port(frequency)

    
    def _init_port(self, frequency=10):
        self.send_IMU_data(chr(0x56)) # Try to stop the output before doing any configuration
        #self.send_IMU_data(chr(0xdd)+chr(0x00)+chr(0x00)+chr(0x00)+chr(0x47)) # Set the header to contain the timestamp        
        self.send_IMU_data(chr(0xdd)+chr(0x0)+chr(0x0)+chr(0)+chr(2))
        self.setStreamTiming(frequency) # Currently only supports 1Hz and 10Hz
        self.setStreamSlots() # Set the streaming slots to stream the tared quaternion

    def get_IMU_data(self):
        data = self.port.read(20)
        #header = self.port.read(7)
        #data = self.port.read(28)
        #TODO what is this function doing?
        header = struct.unpack(">I", data[0:4])
        data = struct.unpack(">ffff",data[4:20])
        return header, data
        
    def send_IMU_data(self, cmd):
        self.send_command_bytes_usb(cmd)
        self.port.read(4)
    
    def start_stream_to_queue(self, with_header=True):
        """

        The start_stream method sends the command that causes the IMU to 
        start streaming data, and drains any residual bytes in the buffer. It does not handle any configuration of the 
        stream settings, aside from setting whether or not to include a
        response header, which is ______. #TODO
        

        Args:
            with_header (Boolean, optional): Determines whether or not to 
                stream with a response header. Defaults to True.

        """
        # Start Streaming
        self.send_command_bytes_usb(chr(0x55), response_header=with_header)
        # Drain any residual bytes
        self.port.reset_input_buffer()
        while self.running:
            header, data = self.get_IMU_data()
            #timestamp = header[1]
            """
            DO STUFF
            """
            #print(self.port_num, data)
            #print("%f,%d,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data1) )
            #print("% 9f,% 9f,% 9f,% 9f,% 9f,% 9f,% 9f" % tuple(data) )
            self.q.put((header, data))

    def send_command_bytes_usb(self, data, response_header = False):
        """

        The send_command_bytes_usb method is a general command that takes data and 
        packages it into a form that the YOST Labs IMU can understand. The 
        data is in the format _______, and is repackaged as ___________. It
        also handles whether or not to include a response_header, which is
        set to False by default.

        Args:
            data (str): Description of `param1`.
            response_header (Boolean, optional): Determines whether or not to 
                stream with a response header. Defaults to False.

        """
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

    def stop_streaming(self, close_port=False):
        """

        The stop_streaming method simply sends the stop stream command to the
        IMU, and can also close the port if specified.

        Args:
            close_port (Boolean, optional): If set to be True, function will 
                also close port. Defaults to False.


        """
        self.running = False
        self.send_command_bytes_usb(chr(0x56))
        if close_port:
            self.port.close()

    def setStreamTiming(self, frequency):
        # Set the stream timing
        # From manual page 39:
        #   0x52   : Set streaming timing, takes 3 x 4-byte unsigned ints, all in microsecond
        #   bytes 1-5   : interval (don't know what these mean, though 0x000003E8 == 1000 us = 1 ms)
        #               :   0x186A0 = 100,000 = 10Hz
        #               :   0xF4240 = 1,000,000 = 1Hz
        #   bytes 6-9   : duration -- how long the streaming will run for (set to 0xFFFFFFFF.  What does it mean?)
        #   bytes 10-13 : delay between start command and streaming data .. insert a short 100ms delay to allow
        #                 other response headers to clear the system
        
        delayTime = chr(0x0)+chr(0x01)+chr(0x86)+chr(0xA0)
        duration = chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)
        #TODO: Get this working
        # freqInterval = hex(1000000.0 / frequency)
        
        freqInterval = chr(0x0)
        if frequency == 1:
            freqInterval = chr(0x0)+chr(0x0F)+chr(0x42)+chr(0x40)
        elif frequency == 10:
            freqInterval = chr(0x0)+chr(0x1)+chr(0x86)+chr(0x0A)
        elif frequency == 1000:
            freqInterval = chr(0x0)+chr(0x00)+chr(0x03)+chr(0xE8)
        

        self.send_IMU_data(chr(0x52)+freqInterval+duration+delayTime)

    def setStreamSlots(self):
        # Set the streaming slots to stream the tared quaternion
        # From manualpage 39:
        #   0x50   : Set streaming slots, takes 8 bytes, presumably 8 "slots"
        #   0x00   : Read filtered, tared orientation(Quaternion) --> 16 bytes
        #   0x01   : Read filtered, tared orientation(Euler Angles) --> 12 bytes
        #   0xff   : Must mean "don't stream anything"

        #TODO get quaternion streaming
        #self.send_IMU_data(chr(0x50)+chr(0x00)+chr(0x01)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)) 
        # Quaternions only
        self.send_IMU_data(chr(0x50)+chr(0x00)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff)+chr(0xff))

'''
Streaming Commands
 0(0x00), Read tared orientation as quaternion
 1(0x01), Read tared orientation as euler angles
 2(0x02), Read tared orientation as rotation matrix
 3(0x03), Read tared orientation as axis angle
 4(0x04), Read tared orientation as two vector
 5(0x05), Read difference quaternion
 6(0x06), Read untared orientation as quaternion
 7(0x07), Read untared orientation as euler angles
 8(0x08), Read untared orientation as rotation matrix
 9(0x09), Read untared orientation as axis angle
 10(0x0a), Read untared orientation as two vector
 11(0x0b), Read tared two vector in sensor frame
 12(0x0c), Read untared two vector in sensor frame
 32(0x20), Read all normalized component sensor data
 33(0x21), Read normalized gyroscope vector
 34(0x22), Read normalized accelerometer vector
 35(0x23), Read normalized compass vector
 37(0x25), Read all corrected component sensor data
 38(0x26), Read corrected gyroscope vector
 39(0x27), Read corrected accelerometer vector
 40(0x28), Read corrected compass vector
 41(0x29), Read corrected linear acceleration
 43(0x2B) Read temperature C
 44(0x2C), Read temperature F
 45(0x2D), Read confidence factor
 64(0x40), Read all raw component sensor data
 65(0x41), Read raw gyroscope vector
 66(0x42), Read raw accelerometer vector
 67(0x43), Read raw compass vector
 201(0xc9), Read battery voltage
 202(0xca), Read battery percentage
 203(0xcb), Read battery status
 250(0xfa), Read button state
 255(0xff), No command
'''



        
