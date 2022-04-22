from threading import Event
from .thread_utils import OutputFile
from sensors.gps.gps_utils import parse_gga
from datetime import datetime as dt
import time
import logging



    
    
def generate_data_dict(sensors): 
    
    """Creates a dictionary of sensor data from a dictionary of sensors"""
    
    return {k:sensors[k].data for k in sensors}



def generate_telem_dict(data_dict): 
    
    """Creates a dictionary of data to be sent as telemetry"""
    
    
    gps_dict = parse_gga(data_dict['gps'])

    telem_dict = {
        'hhmmss':dt.now(),
        'lat_dec_deg':gps_dict['latitude'],
        'lon_dec_deg':gps_dict['longitude'],
        'lat_dil':gps_dict['hdop'],
        'alt':gps_dict['altitude'],
        'temp1':data_dict['t_internal'],
        'temp2':data_dict['t_external'],
        'pressure':data_dict['pressure'][1]
    }
    
    return telem_dict






def generate_payload_dict(data_dict):
    gps_dict = parse_gga(data_dict['gps'])

    payload_dict = {
        'pressure':data_dict['pressure'][1],
        't_external':data_dict['t_external'],
        'alt': gps_dict['altitude'],
    }

    return payload_dict

def format_payload_data(payload_dict):

    formats = {
        'pressure':'09.04f',
        't_external': '+08.03f',
        'alt': '08.02f'
    }
    return ','.join([format(payload_dict[k],formats[k]) if payload_dict[k] != None else ' ' for k in payload_dict])


def counter(count): 
    return '{0:05}'.format(count)




#------------------------------------------

class HandleTelemetry: 

    """Class to manage the collection and transmission of telemetry data
       
       INPUTS: 
       sensors: dict, a dictionary of sensor objects
       radio: object, a tuppersat radio object """
    def __init__(self, sensors, radio): 

        self._sensors = sensors
        self._radio = radio
        self._data = None


    def setup(self):
        pass

    def teardown(self):
        pass

    def read(self): 
        self._data = generate_data_dict(self._sensors)

    def update(self):
        self.read()
        telemetry_dict = generate_telem_dict(self._data)
        print(telemetry_dict)
        self._radio.send_telemetry_packet(telemetry_dict)
        print("Telemetry Package sent")
        logging.info("Telemetry Packet Sent")
        time.sleep(20)


#-------------------------------------------------

class HandleData:

    """Class to handle the compiling and transmission of payload data"""

    def __init__(self, sensors, radio): 

        self.index = 0
        self._sensors = sensors
        self._radio = radio
        self._data = None


    def setup(self):
        pass

    def teardown(self):
        pass   

    def read(self): 
        self._data = generate_data_dict(self._sensors)

    def update(self):
        data_packet = self.generate_payload_string()
        self._radio.send_data(data_packet)
        self.index+=1
        print("Payload Package sent")
        logging.info("Payload Package Sent")

       
    def generate_payload_string(self):

        """Generates a byte string from compiled payload data"""

        data_list =[]
        #two sets of data
        while len(data_list) < 2:
            self.read()
            payload_dict = generate_payload_dict(self._data)
            data_list.append(format_payload_data(payload_dict))
            time.sleep(10) 
        return ';'.join([counter(self.index),*data_list]).encode()
            



#-------------------------------------------------

class StoreData:

    """Class to store sensor data by writing it to a file using
       the thread-safe OutputFile method""" 

    def __init__(self, sensors, dir, pause = 1): 

        """Initialiser"""

        self.gps_file = None
        self.env_file = None
        self.geiger_file = None
        self.data = None
        self._sensors = sensors
        self._dir = dir
        self.pause = pause

    def setup(self): 

        """Setup step which creates output files for data storage"""
        self.env_file = OutputFile(f'{self._dir}{dt.now():%Y-%m-%d-%H-%M-%S}_enviroment.txt')
        self.gps_file = OutputFile(f'{self._dir}{dt.now():%Y-%m-%d-%H-%M-%S}_gps.txt')
        self.env_file.open()
        self.gps_file.open()


    def teardown(self): 
        """Teardown step which closes any open files"""
        self.env_file.close()
        self.gps_file.close()

    
    def read(self): 
        """Assigns a dictionary of payload data to the sensor attribute"""
        self._data = generate_data_dict(self._sensors)

    def update(self):
        """Updates the class data attribute and writes contents to a file"""        
        self.read()
        write_gps_data(self._data,  self.gps_file)
        write_enviroment_data(self._data,  self.env_file)
        time.sleep(self.pause)


#-----------------------------------------------------
  
def write_gps_data(sensor_dict, file):
    """Writes NMEA GGA sentence to a text file"""

    gga_sentence = sensor_dict['gps']
    if gga_sentence == None:
        gga_sentence = "No GPS"  
    file.writeline(gga_sentence)
    
        

def write_enviroment_data(sensor_dict, file):

    """Compliles enviromental sensor data and writes to a file"""

    env_sensors = [
        sensor_dict['t_external'],
        sensor_dict['t_internal'], 
        sensor_dict['pressure']
    ]
    data= [str(sensor) for sensor in env_sensors] 
    data_str = f"{time.time(): .6f},{','.join(data)}"
    file.writeline(data_str)
     
