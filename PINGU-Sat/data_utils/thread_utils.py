import queue
import threading
import time
from queue import Queue
import contextlib


#-------------------------------------------

@contextlib.contextmanager
def catch_and_suppress(*exc,callback=None):
    """Context manager to suppress specified exception types"""
    try:
        yield

    except exc as e:
        if callback:
            callback(e)

    return
#--------------------------------------------

def repeat(target, condition = None): 
    
    """Repeat target indefinitely, or until condition met
    
    Inputs:
        target: callable
            the function to be run on repeat
            
        condition: callable [optional]
            a function whose result is used to determine if the next
            iteration of the loop continues.
    """

    while (True if condition is None else condition()):
        target()
        

def run(loop, setup=None, teardown=None, keep_running=None): 
    
    """Initialises a sensor class with setup, loop, teardown steps"""
    
    if setup:
        setup()
    try: 
        repeat(loop, keep_running)
        
    finally:
        if teardown: 
            teardown()
        


def loop(sensor):
    
    """Updates a sensor class attribute when included in a loop"""
    
    def _loop():
        sensor.update()
        print(f"{time.time(): .6f} : {sensor._data}")
        time.sleep(2)
    return _loop 

#------------------------------------------

class LoopThread(threading.Thread):
    """Execute function in an infinite loop with optional setup/teardown"""
    def __init__(self, loop, setup=None, teardown=None):

        self._stop_event = threading.Event()

        self._loop = loop 
        self._setup = setup 
        self._teardown = teardown

        super().__init__() #allows us to use the properties of this class in subclasses

    def run(self): 
        self.setup()
        try: 
            while self.is_running():
                self.loop()

        finally: 
            self.teardown()

    def setup(self):
        if self._setup: 
            self._setup()
    
    def teardown(self): 
        if self._teardown:
            self._teardown()

    def loop(self):
        self._loop()

    def is_running(self):
        return not self._stop_event.is_set()
        
    def stop(self):
        """Terminate the looped thread's execution."""
        self._stop_event.set()
        self.join()

    def __enter__(self): 
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        return False

#----------------------------------------------

class ConsumerThread(LoopThread):
    """Waits for item in a queue and consumes them"""
    def __init__(self, queue, func, timeout): 
        self.queue = queue
        self._func = func
        self._timeout = timeout

        super().__init__(loop=None)

    def loop(self):
        consume(self.queue, self._func, self._timeout)

def consume(q, func, timeout=None):

    try:
        item = q.get(timeout=timeout)

    except queue.Empty:
        pass

    else:
        func(item)


#--------------------------------------------

class ProducerThread(LoopThread):
    """Produces items and adds them to a Queue."""
    def __init__(self, queue, func):
        self.queue = queue
        self._func = func

        super().__init__(loop=None)

    def loop(self):
        produce(self.queue, self._func)



def produce(q, func):
    """Tries to create a new item and add it to a Queue for later use."""
    item = func()
    if item:
        q.put(item)


#----------------------------------------------

class OutputFile:
    """A thread-safe file output."""
    def __init__(self, filename, mode='w', buffering=1, encoding=None,
                 timeout=1):
        """Initialiser.
        ==========
        Parameters
        ==========
        filename, mode, buffering, encoding are passed to the built-in open.
        timeout is passed to ConsumerThread
        """
        # file arguments
        self._filename  = filename
        self._mode      = mode
        self._buffering = buffering
        self._encoding  = encoding
        
        # consumer thread arguments
        self._timeout  = timeout
        
        self._queue = Queue()

    def __repr__(self):
        return f'OutputFile({self._filename}, mode={self._mode})'        

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
        
    def open(self):
        self._file = open(
            self._filename             ,
            mode      = self._mode     ,
            buffering = self._buffering,
            encoding  = self._encoding ,
        )

        self._thread = ConsumerThread(
            queue   = self._queue        ,
            func    = self._write_to_file,
            timeout = self._timeout      ,
        )
        self._thread.start()

    def close(self):
        self._thread.stop()
        self._file.close()


    def _write_to_file(self, msg):
        """Internal method to write to file."""
        self._file.write(msg)

    def write(self, msg):
        """Write string to file.
        Internally, this uses a Queue to ensure thread-safety.
        """
        self._queue.put(msg)

    def writeline(self, msg, newline='\n'):
        """Write string to file with newline termination.
        Internally, this uses a Queue to ensure thread-safety.
        """
        self.write(msg+newline)


#--------------------------------------------------------

def loop_thread(loop, stop_event, setup=None, teardown=None):

    def keep_running():
        return not stop_event.is_set()

    return threading.Thread(
        target=run,
        args=(loop, setup, teardown, keep_running)
    )

def sensor_thread(sensor,stop_event):
    
    return loop_thread(
        loop=sensor.update,
        setup=sensor.setup,
        teardown=sensor.teardown, 
        stop_event=stop_event
    )

def process_thread(process, stop_event): 
    return loop_thread(
        loop = process.update,
        setup = process.setup, 
        teardown = process.teardown,
        stop_event = stop_event
    )


def radio_thread(radio,stop_event):
    
    return loop_thread(
        loop=radio.update,
        setup=radio.setup,
        teardown=radio.teardown, 
        stop_event=stop_event
    )



##########################################

def start_threads(threads): 

    """Starts threads from a list of threads"""

    for thread in threads:
        thread.start()

def stop_threads(event,threads): 

    event.set()

    for thread in threads:
        thread.join()


