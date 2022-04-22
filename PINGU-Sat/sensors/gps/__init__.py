import serial
import time
import logging


############################

def check_sentence(sentence, gps_id):
    
    """Returns True if sentence matches sentence ID"""

    if sentence[3:6] == gps_id:
        return True

#############################

class GPSSensor:

    """Sensor class for the GPS sensor"""
    
    def __init__(self, port):

        """Initializer"""

        self.serial = None
        self._data = None
        self.id = 'GGA'
        self.serial_details = {
            'baud':9600,
            'port': port,
            'timeout':1            
        }
        
    def update(self):
        try: 
            self._data = self.read()
        
        except serial.SerialException:
            self._data = None
            logging.info('SerialException for GPS')
            time.sleep(5)
            pass
        
    def setup(self):
        self.serial = serial.Serial(self.serial_details['port'],
                                    self.serial_details['baud'])
        
    def read(self): 
        while True:
            sentence = self.serial.readline().decode('ascii')
     
            if check_sentence(sentence, self.id):

                return sentence.strip('\r\n')
    
          
    def teardown(self):
        self.serial.close()
           
    @property
    def data(self): 
        return self._data
