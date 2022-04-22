import logging
import time

def check_sign(temp_float):
    
    """Appends +/- to string temperature value"""
    
    if temp_float >= 0: 
        return str("+")+str(temp_float)
    else:
        return str("-")+str(temp_float)


def read_ds18b20(filepath):
    """Read DS18B20 temperature as  float"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
        equals_pos = lines[1].find('t=')
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string)/1000.0
        return temp_c

###############################

class TemperatureSensor:

    """Class for the DS18B20 sensor"""

    def __init__(self, filepath):

        self.filepath = filepath

        self._data = None 

    def update(self):

        """Update the class data attribute by calling the read function"""

        try:
            self._data = self.read()

        except (FileNotFoundError, IndexError) as exc:
            logging.info(f'Temperature Sensor - {type(exc).__name__}')
            self._data = None
            #pause for 5 seconds before trying again
            time.sleep(1)
            pass

    def read(self): 
        """Read temperature values from specific file"""
        temperature = read_ds18b20(self.filepath)
        return temperature

    #no setup needed, the file constantly updates
    def setup(self):
        #log the startup
        logging.info('Temperature Sensor Started')
        pass

    #no teardown needed
    def teardown(self):
        logging.info('Temperature Sensor Shutdown')
        pass

    @property
    def data(self):
        return self._data
