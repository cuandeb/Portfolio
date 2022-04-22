from threading import Event
from .thread_utils import start_threads, stop_threads, sensor_thread, process_thread
import time



class RunSensor: 
    
    def __init__(self, sensor_dict):

        self._sensor_dict = sensor_dict

        self._stop_event = Event()
        self.threads = [sensor_thread(self._sensor_dict[k], self._stop_event) for k in self._sensor_dict]
        self.pause = 1


    def __enter__(self): 
        self.setup()

    def __exit__(self, exc_type, exc_value, traceback): 
        self.teardown()

    def setup(self): 
        start_threads(self.threads)

    def teardown(self): 
        stop_threads(self._stop_event, self.threads)

    def loop(self):
        pass


#----------------------------------------------------

class RunProcesses: 

    def __init__(self, processes):

        self._processes = processes
        self._stop_event = Event()
        self.threads = [process_thread(process, self._stop_event) for process in self._processes]


    def __enter__(self):
        self.setup()
        return self

    def __exit__(self,exc_type,exc_value, traceback):
        self.teardown()

    def setup(self):
        start_threads(self.threads)        

    def teardown(self): 
        stop_threads(self._stop_event,self.threads)

    def loop(self):
        pass

    def update(self):
        pass
    

