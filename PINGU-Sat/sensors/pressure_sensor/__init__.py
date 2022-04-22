from .pressure_utils import ms5611_temp_and_pressure
from .pressure_utils import unpack_constants
import smbus


class PressureSensor: 

    """Sensor class for the pressure sensor"""

    def __init__(self, addr):

        """Initialiser
        
        Input:
            address of smbus e.g. 0x77"""

        self._addr = addr
        
        self._bus = smbus.SMBus(1)

        self._calibration_constants = None
        #tuple with two values for temperature and pressure
        self._data = (None,None)

        self.buffers = {
            'calibration':[0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC],
            'pressure':0x58,
            'temperature':0x48
        }


    def update(self): 
        """Read and update the stored data value"""
        self._data =self.read()

    def read(self): 
        """Read the pressure and temperature values from the sensor"""

        p, t = ms5611_temp_and_pressure(
            self._bus,
            self._addr,
            self._calibration_constants,
            self.buffers['pressure'],
            self.buffers['temperature'])

        return(p,t)

    def setup(self):

        """Setup step which requests and unpacks the 
           calibration constants from the sensor"""

        self._calibration_constants = unpack_constants(
            self._bus,
            self._addr,
            self.buffers['calibration'] 
        )

    def teardown(self):
        #no teardown step for sensor
        pass

    @property
    def data(self):
        return self._data

