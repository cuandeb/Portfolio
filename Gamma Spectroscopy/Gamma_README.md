# Gamma Spectroscopy 

This is the largest programming project I have undertaken to this point. The project was part
of the "Space Detector Lab" module in my Space Science masters. The goal of the project was
to analyse and characterise a set of four gamma radiation detectors through the construction 
of an analysis pipeline. This was the first experience I had with basic software development and full "start-to-finish" 
analysis pipelines. 

The four detectors all output their data in the form of .SPE files which included basic information about the date and time
of recording, as well as a dataset of counts for given energies. Using this information the detectors can be 
calibrated, and their performance analysed. Key performance metrics included energy resolution, detector efficiency and off-axis response
to radiation. 

To perform this analysis I wrote a number of Python scripts which were adapted into basic software packages that could be run in Jupyter notebooks. 
These packages make up the *Analysis* repository. The *Detector Results* repository contains notebooks (which run these packages) for each detector with the results of the 
analysis including plots, values, and uncertainties. 

Overall this is a project that really made me rethink my style of programming into a far more functional, "industry-friendly" style of programming. 

## Analysis
### extraction_utils

This script contains functions necessary to load a set of data files in SPE format and perform the required tasks to extract and prepare the data for curve fitting. 
These functions include: 

- Loading the files and reading the data to lists.
- Extracting the datetime information and the energy count data and storing them accordingly. 
- Normalising the radiation data from counts to count rate. 
- Calculating the uncertainties for these count rates. 
- Loading and preparing background rates with associated uncertainties. 

These functions were the base of all following analysis as they formatted the data and prepared it in a way that would be easier to analysis in the following steps. 

### curvefit_utils

The script takes the prepared data, plots it as a histogram and performs adaptive curve fitting to the function. The main function of this script was to 
fit some form of modified gaussian curve to the data using a method of least squares fit to the data. These compound functions could be: 

- A single gaussian curve
- A product of two overlapping gaussians
- Two overlapping gaussians with additional polynomial componants to account for noise

The above functions were fit to the data depending on detector type, radioactive source, and regions of interest defined in the histogram. 
Once fitted, the fit parameters of each plot were saved to a CSV file with associated uncertainties and relevent information about count rates, source type and detector. 


### calibration_resolution 

This script performs the detector calibration process which essentially consists of comparing the known energy of radioactive sources with those measured by the detector. The aim is to 
create a sort of translation function that can take the values measured by the detector and convert them to the actual energies. Once calibrated we can determine the energy resolution 
which is a measurement of how accurately the detector can measure radiation energies. 
To accomplish this *calibration_resolution* contains functions to: 

- Extract the on-axis fitted data.
- Fit a quadratic or linear model to the measured vs. real energies.
- Use the model to create a real energy scale for the detector. 
- Measure the Full-Width-Half-Maximum of the energy peaks with this adapted scale. 
- Plot the FWHM of the energy peaks vs energy for each detector


### efficiency 

This final script measures how much radiation is being detected by the instruments and analyses their off-axis response to radiation. 

To perform these functions the script needed to 

- Calculate the actual decay rate and count rate of the radioactive sources at the time of measurement
- Determine the measured count rate based on the source by measuring the counts under the fitted gaussian curve
- Express the ratio between these values as percentage and plot over the measured energies 
- Determine a basic geometric model of the detector that can be used to model off-axis response
- Plot the efficiencies (on-axis and off-axis) of the four detectors together to compare and contrast performance. 


## Detector Notebooks

The notebooks in this repository use the modules detailed above to deliver the performance characteristics of each detector. 
This includes: 

- Plots of the energies measured by the detectors with fitted curves and residuals included
- A calibration plot/function for each detector 
- Energy resolution vs. Energy 
- On-axis absolute and intrinsic efficiency
- Off-axis efficiency response

There is a notebook for each detector which contains these values and a final comparison notebook which shows comparitive plots of the detectors' performance. 


 






