import struct
import time
import numpy as np
from script import pulser_comms

amplitude=1500
print(amplitude,'V')
period=10000
print(period,'uS')

preamble=0x55


size=0x09
command_code=0x01
io=0b00000001
comms=pulser_comms()




amp_bits=comms.convert_voltage_to_dec(amplitude)

per_bits=comms.convert_period_to_dec(period)

flag=0b00000110



a=['b','b','b','b','2b','4b','b']
code='bbbbHIb'


to_send=struct.pack(code,preamble,size,command_code,io,amp_bits,per_bits,flag)

print('sending this packet',to_send)
rec=struct.unpack(code,to_send)
print(comms.convert_dec_to_voltage(rec[4]),'V')
print(comms.convert_dec_to_period(rec[5]),'uS')