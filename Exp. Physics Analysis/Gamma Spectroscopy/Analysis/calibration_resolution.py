import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from collections import namedtuple

plt.rcParams["font.family"] = "monospace" #sets the fonts to be used by the plots later on
plt.rcParams.update({'font.size': 14})

#known energy peaks for calibration 
PEAKS={'cs':661.657,
       'co':(1173.228,1332.501),
       'co1':1173.228,
       'co2':1332.501,
       'ba': (302.8508,356.0129),
       'ba1':(276.4,302.8508),
       'ba2':(356.02,383.8),
       'low_am':(13.81,17.7), 
       'low_ba':(31, 35),
       'mid_ba':80.997,
       'am' :(26.3446,59.5412),
       'am1': 26.3446,
       'am2': 59.5412,
       'ka':32.19}

LINEAR_PARAMS = ('m', 'c')
QUAD_PARAMS = ('a', 'b', 'c')

TOTAL_HPGE="Fitted_Data/HPGe/total_hpge.csv"
TOTAL_BGO="Fitted_Data/BGO/total_bgo.csv"
TOTAL_NAI="Fitted_Data/NaI/total_nai.csv"
TOTAL_CDTE="Fitted_Data/CdTe/total_cdte.csv"


##################################################

#This first section deals with extracting the data from the
#csv file containing all the gamma peak info

def read_csv(filename):    
    with open(filename) as file: 
        csv_reader = csv.reader(file)
        data_list=[line for line in csv_reader]
    return data_list
    
#the following functions extract the fit parameters based on 
#what model was used to fit them
    
def mean_gaussian_line(data):
    """Extracts mu from list of data"""
    mu, mu_err=data[7].strip('()').split(', ')
    return float(mu), float(mu_err)

    
def mean_double_gaussian(data):
    """Extracts mu from list of data"""
    mu1, mu1_err=data[7].strip('()').split(', ')
    mu2, mu2_err=data[10].strip('()').split(', ')
    return float(mu1), float(mu1_err), float(mu2), float(mu2_err)  


def sig_gaussian_line(data):
    """Extracts sigma from list of data"""
    sig, sig_err=data[8].strip('()').split(', ')
    return float(sig), float(sig_err)

    
def sig_double_gaussian(data):
    """Extracts sigma from list of data"""
    sig1, sig1_err=data[8].strip('()').split(', ')
    sig2, sig2_err=data[11].strip('()').split(', ')
    return float(sig1), float(sig1_err), float(sig2), float(sig2_err)  




def extract_mean_calib(filename): 
    """Extracts centroid position of peak and 
       associated uncertainty depending on
       model used to fit peak"""
    _data=read_csv(filename)
    mean_energy=[]
    
    for i in range(1,len(_data)-1): 

        if _data[i][3]=='gaussian line' and _data[i][2]=='0Deg': 
            _mu = mean_gaussian_line(_data[i])
            mean_energy.append([_mu, PEAKS[_data[i][6]]])
            
        elif _data[i][3]=='gaussian' and _data[i][2]=='0Deg': 
            _mu = mean_gaussian_line(_data[i])            
            mean_energy.append([_mu, PEAKS[_data[i][6]]])
            
            
        elif _data[i][3]=='double line' and _data[i][2]=='0Deg': 
            _mu1 = mean_double_gaussian(_data[i])[0:2]
            _mu2 = mean_double_gaussian(_data[i])[2:]
            mean_energy.append([_mu1, PEAKS[_data[i][6]][0]])
            mean_energy.append([_mu2, PEAKS[_data[i][6]][1]])
            
        elif _data[i][3]=='double peak' and _data[i][2]=='0Deg': 
            _mu1 = mean_double_gaussian(_data[i])[0:2]
            _mu2 = mean_double_gaussian(_data[i])[2:]
            mean_energy.append([_mu1, PEAKS[_data[i][6]][0]])
            mean_energy.append([_mu2, PEAKS[_data[i][6]][1]])
    return mean_energy


def extract_sig_calib(filename): 
    """Extracts standard deviation of peak and 
       associated uncertainty depending on
       model used to fit peak"""
    _data=read_csv(filename)
    sig_vals=[]
    
    for i in range(1,len(_data)-1):
        if _data[i][3]=='gaussian line' and _data[i][2]=='0Deg': 
            _sig=sig_gaussian_line(_data[i])
            sig_vals.append([_sig, PEAKS[_data[i][6]]])
            
        elif _data[i][3]=='gaussian' and _data[i][2]=='0Deg': 
            _sig=sig_gaussian_line(_data[i])  
            sig_vals.append([_sig, PEAKS[_data[i][6]]])
           
        elif _data[i][3]=='double line' and _data[i][2]=='0Deg': 
            _sig1 = sig_double_gaussian(_data[i])[0:2]
            _sig2 = sig_double_gaussian(_data[i])[2:]
            sig_vals.append([_sig1, PEAKS[_data[i][6]][0]])
            sig_vals.append([_sig2, PEAKS[_data[i][6]][1]])
            
        elif _data[i][3]=='double peak' and _data[i][2]=='0Deg': 
            _sig1 = sig_double_gaussian(_data[i])[0:2]
            _sig2 = sig_double_gaussian(_data[i])[2:]
            sig_vals.append([_sig1, PEAKS[_data[i][6]][0]])
            sig_vals.append([_sig2, PEAKS[_data[i][6]][1]])
    return sig_vals


def extract_energy_values(func):     
    """Arranges extracted data into columns"""
    channels=[func[i][0][0] for i in range(len(func))]
    errors=[func[i][0][1] for i in range(len(func))]
    actual_energy=[func[i][1] for i in range(len(func))]
    return channels, actual_energy, errors


def values_for_calibration(filename):
    sig_calib_values=extract_sig_calib(filename)
    mean_calib_values=extract_mean_calib(filename)
    sig_values_final=np.array(extract_energy_values(sig_calib_values))
    mean_values_final=np.array(extract_energy_values(mean_calib_values))    
    return mean_values_final, sig_values_final

######################################################################

def quad(x,a,b,c): 
    return a*x**2+b*x+c

def linear(x,a,b): 
    return a*x+b


def fit_model(model, x, y, **kwargs):   
    """Takes input x and y values and fits a given 
       function to the values"""     
    opt, cov = curve_fit(model, x, y, **kwargs)
    return opt, cov


def make_model(x,y,func,errors):
    """Fits a line of best fit to x-y data
       and prints the parameters and 
       uncertainties"""
    opt, cov = fit_model(func.model, x, y, sigma=errors, absolute_sigma=True)
    # display result
    print("Parameters:")
    print(format_result(LINEAR_PARAMS, opt, cov))
    return opt, cov


def basic_plot(ax, x, y, errors, colour='b', **kwargs):     
    """Plots x-y data as a scatterplot 
       and formats the ax object"""   
    ax.scatter(x, y, s=5, **kwargs)
    ax.errorbar(x, y, yerr= errors, fmt='.', capsize=0.5)
    format_plot(ax, x, y)  


def basic_log_plot(ax, x, y, errors, **kwargs):  
    
    """Plots x-y data as a scatterplot 
       and formats the ax object as 
       a log-log plot"""
    
    ax.scatter(x, y, s=5,**kwargs)
    ax.errorbar(x, y, yerr= errors, fmt='.', capsize=2, **kwargs)
    format_log_plot(ax, x, y)   
    
    
    
def plot_model(ax, func, x, ps, npoints=1001, colour='r',**kwargs):
    """Plots a fitted model smoothly over
       a desired linear range."""
    _x = np.linspace(0,np.max(x)+50, npoints)
    _y = func(_x, *ps)
    return ax.plot(_x, _y, '-',**kwargs)



def plot_log_model(ax, func, ps, npoints=1001, **kwargs):
    """Plots a fitted model smoothly
       over a desired logarithmic range."""
    x = np.logspace(1.2,3.2, npoints)
    y = func(x, *ps)   
    return ax.plot(x, y, '-' ,**kwargs)


        
def format_plot(ax, x, y, 
               x_ax='Energy (keV)', 
               y_ax='Channel (arb.)'):
    
    """Applys formatting to plot including:
       -setting x and y limits
       -labeling the axis"""
   
    ax.set_xlabel(x_ax)
    ax.set_ylabel(y_ax)
    
    #define limits using roi for x-axis
    #maxium y-value in roi defines y-axis 
    
    ax.set_xlim(0,np.max(x)+50)
    ax.set_ylim(0,max(y)*1.1)   
    
    ax.grid(True)
    
    
def format_log_plot(ax,x,y,
                    x_ax='Energy (keV)', 
                    y_ax='Spectral Resolution (%)'):
    
    """Applys formatting to plot including:
       -setting x and y limits
       -labeling the axis"""
       
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(x_ax)
    ax.set_ylabel(y_ax)    
    ax.grid(True, which='both')
    
def add_legend(ax):
    """Adds legend to axis if needed"""
    ax.legend(loc='best')

def fit_model(model, x, y, **kwargs):    
    """Takes input x and y values and fits a given 
       function to the values"""        
    opt, cov = curve_fit(model, x, y, **kwargs)
    return opt, cov


def format_result(params, opt, cov):    
    """Display parameter best estimates and uncertainties.
       Uncertainties are taken as the square root of the 
       covariance matrix"""     
    err = np.sqrt(np.diag(cov))    
    _lines = (f"{p} = {o} ± {e}" for p, o, e in zip(params, opt, err))
    return "\n".join(_lines)   
    
    
def make_model(func,x, y, errors, params=LINEAR_PARAMS):
    """Performs a curve_fit on """

    opt, cov = fit_model(func, x, y, sigma=errors, absolute_sigma=True)
    # display result
    print("Parameters:")
    print(format_result(params, opt, cov))
    return opt, cov



def save_plots(filename, fig, description): 
    
    """Saves the plots as a png with a description
        of the plotted information """
    
    title=(filename.replace('total',description)).strip('.csv')
    fig.savefig(title+'.png', overwrite=True)
    
   

def calibration_plot(filename, **kwargs): 
    
    """Combines previous functions to extract values of mu
       from input file, plot them, and return a calibration
       function"""
    #extract data 
    fits=values_for_calibration(filename)
    #perform curve_fit
    _opt, _cov = make_model(linear,fits[0][1],fits[0][0], fits[0][2])  
    #plot data and fitted model
    _fig, _ax= plt.subplots(1, figsize=(10,8))
    basic_plot(_ax, fits[0][1], fits[0][0], fits[0][2], **kwargs)
    format_plot(_ax, fits[0][1], fits[0][0])
    plot_model(_ax, linear, fits[0][1],_opt, npoints=1001, c='r', **kwargs)
    save_plots(filename, _fig, 'calibration')
    plt.show()
    
##############################################################################

#The next portion of code takes the calibration function and 
#uses it to find the spectral resolution and energy    


def calibration_func(filename, uncalibrated): 
    
    """Takes uncalibrated channel list and converts to 
       energy values"""
    
    fits = values_for_calibration(filename)
    _opt, _cov = make_model(fits[0][1],fits[0][0], linear, fits[0][2])
    calibrated = invert_func(uncalibrated, _opt)
    return calibrated
    


def invert_range(x,opt):     
    """Takes channel range and converts it to energy
       based on pre-determined calibration function """    
    return x/opt[0]

def invert_func(x,opt):     
    """Takes channel range and converts it to energy
       based on pre-determined calibration function """    
    return (x-opt[1])/opt[0]


def FWHM(sig): 
    """Returns FWHM for peak given the standard
       deviation of the peak """
    return 2.355*sig
    
    
def FWHM_list(sig_list):
    """Returns list of FWHM for a list
       of input sigmas"""
    return [FWHM(i) for i in sig_list]

def res_curve(x, a, b, c):  
    """Models the relationship between energy 
       and spectral resolution """
    result= a*(x**-2)+b*(x**-1)+c    
    return np.sqrt(result)


def error_prop_res(sig, opt, cov): 
    """Returns propagated error for the calibration
       parameters and sigma"""
    _err=np.sqrt(np.diag(cov))
    _sig_err=sig[2]
    return np.sqrt((_err[0]/opt[0])**2+(_err[1]/opt[1])**2+(_sig_err/sig[0])**2)
    
    

def resolution_curve(sig, opt):
    """"""
    real_sig=invert_range(sig[0],opt)
    spec_res=FWHM(real_sig)
    return sig[1], spec_res
    

def spectral_res(filename): 
    """Uses calibration paramaters to determine the
    energy values for the """    
    means, sigs= values_for_calibration(filename)
    _opt, _cov = fit_model(means[1],means[0], linear, means[2])
    _real_sigs=resolution_curve(sigs, _opt)
    _spectral_res=(_real_sigs[1]/_real_sigs[0])*100
    _spec_err=error_prop_res(sigs,_opt,_cov)
    return sigs[1], _spectral_res, _spec_err


def display_resolution(filename):
    """Format and return resolution with associated 
       errors for a given energy"""
    energies, resolution, uncertainty=spectral_res(filename)
    _lines = (f" Resolution = {r} ± {u} at {e} keV" 
              for e, r, u in zip(energies, resolution, uncertainty))
    return "\n".join(_lines)   



def format_csvlist(filename):
    
    """Takes opt, cov determined for fit
       and creates a dictionary containing
       fit info that can be saved to csv"""
    
    energies, resolution, uncertainty=spectral_res(filename)
    headings=["Energy",
               "Resolution",
               "Uncertainty"               
              ]
              
    data=[energies, 
          resolution,
          uncertainty          
         ]
    
    return headings, data 

    
    
def save_csv(filename):
    """Saves formatted calibration and spectral data
       in a csv file"""
    headings, data = format_csvlist(filename)
    
    new_file = filename.strip('.csv')
    csv_file=new_file+'_resolution.csv' 
    print(data[0])
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file) 
        writer.writerow(headings)
        for i in range(len(data[0])):
            writer.writerow([round(data[0][i],3),
                             round(data[1][i],3),
                             round(data[2][i],3)])
            
def specres_model(_ax, filename, colour, det_name, **kwargs):
    """Calculates and fits the spectral resolution of a detector.
       The fitted spectral resolution-energy relationship is then 
       plotted."""    
    data=spectral_res(filename)
    _opt, _cov = fit_model(res_curve,data[0],data[1],
                           sigma=data[2], absolute_sigma=True)
    basic_log_plot(_ax, data[0], data[1], data[2],c=colour, **kwargs)
    plot_log_model(_ax, res_curve, _opt, c=colour, label=det_name)
    add_legend(_ax)
                
            
            

def make_specres_model(filename, **kwargs):
    data=spectral_res(filename)
    print("Resolutions:")
    print(display_resolution(filename))
    _opt, _cov = make_model(res_curve, data[0], data[1], data[2], QUAD_PARAMS)    
    _fig, _ax = plt.subplots(1, figsize=(10,8))
    basic_log_plot(_ax, data[0], data[1], data[2], **kwargs)
    plot_log_model(_ax, res_curve, _opt, c='r')
    save_plots(filename, _fig, 'resolution')
    save_csv(filename)

    

def total_calibration_spec(filename): 
    """Plots a calibration curve from an input data file
       and uses the calibration parameters to determine
       the fit and plot the spectral resolution energy 
       relation"""
    calibration_plot(filename)
    make_specres_model(filename)


