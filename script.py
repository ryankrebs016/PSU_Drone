import time
import numpy as np
import serial
import RPi.GPIO as gpio

#call this script when the pi is started up. Then use the switch to turn on pulsing.


pulser_port=''
pulser_baud=1600
timeout=1

#make class for switch to clean up code a little
def switch():
    pin=18
    gpio.setmode(gpio.BCM)
    gpio.setup(pin,gpio.INPUT)
    def read_switch():
        return gpio.INPUT(pin)

def gps_comms():
    print('holding')
    time=0
    coords=0

#make class for commuication with the pulsers
def pulser_comms():
    amplitude=1000
    period=100000
    read_write=1
    flag='0110'
    pulser=serial.Serial(pulser_port,pulser_baud,timeout=1)
    start_time=0

    #build packet to send to the pulser
    def build_pulsar_packet(amplitude,period,read_write,flag):
        to_send=[]
        preamble=0x55
        size=0x9
        command_code=0x01
        io=0b00000000
        if(read_write==1):
            io=0b00000001
        amp_bits=convert_voltage_to_binary(amplitude)
        per_bits=convert_period_to_binary(period)
        flag
        #handle crc
        to_send=[preamble,size,command_code,io,amp_bits,per_bits,flag_bits,crc]
        return to_send
    
    def build_flag_byte(flag):
        return
    def convert_voltage_to_binary(amplitude):
        if(amplitude<1000):
            print('below range')
            return '{0:016b}'.format(0)
        if(amplitude>2000):
            print('above range')
            return '{0:016b}'.format(65535)
        bit_value=65536/1000 * (amplitude-1000)
        binary_val='{0:016b}'.format(bit_value)
        return binary_val
    
    def convert_binary_to_voltage(val):
        i=int(val,2)
        voltage=1000/65536 * i  +1000
        return voltage

    def convert_period_to_binary(period):
        if(period<1000):
            print('below range')
            return '{0:032b}'.format(0)
        if(period>500000):
            print('above range')
            return '{0:032b}'.format(2**32 -1)
        bit_value=2**32 /(500000-1000) * (period-1000)
        binary_val='{0:032b}'.format(bit_value)
        return binary_val
        
    def convert_binary_to_period(val):
        i=int(val,2)
        period=(500000-1000)/10**32 * i  +1000
        return period
    
    #read packet returned from the pulser, either after send read command or from the normal response
    def read_pulser_response(response):
        print('holding')
        #create general function to read the contents of a returned packet
    def turn_on():
        pulser.write(build_pulsar_packet(amplitude,period,1,'0110'))
        start_time=time()
        time.sleep(.001)
        returned_bytes=pulser.read()
        read_pulser_response(returned_bytes)

    def turn_off():
        pulser.write(build_pulsar_packet(amplitude,period,1,'0000'))

    def request_info():
        pulser.write(build_pulsar_packet(amplitude,period,0,'0000'))
        time.sleep(.001)
        returned_bytes=pulser.read()
        read_pulser_response(returned_bytes)
    

if __name__=='__main__':
    coms=pulser_comms() #initalize pulser comms
    swi=switch() #initialize switch class
    gps=gps_comms()
    coms.amplitude=1000 #amps of pulse in V
    coms.period=10**6 #time between pulse in micro s

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


