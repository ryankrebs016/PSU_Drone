from hashlib import new
from sys import byteorder
import time
import numpy as np
import serial
import RPi.GPIO as gpio
try:
    from picamera import PiCamera
except:
    print('pi modules not loaded')

#call this script when the pi is started up. Then use the switch to turn on pulsing.


pulser_port='/dev/serial0' #define which port to use, in this case serial 0
pulser_baud=115200 #define pulser baud rate. ie frequency in which pi sends out bits
timeout=1

def main():
    coms=pulser_comms() #initalize pulser comms
    coms.amplitude=1000 #amplitude of pulse in V
    coms.period=1E5 #time between pulses in micro s when using pulser's timing
    print('Voltage set to %s V. Period set to %s uS'%(coms.amplitude,coms.period))
    #coms.turn_on(0) #run class function which turns on pulser and enables pulsing
    time.sleep(3)
    #coms.request_info()
    #time.sleep(3)
    #coms.turn_off() #shuts off pulsing
    coms.test_RS()
    exit() #testing comms to pulser for now
    ins=inputs() #initialize switch class
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
class inputs():
    def __init__(self):
        self.switch_pin=4
        self.pps_pin=25
       
        gpio.setmode(gpio.BCM)
        gpio.setup(self.switch_pin,gpio.INPUT)
        gpio.setup(self.pps_pin,gpio.INPUT)
       
        gpio.add_event_detect(self.pps_pin,gpio.RISING,callback=self.triggered(),bouncetime=.1)
    def read_switch(self):
        return gpio.INPUT(self.pin)
    def triggered():
        print('saw a pps')


class gps_comms():
    time=0
    coords=0

#make class for commuication with the pulsers
class pulser_comms():
    def __init__(self):
        self.amplitude=1000 #amplidue of pulses
        self.period=100000 #period between pulses
        self.read_write=1 #define read or write bit
        #self.flag='0101' #defines flag bits 'abcd' a=read only vcc error, b=enable pulsing, enable eternal triggering, enable high voltage supply]
        self.flag=0b00000101
        self.pulser=serial.Serial(pulser_port,pulser_baud,timeout=1)
        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)
        self.start_time=0
        self.pulser_rx_pin=23
        self.pulser_tx_pin=24
        gpio.setup(self.pulser_rx_pin,gpio.OUT,initial=True)
        gpio.setup(self.pulser_tx_pin,gpio.OUT,initial=False)

    def set_RS_tx(self):
        gpio.output(self.pulser_rx_pin, True)
        gpio.output(self.pulser_tx_pin, True)
        time.sleep(0.05)
    def set_RS_rx(self):
        gpio.output(self.pulser_rx_pin,False)
        gpio.output(self.pulser_tx_pin,False)
        time.sleep(0.05)
    def test_RS(self):
        gpio.output(self.pulser_rx_pin,False)
        gpio.output(self.pulser_tx_pin,True)
        self.pulser.write([0x01])
        rxed=self.pulser.read(1)
        print(rxed)

    #build packet to send to the pulser
    def build_pulsar_packet(self,amplitude,period,read_write,flag):
        
        preamble=0x55 #always the same
        size=0x09 #always the same
        command_code=0x01 #always the same
        io=0b00000000 #defined byte for input or output status
        if(read_write==1):
            io=0b00000001

        amp_dec=self.convert_voltage_to_dec(amplitude) #gets the int value corresponding to a voltage (V)
        amp_bits=amp_dec.to_bytes(2,byteorder='big')
        
        per_dec=self.convert_period_to_dec(period) #gets the int value corresponding to a period (uS)
        per_bits=per_dec.to_bytes(4,byteorder='big')
 
        to_send_dec=[preamble,size,command_code,io,amp_bits[0],amp_bits[1],per_bits[0],per_bits[1],per_bits[2],per_bits[3],flag]
   
        crc_int=self.crc16(to_send_dec,11)
        crc_hex=crc_int.to_bytes(2,byteorder='big')
        to_send_dec.append(crc_hex[0])
        to_send_dec.append(crc_hex[1])

        return to_send_dec #return array which should be used in serial.write()

    def crc16(self,data, no):
        crc = 0xffff
        poly = 0xa001               # Polynomial used for Modbus RS485 applications
        temp = no

        while True:
            crc ^= data[temp - no]        
            for i in range(0, 8):
                if crc & 0x0001:
                    crc = (crc>>1) ^ poly
                else:
                    crc >>= 1           
            no -= 1
            if no == 0:
                break

        return crc & 0xffff

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
        
        period=(500000-1000)/2**32 * val  +1000
        return period
    
    #read packet returned from the pulser, either after send read command or from the normal response
    def read_pulser_response(self,response): #unpacks data from response and print ampltiude and period to CL
        voltage_packet=int.from_bytes(response[4:5],byteorder='big')
        period_packet=int.from_bytes(response[6:10],byteorder='big')
        
        print(self.convert_dec_to_voltage(voltage_packet),' V')
        print(self.convert_dec_to_period(period_packet),' uS')

        #create general function to read the contents of a returned packet
    def turn_on(self,ext_trigger):#will be used to turn on pulsing w/ pulser period\
        if(ext_trigger==1):
            self.flag=0b00000111
        send_packet=self.build_pulsar_packet(self.amplitude,self.period,1,self.flag)
        print('Sending packet: ',send_packet)
        self.set_RS_tx()
        self.pulser.write(send_packet)
        self.set_RS_rx() 
        time.sleep(2)
        returned_bytes=self.pulser.read(13)
        print('Returning packet: ',returned_bytes)
        self.read_pulser_response(returned_bytes)
        

    def turn_off(self): #turns off puslsing
        self.set_RS_tx()
        self.pulser.write(self.build_pulsar_packet(self.amplitude,self.period,1,0b00000000))

    def request_info(self):#sends byte array to request info from the pulser
        self.set_RS_tx()
        self.pulser.write(self.build_pulsar_packet(self.amplitude,self.period,0,self.flag))
        time.sleep(.5)
        self.set_RS_rx()
        returned_bytes=self.pulser.read(13)
        self.read_pulser_response(returned_bytes)
    def adjust_voltage_and_period(self):
        new_voltage=input('Input new voltage between 1000 and 2000 V: ')
        new_period=input('Input new period between 1000 and 5E5 uS: ')

        self.amplitude=new_voltage
        self.period=new_period

        send_packet=self.build_pulsar_packet(self.amplitude,self.period,1,self.flag)
        print('Sending packet: ',send_packet)
        self.set_RS_tx()
        self.pulser.write(send_packet)
         
        time.sleep(.1)
        self.set_RS_rx()
        returned_bytes=self.pulser.read(13)
        print('Returning packet: ',returned_bytes)
        self.read_pulser_response(returned_bytes)


if __name__=='__main__':
    main()

