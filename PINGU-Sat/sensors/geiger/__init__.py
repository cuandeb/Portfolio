import serial


def create_geiger_dict(data_list):

    """Generates a dictionary from a list of data strings"""

    return {
        'CPS':int(data_list[1]),
        'CPM':int(data_list[3]),
        'Dose':float(data_list[5]),
        'Mode':str(data_list[6])
    }
    

def parse_geiger(data_string):

    """Returns a dictionary of Geiger data from an input string
    
    Input: 
        A string of format: CPS, #####, CPM, #####, uSv/hr, ###.##, SLOW
        
    Output:
        Dictionary of Geiger data"""

    sep_vals = data_string.split(',')
    return create_geiger_dict(sep_vals)


def sum_queue(_queue):
    sum_list =[_queue.pop() for _ in range(10)]
    return sum(sum_list)


class RadiationSensor: 

    """Sensor class for the onboard Geiger Counter"""

    def __init__(self, port): 

        """Initializer
        
        Input: 
            Serial port address of sensor"""

        self.serial = None
        self._data = [None, 0]
        self._queue = [],
        self.serial_details = {
            'baud':9600,
            'port': port,
            'timeout':1
            
        }

    def update(self):
        val=self.read()
        self._data[0]=val
        self._queue.append(val)
        if len(self._queue) >= 10:
            self._data[1] = sum(self._queue)
            self._queue = []
        
        
    def setup(self):

        """Setup step that creates and opens serial port"""

        self.serial = serial.Serial(self.serial_details['port'],
                                    self.serial_details['baud'])

    
    def read(self): 
        while True:
            sentence = self.serial.readline().decode('ascii')
            return parse_geiger(sentence)['CPS']

          
    def teardown(self):
        self.serial.close()
           
    @property
    def data(self): 
        return self._data