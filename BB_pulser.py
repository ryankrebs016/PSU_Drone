from sys import byteorder
import time
import numpy as np
import serial
import Adafruit_BBIO.GPIO as gpio

#call this script when the pi is started up. Then use the switch to turn on pulsing.



def main():
    options='\n 1:turn on pulser without trigger\n 2:turn on pulser with trigger\n 3:Request info \n 4:test ext trigger\n 5:turn off pulser'
    coms=pulser_comms() #initalize pulser comms
    coms.amplitude=1000 #amplitude of pulse in V
    coms.period=5E5 #time between pulses in micro s when using pulser's timing
    try:
        while(1):
            option=input(options='\n 1:turn on pulser without trigger\n 2:turn on pulser with trigger\n 3:Request info \n 4:test ext trigger\n 5:change voltage and amplitude\n 6:turn off pulser\n')
            if(option==1):coms.turn_on(0)
            elif(option==2):coms.turn_on(1)
            elif(option==3):coms.request_info()
            elif(option==4):coms.test_ext_trigger()
            elif(option==5):coms.adjust_voltage_and_period()
            elif(option==6):coms.turn_off()
            time.sleep(1)
    except:
        print("ending code")
        exit()
    print('Voltage set to %s V. Period set to %s uS'%(coms.amplitude,coms.period))
    coms.turn_on(0) #run class function which turns on pulser and enables pulsing
    time.sleep(10)
    coms.turn_off() #shuts off pulsing
    exit() #testing comms to pulser for no
    '''
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
    '''
    

       
#make class for commuication with the pulsers
class pulser_comms():
    def __init__(self):
        
        self.pulser_port='/dev/ttyS1' #define which port to use, in this case serial 0
        self.pulser_baud=115200 #define pulser baud rate. ie frequency in which pi sends out bits
        self.timeout=1
        self.amplitude=1000 #amplidue of pulses
        self.period=100000 #period between pulses
        self.read_write=1 #define read or write bit
        #self.flag='0101' #defines flag bits 'abcd' a=read only vcc error, b=enable pulsing, enable eternal triggering, enable high voltage supply]
        self.flag=0b00000000
        self.pulser=serial.Serial(port=self.pulser_port,baudrate=self.pulser_baud,timeout=self.timeout)
        self.pulser_rx_pin=14
        self.pulser_tx_pin=16
        self.pulser_tg_pin=18
        gpio.setup(self.pulser_rx_pin,gpio.OUT,initial=gpio.high)
        gpio.setup(self.pulser_tx_pin,gpio.OUT,initial=gpio.low)
        gpio.setup(self.pulser_tg_pin,gpio.OUT,initial=gpio.low)

    def set_RS_tx(self):
        gpio.output(self.pulser_rx_pin, gpio.low)
        gpio.output(self.pulser_tx_pin,gpio.low)
    def set_RS_rx(self):
        gpio.output(self.pusler_rx_pin,gpio.high)
        gpio.output(self.pulser_tx_pin,gpio.high)

    #build packet to send to the pulser
    def build_pulsar_packet(self,amplitude,period,read_write,flag):
        
        preamble=0x55 #always the same
        size=0x09 #always the same
        command_code=0x01 #always the same
        io=0b00000000 #defined byte for input or output status
        if(read_write==1):
            io=0b00000001

        
        amp_bits=amplitude.to_bytes(2,byteorder='big')
        per_bits=period.to_bytes(4,byteorder='big')
 
        to_send_dec=[preamble,size,command_code,io,amp_bits[1],amp_bits[0],per_bits[3],per_bits[2],per_bits[1],per_bits[0],flag]
   
        crc_int=self.crc16(to_send_dec,11)
        crc_hex=crc_int.to_bytes(2,byteorder='big')
        to_send_dec.append(crc_hex[1])
        to_send_dec.append(crc_hex[0])

        return to_send_dec #return array which should be used in serial.write()

    def crc16(self,data, no):
        crc = 0xffff
        poly = 0xa001               # Polynomial used for Modbus RS485 applications
        temp = no

        while True:
            crc ^= data[temp - no]        
            print(data[temp-no])
            for i in range(0, 8):
                print(crc)
                if crc & 0x0001:
                    crc = (crc>>1) ^ poly
                else:
                    crc >>= 1           
            no -= 1
            if no == 0:
                break

        return crc & 0xffff


    #read packet returned from the pulser, either after send read command or from the normal response
    def read_pulser_response(self,response): #unpacks data from response and print ampltiude and period to CL

        voltage=int.from_bytes(response[4:5],byteorder='little')
        period=int.from_bytes(response[6:10],byteorder='little')
        flag=response[10]
        print('Amplitude at %s V'%voltage)
        print('Period at %s'%period)
        if(flag==5):print('Pulsing without trigger')
        elif(flag==7):print('Pulsing with trigger')
        elif(flag==0):print('Pulser off')
        else:print('invalid flag ',flag)

    def turn_on(self,ext_trigger):#will be used to turn on pulsing w/ pulser period\
        print('Turning pulser on')
        self.flag=0b00000101
        if(ext_trigger==1):
            self.flag=0b00000111
        
        send_packet=self.build_pulsar_packet(self.amplitude,self.period,1,self.flag)
        print('Sending packet: ',send_packet)

        self.set_RS_tx()
        time.sleep(.1)
        self.pulser.write(send_packet)
         
        time.sleep(.001)
        self.set_RS_rx()
        returned_bytes=self.pulser.read(13)
        print('Returning packet: ',returned_bytes)
        self.read_pulser_response(returned_bytes)
        

    def turn_off(self): #turns off puslsing
        print('Turning pusler off')
        send_packet=self.build_pulsar_packet(self.amplitude,self.period,1,0b00000000)
        print('Sending packet: ',send_packet)
        self.set_RS_tx()
        time.sleep(0.1)
        self.pulser.write(send_packet)
        time.sleep(.001)
        self.set_RS_rx()
        returned_bytes=self.pulser.read(13)
        print('Returning packet: ',returned_bytes)
        self.read_pulser_response(returned_bytes)


    def request_info(self):#sends byte array to request info from the pulser
        print('Requesting info')
        send_packet=self.build_pulsar_packet(self.amplitude,self.period,0,self.flag)
        print('Sending packet: ',send_packet)
        self.set_RS_tx()
        time.sleep(0.1)
        self.pulser.write(send_packet)
        time.sleep(.001)
        self.set_RS_rx()
        returned_bytes=self.pulser.read(13)
        print('Returning packet: ',returned_bytes)
        self.read_pulser_response(returned_bytes)

    def adjust_voltage_and_period(self):

        new_voltage=input('Input new voltage between 1000 and 2000 V: ')
        new_period=input('Input new period between 1000 and 5E5 uS: ')

        self.amplitude=new_voltage
        self.period=new_period

        send_packet=self.build_pulsar_packet(self.amplitude,self.period,1,self.flag)
        print('Sending packet: ',send_packet)
        self.set_RS_tx()
        time.sleep(0.1)
        self.pulser.write(send_packet)
         
        time.sleep(.001)
        self.set_RS_rx()
        returned_bytes=self.pulser.read(13)
        print('Returning packet: ',returned_bytes)
        self.read_pulser_response(returned_bytes)

    def test_ext_trigger(self):

        send_packet=self.build_pulsar_packet(self.amplitude,self.period,1,self.flag)
        print('Sending packet: ',send_packet)
        self.set_RS_tx()
        time.sleep(.1)
        self.pulser.write(send_packet)
         
        time.sleep(.001)
        self.set_RS_rx()
        returned_bytes=self.pulser.read(13)
        print('Returning packet: ',returned_bytes)
        self.read_pulser_response(returned_bytes)

        try:
            while(1):
                gpio.output(self.pulser_tg_pin,gpio.high)
                time.sleep(0.05)
                gpio.output(self.pulser_tg_pin,gpio.low)
                time.sleep(1)
        except:
            print('\n Exit ext trigger loop')


if __name__=='__main__':
    main()

