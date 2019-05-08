#!/usr/bin/env python2
# vim: set fileencoding=utf-8 :
"""
Copyright (c) 2012, Michael Koval
Copyright (c) 2012, Cody Schafer <cpschafer --- gmail.com>
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import serial
import struct
import crcmod
import threading
from time import time as _time
from collections import namedtuple

import math

class _one_msg_stall:
    def __init__(self, *frame_ids):
        self.cond = threading.Condition()
        self.data = None
        self.frame_ids = frame_ids

    def cb(self):
        def real_cb(pkts):
            c = self.cond
            frame_ids = self.frame_ids

            c.acquire()
            if self.data != None:
                c.release()
                return True # we are no longer waiting
            c.release()

            for p in pkts:
                if p[0] in frame_ids:
                    c.acquire()
                    self.data = bytes(p)
                    c.notify()
                    c.release()
                    return True # remove us.
            return False # haven't got our packet yet.
        return real_cb

    def wait(self, timeout=None):
        c = self.cond
        c.acquire()
        if timeout != None:
            start_time = _time()
        while self.data == None:
            c.wait(timeout)
            # required due to http://bugs.python.org/issue1175933
            if timeout != None and (_time() - start_time) > timeout:
                c.release()
                return None
        it = self.data
        c.release()
        return it


class TimeoutException(Exception):
    def __init__(self, msg, time=None):
        Exception.__init__(self, msg)
        self.time=time

class FrameID:
    kGetModInfo         = 1
    kModInfoResp        = 2
    kSetDataComponents  = 3
    kGetData            = 4
    kDataResp           = 5
    kSetConfig          = 6
    kGetConfig          = 7
    kConfigResp         = 8
    kSave               = 9
    kStartCal           = 10
    kStopCal            = 11
    kSetParam           = 12
    kGetParam           = 13
    kParamResp          = 14
    kPowerDown          = 15
    kSaveDone           = 16
    kUserCalSampCount   = 17
    kUserCalScore       = 18
    kSetConfigDone      = 19
    kSetParamDone       = 20
    kStartIntervalMode  = 21
    kStopIntervalMode   = 22
    kPowerUp            = 23
    kSetAcqParams       = 24
    kGetAcqParams       = 25
    kAcqParamsDone      = 26
    kAcqParamsResp      = 27
    kPowerDownDone      = 28
    kFactoryUserCal     = 29
    kFactoryUserCalDone = 30
    kTakeUserCalSample  = 31
    kFactoryInclCal     = 36
    kFactoryInclCalDone = 37
    kSetMode            = 46
    kSetModeResp        = 47
    kSyncRead           = 49
FrameID.__dict__['invert'] = dict([(v, k) for (k, v) in FrameID.__dict__.iteritems()])

_DEFAULT_TIMEOUT = 0.5
_struct_uint8   = struct.Struct('>B')
_struct_uint16  = struct.Struct('>H')
_struct_uint32  = struct.Struct('>I')
_struct_float32 = struct.Struct('>f')
_struct_boolean = struct.Struct('>?')

class FieldforceTCM:
    Component = namedtuple('Component', [
        'name', 'struct'
    ])
    ModInfo   = namedtuple('ModInfo', [
        'Type', 'Revision'
    ])
    CalScores = namedtuple('CalScores', [
        'MagCalScore', 'CalParam2', 'AccelCalScore', 'DistError',
        'TiltError', 'TiltRange'
    ])
    AcqParams = namedtuple('AcqParams', [
        'PollingMode', 'FlushFilter', 'SensorAcqTime', 'IntervalRespTime'
    ])
    Datum     = namedtuple('Datum', [
        'Heading', 'Temperature', 'Distortion', 'CalStatus',
        'PAligned', 'RAligned', 'IZAligned',
        'PAngle', 'RAngle', 'XAligned', 'YAligned', 'ZAligned'
    ])

    good_cal_score = CalScores('< 1', 'ignore (pni reserved)', '< 1',
            '< 1', '< 1', 'angle of tilt' )


    components = {
        5:  Component('Heading',     _struct_float32),
        7:  Component('Temperature', _struct_float32),
        8:  Component('Distortion',  _struct_boolean),
        9:  Component('CalStatus',   _struct_boolean),
        21: Component('PAligned',    _struct_float32),
        22: Component('RAligned',    _struct_float32),
        23: Component('IZAligned',   _struct_float32),
        24: Component('PAngle',      _struct_float32),
        25: Component('RAngle',      _struct_float32),
        27: Component('XAligned',    _struct_float32),
        28: Component('YAligned',    _struct_float32),
        29: Component('ZAligned',    _struct_float32)
        }    
    
    
    def __init__(self, path, baud):
        self.fp = serial.Serial(
        port     = path,
        baudrate = baud,
        bytesize = serial.EIGHTBITS,
        parity   = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE
        )
        # CRC-16 with generator polynomial X^16 + X^12 + X^5 + 1.
        self.crc = crcmod.mkCrcFun(0b10001000000100001, 0, False)
        self.recv_cbs = []
        self.cb_lock = threading.Lock()

        self.decode_pos = 0
        self.discard_stat = 0
        self.recv_buf = bytearray()

        self.read_th = rt = threading.Thread(target=self.reader())
        rt.daemon = True
        rt.start()
        
    def reader(self):
        """
        factory which returns a callable object suitable (for example)
        to pass to threading.Thread(target=reader()).
        """
        def do_it():
            while True:
                self._wait_and_read_all()
                rdy_pkts = self._decode()
                if rdy_pkts:
                    #for pkt in rdy_pkts:
                    #    fid = ord(pkt[0])
                    #    print 'new pkt: {0} {1}'.format(FrameID.invert[fid], fid)

                    self._notify_listeners(rdy_pkts)
        return do_it        
        
        
    def remove_listener(self, r):
        c = self.recv_cbs
        l = self.cb_lock
        l.acquire()
        try:
            # FIXME: linear search.
            c.remove(r)
        except Exception:
            pass
        l.release()  
        

    def add_listener(self, cb):
        c = self.recv_cbs
        l = self.cb_lock
        l.acquire()
        c.append(cb)
        l.release()
        return cb        
        
    def stopAll(self):
        """
        Stop all modes which result in periodic messages
        """
        self.stopStreaming()
            
 
    def stopStreaming(self):
        """
        Stops streaming data; companion of startStreaming(). Streaming must be
        stopped before any other commands can be used.
        """
        self._sendMessage(FrameID.kStopIntervalMode) 
            
    def startStreaming(self):
        """
        Start streaming data. See setAcquisitionParams() for more information
        and use stopStreaming() when done. Streaming must be stopped before any
        other commands can be used.
        """
        self._sendMessage(FrameID.kStartIntervalMode)  
        
    def getData(self, timeout=None):
        """
        Query a single packet of data that containing the components specified
        by setDataComponents(). All other components are set to zero.
        """
        # FIXME: race condition: data may already have passed us by before we are listening.
        self._sendMessage(FrameID.kGetData)
        return self.readData(timeout) 

    def readData(self, timeout=None):
        """
        Read a single DataResp frame
        """
        (_, payload) = self._recvSpecificMessage(FrameID.kDataResp, timeout=timeout)

        (comp_count, ) = struct.unpack('>B', payload[0])
        comp_index = 0
        offset = 1
        data = dict()

        while comp_index < comp_count:
            (component_id, ) = struct.unpack('>B', payload[offset])
            component = self.components[component_id]

            datum = payload[(offset + 1):(offset + component.struct.size + 1)]
            (value, ) = component.struct.unpack(datum)
            data[component.name] = value

            offset     += 1 + component.struct.size
            comp_index += 1

        return self._createDatum(data)  
    
 
    def _wait_and_read_all(self):
        s = self.fp
        b = self.recv_buf
        b.append(s.read())
        wait_ct = s.inWaiting()
        if wait_ct > 0:
            b.extend(s.read(wait_ct))

    def _notify_listeners(self, rdy_pkts):
        cbs = self.recv_cbs
        lock = self.cb_lock
        lock.acquire()
        x = []
        for i in range(0, len(cbs)):
            if cbs[i](rdy_pkts):
                # A callback returning true is removed.
                # XXX: Can't remove while iterating over it.
                x.append(i)
        for it in x:
            del cbs[it]
        lock.release()
        
    def _decode(self):
        """
        Given self.recv_buf and self.crc, attempts to decode a valid packet,
        advancing by a single byte on each decoding failure.
        """
        b = self.recv_buf
        crc_fn = self.crc
        decode_pos  = 0
        discard_amt = 0
        good_pos    = 0 # discard before this
        decode_len  = len(b)
        rdy_pkts = []        
         # min packet = 2 (byte_count) + 1 (frame id) + 2 (crc) = 5
        #attempt_ct = 0
        #print decode_len
        while decode_len >= 5:
            #attempt_ct += 1
            #print '--decode attempt {0}'.format(attempt_ct)
            (byte_count, ) = struct.unpack('>H', bytes(b[decode_pos:decode_pos+2]))
            frame_size = byte_count - 4

            # max frame = 4092, min frame = 1
            if frame_size < 1 or frame_size > 4092:
                #print '-- fail 1 {0}'.format(frame_size)
                decode_pos += 1
                decode_len -= 1
                continue

            # not enough in buffer for this decoding
            if decode_len < byte_count:
                #print '-- fail 2'
                decode_pos += 1
                decode_len -= 1
                continue

            frame_pos = decode_pos + 2
            frame_id = b[frame_pos]

            # invalid frame id
            if frame_id not in FrameID.__dict__.itervalues():
                #print '-- fail 3'
                decode_pos += 1
                decode_len -= 1
                continue

            crc_pos   = frame_pos  + frame_size
            crc = b[crc_pos:crc_pos + 2]
            entire_pkt = b[decode_pos:frame_pos + frame_size + 2]

            # CRC failure
            crc_check = crc_fn(bytes(entire_pkt))
            if crc_check != 0:
                #print '-- fail 4'
                decode_pos += 1
                decode_len -= 1
                continue

            # valid packet? wow.
            rdy_pkts.append(b[frame_pos:frame_pos + frame_size])

            # number of invalid bytes discarded to make this work.
            discard_amt += decode_pos - good_pos

            # advance to right after the decoded packet.
            decode_pos += byte_count
            decode_len -= byte_count

            # the decode position that will be started from next time
            good_pos     = decode_pos

        # discard this packet from buffer. also discard everything prior.
        del b[0:good_pos]
        self.discard_stat += discard_amt

        return rdy_pkts


    def _recvSpecificMessage(self, *expected_frame_id, **only_timeout):
        w = self._recv_msg_prep(self, *expected_frame_id)
        return self._recv_msg_wait(w, **only_timeout) 
    

    def _recv_msg_prep(self, *expected_frame_id):
        s = _one_msg_stall(*expected_frame_id)
        t = self.add_listener(s.cb())
    
        return (s, t)    
    
    def _recv_msg_wait(self, w, timeout = _DEFAULT_TIMEOUT):
        s, t = w
        r = s.wait(timeout)

        self.remove_listener(t)

        if (r == None):
            raise TimeoutException('Did not recv frame_id {0} within {1} seconds.'.format(s.frame_ids, timeout), timeout)
        else:
            return (ord(r[0]), r[1:])    
        
    def _sendMessage(self, frame_id, payload=b''):
        count = len(payload) + 5
        head = struct.pack('>HB{0}s'.format(len(payload)), count, frame_id, payload)
        tail = struct.pack('>H', self.crc(head))
        self._send(head + tail)  
        
    def _send(self, fmt):
        self.fp.write(fmt)
        
    def _createDatum(self, data):
        for component in self.Datum._fields:
            if component not in data.keys():
                data[component] = None
        return self.Datum(**data)        
        
        
def start_IMU(IMU):
    IMU.stopAll()
    
    IMU.startStreaming()

if __name__ == '__main__':
    IMU = FieldforceTCM("/dev/ttyUSB0", 38400)
    start_IMU(IMU)
    while True:
        datum = IMU.getData(2)
        ax = math.radians(datum.RAngle)
        ay = math.radians(datum.PAngle)
        az = -math.radians(datum.Heading)
        
        print(ax, ay, az)
    
    
    
    
    
    
    
    
    
    
    
    