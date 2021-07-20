import time
import numpy as np
import serial
try:
    import RPi.GPIO as gpio
    from picamera import PiCamera
except:
    print('pi modules not loaded')
import struct


#call this script when the pi is started up. Then use the switch to turn on pulsing.


pulser_port='serial0'
pulser_baud=112500
timeout=1

def main():
    print('main')
    coms=pulser_comms() #initalize pulser comms
    swi=switch() #initialize switch class
    gps=gps_comms()
    coms.amplitude=1000 #amps of pulse in V
    coms.period=10**6 #time between pulse in micro s
    coms.turn_on()
    time.sleep(10)
    coms.turn_off()
    exit() #testing comms to pulser for now
    f=open('data.txt','w')
    f.write('amplitude, pi timing, gps coord, gps timing')
    while(True):
        time.sleep(5)
        on_off=0
        timing=coms.start_time
        
        while(swi.read_switch()==True):
            if(on_off==0):
                coms.turn_on()
            on_off=1
            gps.get_coords()
            gps.get_time()
            f.write('%s,%s,%s,%s'%(coms.amplitude,timing,gps.coords,gps.time))#saves amplitude and apporx time of pulse
            timing=timing+coms.period/10**6#increment by the period of pulses. hopefully it won't be too far off from the rpi clock timing
            time.sleep(coms.period/10**6)

        coms.turn_off()

def camera():
    try:
        cam=PiCamera()
        cam.resolution(1920,1080)
        cam.start_preview()
        time.sleep(2)
        camera.capture('fromflight.jpg')
        camera.close()
    except:
        print('camera not connected')


#make class for switch to clean up code a little
class switch():
    def __init__(self):
        self.pin=18
        gpio.setmode(gpio.BCM)
        gpio.setup(self.pin,gpio.INPUT)
    def read_switch(self):
        return gpio.INPUT(self.pin)

class gps_comms():
    print('holding')
    time=0
    coords=0

#make class for commuication with the pulsers
class pulser_comms():
    def __init__(self):
        self.amplitude=1000
        self.period=100000
        self.read_write=1
        self.flag='0110'
        #self.pulser=serial.Serial(pulser_port,pulser_baud,timeout=1)
        self.start_time=0
        self.code='bbbbHIb'

    #build packet to send to the pulser
    def build_pulsar_packet(self,amplitude,period,read_write,flag):
        
        preamble=0x55
        size=0x09
        command_code=0x01
        io=0b00000000
        if(read_write==1):
            io=0b00000001
        amp_bits=self.convert_voltage_to_dec(amplitude)
        per_bits=self.convert_period_to_dec(period)
        #handle crc : empty for now
        to_send=struct.pack(self.code,preamble,size,command_code,io,amp_bits,per_bits,flag)
        
        return to_send
    
    def build_flag_byte(flag):
        return 0
    def convert_voltage_to_dec(self,amplitude):
        if(amplitude<1000):
            print('below range')
            return 0
        if(amplitude>2000):
            print('above range')
            return 2**16-1
        value=int(65536/1000 * (amplitude-1000))
        
        return value
    
    def convert_dec_to_voltage(self,val):
        
        voltage=1000/65536 * val  +1000
        return voltage

    def convert_period_to_dec(self,period):
        if(period<1000):
            print('below range')
            return 0
        if(period>500000):
            print('above range')
            return 2**32-1
        value=int(2**32 /(500000-1000) * (period-1000))
        
        return value
        
    def convert_dec_to_period(self,val):
        
        period=(500000-1000)/10**32 * val  +1000
        return period
    
    #read packet returned from the pulser, either after send read command or from the normal response
    def read_pulser_response(self,response):
        rec=struct.unpack(self.code,response)
        print(self.convert_dec_to_voltage(rec[4]),'V')
        print(self.convert_dec_to_period(rec[5]),'uS')

        #create general function to read the contents of a returned packet
    def turn_on(self):
        self.pulser.write(self.build_pulsar_packet(self.amplitude,self.period,1,0b00000110))
        start_time=time()
        time.sleep(.1)
        returned_bytes=self.pulser.read()
        self.read_pulser_response(returned_bytes)

    def turn_off(self):
        self.pulser.write(self.build_pulsar_packet(self.amplitude,self.period,1,0b00000000))

    def request_info(self):
        self.pulser.write(self.build_pulsar_packet(self.amplitude,self.period,0,'0000'))
        time.sleep(.1)
        returned_bytes=self.pulser.read()
        self.read_pulser_response(returned_bytes)
    

if __name__=='__main__':
    main()

