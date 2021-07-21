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


pulser_port='dev/serial0' #define which port to use, in this case serial 0
pulser_baud=112500 #define pulser baud rate. ie frequency in which pi sends out bits
timeout=1

def main():
    print('main')
    coms=pulser_comms() #initalize pulser comms
    coms.amplitude=1000 #amplitude of pulse in V
    coms.period=10**6 #time between pulses in micro s when using pulser's timing
    coms.turn_on() #run class function which turns on pulser and enables pulsing
    time.sleep(10) #let run for a few seconds to obsrve pulses on scope
    coms.turn_off() #shuts off pulsing
    exit() #testing comms to pulser for now
    swi=switch() #initialize switch class
    gps=gps_comms() #initialize gps comms 
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

#if we decide to put the little rpi camera module i have on the payload this could be used
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
        self.amplitude=1000 #amplidue of pulses
        self.period=100000 #period between pulses
        self.read_write=1 #define read or write bit
        self.flag='0101' #defines flag bits 'abcd' a=read only vcc error, b=enable pulsing, enable eternal triggering, enable high voltage supply
        #self.pulser=serial.Serial(pulser_port,pulser_baud,timeout=1)
        self.start_time=0
        self.code='bbbbHIb' #format of data used in struct module. b=1 byte, H= unsigned short 2bytes, I= unsigned int 4bytes

    #build packet to send to the pulser
    def build_pulsar_packet(self,amplitude,period,read_write,flag):
        
        preamble=0x55 #always the same
        size=0x09 #always the same
        command_code=0x01 #always the same
        io=0b00000000 #defined byte for input or output status
        if(read_write==1):
            io=0b00000001
        amp_bits=self.convert_voltage_to_dec(amplitude) #gets the int value corresponding to a voltage (V)
        per_bits=self.convert_period_to_dec(period) #gets the int value corresponding to a period (uS)
        #handle crc : empty for now
        to_send=struct.pack(self.code,preamble,size,command_code,io,amp_bits,per_bits,flag) #build byte array from previous byte pieces
        
        return to_send #return array which should be used in serial.write()
    
    def build_flag_byte(flag): #empty for now. If we need more control over flag byte this can be created
        return 0
    def convert_voltage_to_dec(self,amplitude): #gets unsigned short int value from a voltage
        if(amplitude<1000):
            print('below range')
            return 0
        if(amplitude>2000):
            print('above range')
            return 2**16-1
        value=int(65536/1000 * (amplitude-1000))
        
        return value
    
    def convert_dec_to_voltage(self,val): #converts unsigned short integer value to a voltage
        
        voltage=1000/65536 * val  +1000
        return voltage

    def convert_period_to_dec(self,period): #converts period to unsigned int value
        if(period<1000):
            print('below range')
            return 0
        if(period>500000):
            print('above range')
            return 2**32-1
        value=int(2**32 /(500000-1000) * (period-1000))
        
        return value
        
    def convert_dec_to_period(self,val): #converts unsigned int value to period
        
        period=(500000-1000)/10**32 * val  +1000
        return period
    
    #read packet returned from the pulser, either after send read command or from the normal response
    def read_pulser_response(self,response): #unpacks data from response and print ampltiude and period to CL
        rec=struct.unpack(self.code,response)
        print(self.convert_dec_to_voltage(rec[4]),'V')
        print(self.convert_dec_to_period(rec[5]),'uS')

        #create general function to read the contents of a returned packet
    def turn_on(self):#will be used to turn on pulsing w/ pulser period
        self.pulser.write(self.build_pulsar_packet(self.amplitude,self.period,1,0b00000101))
        start_time=time()
        time.sleep(.1)
        returned_bytes=self.pulser.read()
        self.read_pulser_response(returned_bytes)

    def turn_off(self): #turns off puslsing
        self.pulser.write(self.build_pulsar_packet(self.amplitude,self.period,1,0b00000000))

    def request_info(self):#sends byte array to request info from the pulser
        self.pulser.write(self.build_pulsar_packet(self.amplitude,self.period,0,0b00000000))
        time.sleep(.1)
        returned_bytes=self.pulser.read()
        self.read_pulser_response(returned_bytes)
    

if __name__=='__main__':
    main()

