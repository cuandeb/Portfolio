import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from matplotlib import gridspec
import csv

from numpy import inf as INF

import extraction_utils as extract

PI = np.pi
TWO_PI = np.pi * 2.
INF= np.inf





#####################################################    

def filing(directory):
    """Returns list of filenames from a directory"""
    file_list=extract.files_from_directory(directory)    
    return file_list


def extraction_mca(file_list ,directory, background): 

    """Given a directory, extracts the x-y values of the 
    spectra for the files in this directory.
    Formatted for mca files"""

    xy_values=[]
    for i in file_list:        
        contents=extract.read_data(directory+'/'+i)
        xy_values.append([extract.final_spectrum_mca(contents,background)[0],
                          extract.final_spectrum_mca(contents,background)[1]])
        
                   
    return np.array(xy_values)
    
    
    

def extraction_spe(file_list ,directory, background):

    """Given a directory, extracts the x-y values of the 
    spectra for the files in this directory.
    Formatted for Spe files"""

    xy_values=[]
    for i in file_list:        
        contents=extract.read_data(directory+'/'+i)
        xy_values.append([extract.final_spectrum_spe(contents,background)[0],
                          extract.final_spectrum_spe(contents,background)[1]])
        
                   
    return np.array(xy_values)        


        
def file_junction(file_list ,directory, background, source_box):
    
    """Checks the files extension of input file from 
       file list and then perform appropriate data 
       extraction."""
    
    headings=extract.info_from_files(file_list)
    
    
    if headings[0][1]=='Spe':
        spectra_spe = extraction_spe(file_list ,directory, background)
        _errors = extract.error_prop_spe(file_list ,directory, background)
        _time = extract.time_extraction_spe(file_list, directory, source_box)
        
        return headings, spectra_spe, _errors, _time
    
    elif headings[0][1]=='mca':
        spectra_mca = extraction_mca(file_list, directory, background)
        _errors = extract.error_prop_mca(file_list ,directory, background)
        _time = extract.time_extraction_mca(file_list, directory, source_box)
        return headings, spectra_mca, _errors, _time
    
        
    

def plot_content(path, background, source_box):
    contents=filing(path)
    spectrum=file_junction(contents, path, background, source_box)
    
    return spectrum






###################################################

#This section takes code from Robert Jeffery's instructional guide to 
#using Scipy's 'curve_fit' function


def in_interval(x, xmin=-INF, xmax=INF):
    """Boolean mask with value True for x in [xmin, xmax) ."""
    _x = np.asarray(x)
    return np.logical_and(xmin <= _x, _x < xmax) 

def filter_in_interval(x, y, xmin, xmax):
    """Selects only elements of x and y where xmin <= x < xmax."""
    
    _mask = in_interval(x, xmin, xmax)
    return [np.asarray(x)[_mask] for x in (x, y)]


############################################################

#here the functions used to fitting are defined


def linear(x,a,b):
    return a*x+b
    
def gaussian(x, mu, sig, a):     
    return a * np.exp(-0.5 * (x-mu)**2 / sig**2) / np.sqrt(TWO_PI * sig**2)

def gaussian_line(x, mu, sig, a, m, c):        
    return gaussian(x, mu, sig, a) + linear(x, m, c)


def double_line(x, mu0, sig0, a0, mu1, sig1, a1, m, c):
    return gaussian(x, mu0, sig0, a0) + gaussian(x, mu1, sig1, a1) + linear(x, m, c)

def double_peak(x, mu0, sig0, a0, mu1, sig1, a1):
    return gaussian(x, mu0, sig0, a0) + gaussian(x, mu1, sig1, a1)


###############################################################    
    
    
def fit_model(model, channels, counts, roi, **kwargs):
    
    """Takes input x and y values and fits a given 
       function to the values"""
    
    _channels, _counts = filter_in_interval(channels, counts, *roi)   
    
    opt, cov = curve_fit(model, _channels, _counts, **kwargs)
    return opt, cov


##########################################################

#make estimates of the gaussian parameters
#again the intial estimates are taken from the examples
#given by Robert Jeffrey


def first_moment(x, y):
    return np.sum(x * y) / np.sum(y)
    
def second_moment(x, y):
    x0 = first_moment(x, y)
    return np.sum((x-x0)**2 * y) / np.sum(y)


def slope(x,y):
    
    """Estimates the slope of a linear
       function"""
    
    return (y[-1]-y[0])/(x[-1]-x[0])
   
    
def intercept(x, y, m):
    
    """Estimates the slope of a linear
       function"""    
    
    return y[0]-m*x[0]
    

        
        
def gaussian_initial_estimates(channels, counts):
    
    """Estimates of the three parameters of the gaussian distribution."""
    
    mu0 = first_moment(channels, counts)
    sig0 = np.sqrt(second_moment(channels, counts))
    a0 = np.sum(counts)#
    
    return (mu0, sig0, a0)
    


def gaussian_line_initial_estimates(channels, counts):
    
    """Estimates of the gaussian and line 
       parameters of the gaussian distribution."""
    
    mu0 = first_moment(channels, counts)
    sig0 = np.sqrt(second_moment(channels, counts))
    a0 = np.sum(counts)
    _m = slope(channels,counts)
    _c = intercept(channels,counts,_m)
    
    
    return (mu0, sig0, a0, _m, _c)


def double_line_initial_estimates(channels, counts):
    
    """Estimates of the gaussian and line 
       parameters of the gaussian distribution."""
    
    #split the r.o.i in two and look for 
    #a gaussian in each half
    
    split_list=int(len(channels)/2)
    low_channels=channels[0:split_list]
    high_channels=channels[split_list:-1]
    
    low_counts=counts[0:split_list]
    high_counts=counts[split_list:-1]
    
    
    mu0 = first_moment(low_channels, low_counts)
    sig0 = np.sqrt(second_moment(low_channels, low_counts))
    a0 = np.sum(low_counts)
    
    mu1 = first_moment(high_channels, high_counts)
    sig1 = np.sqrt(second_moment(high_channels, high_counts))
    a1 = np.sum(high_counts)
    
    _m = slope(channels,counts)
    c = intercept(channels,counts,_m)
    
    #I know it's a big function but I'd rather keep
    #the whole model together 
    
    
    return (mu0, sig0, a0, mu1, sig1, a1, _m, c)


def double_peak_initial_estimates(channels, counts):
    
    """Estimates of the gaussian and line 
       parameters of the gaussian distribution."""
    
    #split the r.o.i in two and look for 
    #a gaussian in each half
    
    split_list=int(len(channels)/2)
    low_channels=channels[0:split_list]
    high_channels=channels[split_list:-1]
    
    low_counts=counts[0:split_list]
    high_counts=counts[split_list:-1]
    
    
    mu0 = first_moment(low_channels, low_counts)
    sig0 = np.sqrt(second_moment(low_channels, low_counts))
    a0 = np.sum(low_counts)
    
    mu1 = first_moment(high_channels, high_counts)
    sig1 = np.sqrt(second_moment(high_channels, high_counts))
    a1 = np.sum(high_counts)

    #I know it's a big function but I'd rather keep
    #the whole model together 
    
    
    return (mu0, sig0, a0, mu1, sig1, a1)

##################################################

def format_result(params, opt, cov):
    
    """Display parameter best estimates and uncertainties.
       Uncertainties are taken as the square root of the 
       covariance matrix"""
    
    opt_rounded=[round(i,4) for i in opt]    
    
    err = np.sqrt(np.diag(cov))
    err_rounded=[round(i,4) for i in err]
    
    _lines = (f"{p} = {o} ± {e}" for p, o, e in zip(params, opt_rounded, err_rounded))
    return "\n".join(_lines)




def format_csvlist(headings, counts, time, func, opt, cov, peaks):
    
    """Takes opt, cov determined for fit
       and creates a dictionary containing
       fit info that can be saved to csv"""
    
    err = np.sqrt(np.diag(cov))
    _headings=["source",
               "distance",
               "angle", 
               "model", 
               "sum",
               "time",
               "peaks"               
              ]
              
    data=[headings[0],
          headings[1],
          headings[2],
          func.name, 
          get_sum(counts),
          time,
          peaks
          
         ]
    add_headings=[p for p in func.params]
    add_data=[(o,e) for o,e in zip(opt,err)]
    
    _headings.extend(add_headings)
    data.extend(add_data)          

    return _headings, data 






            
            
####################################################


def make_model(x,y,func, roi, errors):
    
    channels, counts = filter_in_interval(x, y, *roi)
    _errors = filter_in_interval(x, errors, *roi)[1]
    # make initial estimates and round them off
    guess = func.estimates(channels, counts)
    guess_rounded = [round(i,4) for i in guess]
    # show the initial guesses
    print("Estimated Parameters:")
    print("\n".join(f"{p} = {o}" for p, o in zip(func.params, guess_rounded)))   
    # do the fit
    opt, cov = fit_model(func.model, x, y, roi, p0=guess, sigma=_errors, absolute_sigma=True, maxfev=8000)
    # display result
    print("Actual Parameters:")
    print(format_result(func.params, opt, cov))
    return opt, cov


def make_model_no_print(x,y,func,roi,errors):

    # make initial estimates and round them off
    
    channels, counts = filter_in_interval(x, y, *roi)
    _errors = filter_in_interval(x, errors, *roi)[1]
    guess = func.estimates(channels, counts)
    # do the fit
    opt, cov = fit_model(func.model, x, y, roi, p0=guess, sigma=_errors, absolute_sigma=True, maxfev=8000)
    # display result

    return opt, cov



def get_sum(array): 
    return np.sum(array)



def basic_plot(ax, x, y, roi, errors, **kwargs):  
    
    """Plots the basic gamma spectrum
       and formats the ax object"""
    
    ax.scatter(x, y, c='blue', s=5)
    ax.errorbar(x, y, yerr= errors, fmt='.', capsize=0.5)
    format_plot(ax, x, y, roi)   
    
    
    
def plot_model(ax, func, xrange, ps, npoints=1001, **kwargs):
    """Plots a 1d model on an Axes smoothly over xrange."""
    _channels = np.linspace(*xrange, npoints)
    _counts   = func.model(_channels, *ps)
    
    return ax.plot(_channels, _counts, **kwargs)


    

        
    


def plot_components(ax, func, xrange, ps, npoints=1001, **kwargs):
    """Plots the different components of the model seperately"""
    _channels = np.linspace(*xrange, npoints)
    
    if func.name=='gaussian':         
        ax.plot(_channels, gaussian(_channels,*ps), **kwargs) 
        
    elif func.name=='gaussian line': 
        ax.plot(_channels, gaussian(_channels,*ps[0:3]),'r-') 
        ax.plot(_channels, linear(_channels,*ps[3:]), 'g-') 
        
    elif func.name=='double peak': 
        ax.plot(_channels, gaussian(_channels,*ps[0:3]),'r-') 
        ax.plot(_channels, gaussian(_channels,*ps[3:]), 'g-') 
        
    else:
        ax.plot(_channels, gaussian(_channels,*ps[0:3]), 'r-') 
        ax.plot(_channels, gaussian(_channels,*ps[3:6]), 'g-')
        ax.plot(_channels, linear(_channels,*ps[6:]), 'm-')

        
def format_plot(ax, x, y, roi, 
               y_ax='Count Rate'):
    
    """Applys formatting to plot including:
       -setting x and y limits
       -labeling the axis"""
   
    ax.set_ylabel(y_ax)
    
    #define limits using roi for x-axis
    #maxium y-value in roi defines y-axis 
    
    ax.set_xlim(roi[0]-50,roi[1]+50)
    ax.set_ylim(0,max(y[roi[0]:roi[1]])*1.25)      
    ax.grid(True)
    #remove axis labels on shared x-axis
    plt.setp(ax.get_xticklabels(), visible=False)

#############################################

#This section deals with the plotting of the residuals of each 
#fit. There is a different function for formatting the residuals
#plot. 

def residuals(x,y,func,xrange, ps, errors):
    
    """Calculate the residuals of
       the fitted line"""
    
    channels, measured = filter_in_interval(x, y, *xrange)
    _errors = filter_in_interval(x, errors, *xrange)[1]
    
    expected = func.model(channels, *ps)
    return (channels ,measured - expected, _errors)       
    
    
    
    
    
def format_residuals_plot(ax, x, y, roi, 
                          x_ax='Channels', 
                          y_ax='Residuals'):
    
    """Applys formatting to residuals plot    
       including:
       -setting x limit
       -labeling the axis"""
    
    ax.set_xlabel(x_ax)
    ax.set_ylabel(y_ax)
    
    #define limits using roi for x-axis
    #maxium y-value in roi defines y-axis 
    ax.axhline(y=0, linewidth=2, linestyle='--', color='r')
    ax.grid(True)

    
     
    
def plot_residuals(ax, func, xrange, ps, 
                   x, y, errors, gridspec,
                   npoints=1001, **kwargs):    
    
    """Creates an ax object with a plot 
       of the residuals of a fitted curve_fit
       function"""

    ax2 = plt.subplot(gridspec[1], sharex = ax) 
    _channels, _residuals, _errors= residuals(x,y,func,xrange, ps, errors)    
    ax2.scatter(_channels, _residuals, color="blue", s=0.9)
    ax2.errorbar(_channels, _residuals, yerr=_errors, fmt='.', capsize=0.5)    
    format_residuals_plot(ax2, _channels, _residuals, xrange)
    
#########################################

#finally a last few functions that plot the figures and save
#them as png files. The final function combines all the
#above functions to create and save the plots/fit data. 

 
    
def make_title(ax,headings):   
    
    """Creates a plot heading from
       list of raw input info"""
  
    
    title=str("Source:"+headings[0]+
              ", Distance:"+headings[1]+
              ", Angle:"+headings[2])

    ax.set_title(title)

            
def save_pngs(fig, headings, detector):  
    
    """"Saves plots as png files in 
        designated folders. If same 
        plot is being saved, overwrite 
        is enabled to avoid duplication."""
    
    file='_'.join(headings[0:3])
    fig.savefig('Graphs/'+detector+'_plots/'+file+'.png', overwrite=True)
        
        

    
        
def plot_sources(heading, x, y, errors, func, roi, detector):

    """Combines the functions and plots x-y points, 
       fitted model, residuals, errorbars and 
       formats the plot accordingly"""

    gs = gridspec.GridSpec(2, 1, height_ratios=[2.5, 1]) 
    fig = plt.figure(figsize=(12,8)) 
    ax = plt.subplot(gs[0])
    basic_plot(ax,x,y, roi, errors)
    make_title(ax, heading)
    _opt,_cov=make_model(x,y,func,roi, errors)   
    
    #plot the fitted line, fitting functions, residuals
    plot_model(ax, func,roi,_opt,c='k')
    plot_components(ax, func,roi,_opt)
    plot_residuals(ax, func, roi, _opt, x, y, errors, gs)
    #merge the two plots into one and save as png
    plt.subplots_adjust(hspace=.0)
    save_pngs(fig,heading,detector) 
    
    #format_csvlist(heading, func, _opt, _cov)
    #write_to_csv(heading, func, _opt, _cov, detector)
                   
    plt.show() 
    
    
    
def plot_the_gang(source, roi, func, detector): 
    for i in range(len(source[1])): 
        plot_sources(source[0][i][0],
                    source[1][i][0],
                    source[1][i][1],
                    source[2][i],
                    func, 
                    roi, 
                    detector)
        get_sum(source[1][i][1])
        
        
def save_csv(source, roi, peaks ,func, detector):

    """Saves the fit parameters along with other relevent 
    data about the spectrum and source to a csv file """

    csv_file='Fitted_data/'+detector+'/'+peaks+'.csv'    
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        
        for i in range(len(source[1])):
            opt, cov = make_model_no_print(source[1][i][0],source[1][i][1],
                                           func,roi, source[2][i])
            list_data=format_csvlist(source[0][i][0], source[1][i][1],
                                     source[3][i],func, opt, cov, peaks)            

            if i == 0:
                writer.writerow(list_data[0])
                writer.writerow(list_data[1])
            else:
                writer.writerow(list_data[1])

    
def everything(source, roi, peaks, func, detector):
    
    """Executes the plotting function and csv writing function
       for a number of given input parameters"""

    plot_the_gang(source, roi, func, detector)    
    save_csv(source, roi, peaks,func, detector)
    
  

                    
            
