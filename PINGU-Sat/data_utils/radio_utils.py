import serial
from tuppersat.radio import SatRadio


class RunRadio: 

    """Thread safe radio process class"""

    def __init__(self, port):

        """Initialiser.
        
        Input:
            Serial port address of the radio"""

        self._port = {
            'port': port,
            'baudrate': 38400,
            'timeout':2
        }

        self.radio_settings={
            'address': 0x53,
            'callsign': 'PINGUSAT'
        }
        
        self._serial=None
        self.radio = None


    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.teardown()

    def setup(self):

        """Setup step which
            -Opens the serial port provided as an argument
            -Creates the radio object using the serial port
            - """
        self._serial=serial.Serial(**self._port)
        self.radio = SatRadio(self._serial,**self.radio_settings)
        self.radio.start()

    def send_data(self,msg):
        self.radio.send_data_packet(msg)

    def send_telemetry_packet(self, dictionary):
         self.radio.send_telemetry(**dictionary)

    def teardown(self): 
        self.radio.stop()
        self._serial.close()

    def loop(self):
        pass
