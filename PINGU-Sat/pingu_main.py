#PINGU-Sat Main Script

from data_utils.radio_utils import RunRadio
from data_utils.thread_utils import catch_and_suppress
from data_utils.process_handling import RunSensor, RunProcesses
from sensors.pressure_sensor import PressureSensor
from data_utils.data_handling import HandleTelemetry, StoreData, HandleData
from sensors.temperature_sensor import TemperatureSensor
from sensors.gps import GPSSensor
import logging
import time
from datetime import datetime as dt
from tuppersat.airborne import set_airborne



#-------------------------------
#Logging Details

LOG_DIR = '/home/pi/logs/'
LOG_FILE = f'{LOG_DIR}{dt.now():%Y-%m-%d-%H-%M-%S}.log'
LOG_FILE_test=f'{LOG_DIR}spicylog.log'


FILE_DIR = '/home/pi/logs/' 


#-------------------------------
#Port details

RADIO_PORT = r'/dev/ttyAMA0'
GPS_PORT=r'/dev/ttyACM0'
EXT_ADDRESS=r'/sys/bus/w1/devices/28-00000de90790/w1_slave'
INT_ADDRESS=r'/sys/bus/w1/devices/28-0213132359aa/w1_slave'
BUS_ADDRESS=0x77

#---------------------------------
#Sensor details 

set_airborne(GPS_PORT)


sensors={
	'gps':GPSSensor(GPS_PORT),
	't_internal':TemperatureSensor(INT_ADDRESS),
	't_external':TemperatureSensor(EXT_ADDRESS), 
	'pressure':PressureSensor(BUS_ADDRESS)
}


#---------------------------------

def main():
    
    logging.basicConfig(filename=LOG_FILE, level = logging.INFO,
			format='%(asctime)s %(levelname)s: %(message)s')


    with catch_and_suppress(KeyboardInterrupt):
        with RunSensor(sensors):
            with RunRadio(RADIO_PORT) as radio:
                processes = [
			HandleData(sensors, radio),
			HandleTelemetry(sensors, radio),
			StoreData(sensors,FILE_DIR)
			]
                with RunProcesses(processes):
                    while True: time.sleep(0.1) 


if __name__=="__main__":
    main()
