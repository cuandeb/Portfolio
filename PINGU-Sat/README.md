# PINGU-Sat

The **P**fotzer **IN**vestigation and **G**eiger **U**tilization **Sat**ellite (PINGU-Sat) is a small satellite that is to be flown on a weather balloon with the aim of investigating the profile of ionizing radiation in the stratosphere using a Geiger Muller detector. 

This repository contains the Python code that makes up PINGU-Sat's onboard software system. The repository is structured as follows:
* pingu_main.py 
* sensors
* data_utils 

where *pingu_main* is the main script that is executed for flight operations. *sensors* and *data_utils* are two packages that provide the tools to operate the onboard sensors and handle the data from these sensors respectively. 

## pingu_main 

**pingu_main.py** is PINGU-Sat's main executable script and is the program that runs when PINGU-Sat is booted. It contains a main function that turns on the onboard instruments, sets up the radio, and performs 3 key processes.

- Stores data from each of the sensors in a specific file every second
- Sends a data packet containing housekeeping telemetry data every 20 seconds using the radio 
- Sends a data packet containing housekeeping telemetry data every 20 seconds using the radio 

The script needs configuration, primarily to set up the different serial and w1 bus addresses for the sensors so that they can be accessed by the software. The script also sets up a log file that is used throughout the software to log exceptions and key operationans information. The script can be cleanly terminated with a KeyBoard interrupt or a *sudo shutdown* command.


## Sensors

This package contains a set of sub-packages, each providing a sensor class for each of the onboard sensors. The sensor packages are: 
* **geiger**: Provides a sensor class for the Geiger Muller radiation detector. 
* **temperature**: Provides a sensor class for the two DS18B20 temperature probes (one external, one internal). 
* **pressure**: Provides a sensor class for the MS5611 pressure sensor. 
* **gps**: Provides a sensor class for PINGU-Sat's GPS system 

The output of each of these packages is a single sensor class. For example **gps** provides the class **GpsSensor** which is implemented by the main script. A number of the packages contain modules with functions specifically for the sensors that are not used elsewhere in the software (with the exception of **gps_parser**, a function in the **gps_utils** module that is used in the data handling processes). 

## data_utils

The **data_utils** package provides thread safe process classes that perform the tasks listed above in **pingu_main**. The modules are broken down as follows: 

* **data_handling**: Provides the **HandleTelemetry**, **HandleData**, and **StoreData** classes which are thread safe processes that perform the tasks outlined above. 
* **process_handling**: Provides the **RunSensor** and **RunProcesses** classes which create and start the threads for the sensors and the process classes from **data_handling**. These two classes act as context managers in the main function
* **radio_utils**: Provides the **RunRadio** class that sets up a radio object that is used to transmit data packets
* **thread_utils**: Provides a number of functions used by the other modules in data_utils primarily for thread management and looping class functions. **catch_and_supress** is a context manager used to terminate the main function if it encounters a *KeyboardInterrupt*



