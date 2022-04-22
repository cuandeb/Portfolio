import smbus
import time

def unpack(buffer):
    _buffer = reversed(bytearray(buffer))
    return sum(_byte << (_i*8) for _i, _byte in enumerate(_buffer))


def unpack_constants(_bus, _addr, constant_address):
    """establishes constants for calibration"""
    byte_list=[_bus.read_i2c_block_data(_addr,i,2) for i in constant_address]
    constant_list=[unpack(i) for i in byte_list]
    none_buffer=[None]
    return none_buffer+constant_list

def read_adc(bus,bus_address, adc_address):
    """Request data from a specfic address and output the value as integer"""
    bus.write_byte(bus_address, adc_address)
    time.sleep(0.05)
    #read requested data from registry address 0x00
    adc_bytes = bus.read_i2c_block_data(bus_address, 0x00, 3)
    return unpack(adc_bytes)


def calibrated_temp(constant_list, temp_adc): 
    """Returns calibrated temp"""
    c = constant_list 
    dT=temp_adc-(c[5]*(2**8))
    return 2000+dT*(c[6])/(2**23)

def calibrated_pressure(constant_list, pressure_adc, temp_adc):
    c=constant_list
    dT=temp_adc-c[5]*(2**8)
    _off = c[2]*(2**16) + (dT*c[4])/(2**7)
    _sens = c[1]*(2**15) + (c[3]*dT)/(2**8)
    return ((pressure_adc*_sens)/(2**21) - _off)/(2**15)

def ms5611_temp_and_pressure(bus, bus_address, constants, pressure_adc, temperature_adc): 
    D = [read_adc(bus,bus_address, pressure_adc),
         read_adc(bus,bus_address, temperature_adc)]
    temperature = calibrated_temp(constants, D[0])/100.00
    pressure = calibrated_pressure(constants, D[1] ,D[0])/100.00
    return(temperature, pressure)
