import numpy as np
import datetime
import matplotlib.pyplot as plt
from collections import namedtuple
from scipy.optimize import curve_fit
from matplotlib import gridspec
import random
import csv

plt.rcParams["font.family"] = "monospace" #sets the fonts to be used by the plots later on
plt.rcParams.update({'font.size': 14})

PI=np.pi


TOTAL_BGO="Fitted_Data/BGO/total_bgo.csv"
TOTAL_HPGE="Fitted_Data/HPGe/total_hpge.csv"
TOTAL_NAI="Fitted_Data/NaI/total_nai.csv"
TOTAL_CDTE="Fitted_Data/CdTe/total_cdte.csv"

#looks complicated but it's just activity x decay fraction for each peak 
UPSTAIRS_ACTIVITY = {'cs':[459170.*0.851,16989.29*0.851],
                     'am':([441040.*0.024,22052.*0.024],[441040.*0.359,22052.*0.359]),
                     'am1':[441040.*0.024,22052.*0.024],
                     'am2':[441040.*0.359,22052.*0.359],
                     'mid_ba':[400340.*0.3331,19216.32*0.3331],
                     'ba':([400340.*0.6205,19216.32*0.6205],[400340.*0.1833,19216.32*0.1833]),
                     'ba1':([400340.*0.07164,19216.32*0.07164],[400340.*0.1833,19216.32*0.1833]),
                     'ba2':([400340.*0.6205,19216.32*0.6205],[400340.*0.0894,19216.32*0.0894]),
                     'co':([418840.*0.999,7957.96*0.999],[418840.*0.998,7957.96*0.998]),
                     'co1':[418840.*0.999,7957.96*0.999],
                     'co2':[418840.*0.998,7957.96*0.998]}


#if the peak is an x-ray peak, the activity is set to 0
#this allows me to exclude it from later calculations

DOWNSTAIRS_ACTIVITY = {'cs':[412920*0.851,16989.29*0.851],
                       'ka':[0.,0.],
                       'am':([412920*0.024,22052.*0.024],[412920*0.359,22052.*0.359]),
                       'am1':[412920*0.024,22052.*0.024],
                       'am2':[412920*0.359,22052.*0.359], 
                       'ba':([422540*0.1833,19216.32*0.1833],[422540*0.6205,19216.32*0.6205]),
                       'ba1':([422540*0.07164,19216.32*0.07164],[422540*0.1833,19216.32*0.1833]),
                       'ba2':([422540*0.6205,19216.32*0.6205],[422540*0.0894,19216.32*0.0894]),
                       'low_ba':([0.,0],[0.,0]),
                       'low_am':([0.,0.],[0.,0]),
                       'mid_ba':[422540*0.3331,19216.32*0.3331],
                       'co': ([454360.*0.999,7957.96*0.999],[454360.*0.998,7957.96*0.998]),
                       'co1':[454360.*0.999,7957.96*0.999],
                       'co2':[454360.*0.998,7957.96*0.998]}





LAMBDA = {'cs':(7.2811e-10, 7.24e-14),
          'am':(5.0821e-11, 8.23e-14), 
          'ba':(2.0899e-9, 9.94e-12),
          'co':(4.17e-9, 3.96e-13)}


#energy of various peaks in keV
PEAKS={'cs':661.657,
       'ka':32.19,
          'co':(1173.228,1332.501),
          'co1':1173.228,
          'co2':1332.501,
          'ba': (302.8508,356.0129),
          'ba1':(276.4,302.8508),
          'ba2':(356.02,383.8),
          'low_am':(13.81,17.7), 
          'low_ba':(31, 35),
          'mid_ba':81.,
          'am' :(26.3446,59.5412),
          'am1': 26.3446,
          'am2': 59.5412
          }
       



Detector = namedtuple('Detector', ['name','radius', 'length', 'height','distance','face'])

BGO = Detector(name = 'BGO',
              radius = 2.54,
              length = 5.08,
              height = 5.08,
              distance= 10.,
              face = 'circle')


HPGE = Detector(name = 'HPGe',
              radius = 2.4,
              length = 3.7,
              height = 4.8,
              distance = 19.,
              face = 'circle')

NAI = Detector(name = 'NaI',
             radius = 2.54,
             length = 5.08,
             height = 5.08,
             distance= 16.,
             face = 'circle')
                         
CDTE = Detector(name = 'CdTe',
             radius = 0.15,
             length = 0.1,
             height = 0.3,
             distance =10.,
             face = 'square')
                         
                      
############################################################

def activity(t, A, lam): 
    """Returns activity of a source given
    A_0, elapsed time and """
    return A*np.exp(-lam*t)

def read_csv(filename):
    """Takes an input .csv file and
       reads it into a list"""
    with open(filename) as file: 
        csv_reader = csv.reader(file)
        data_list=[line for line in csv_reader]
    return data_list
    
    
def sum_gaussian_line(data):
    """Returns the sum under the peak with associated
       error from data file for a model with 
       a single gaussian peak"""
    A, A_err=data[9].strip('()').split(', ')
    return float(A), float(A_err)

    
def sum_double_gaussian(data):
    """Returns the sum under the peak with associated
       error from data file for a model with 
       two gaussian peaks"""
    A, A_err=data[9].strip('()').split(', ')
    A1, A1_err=data[9].strip('()').split(', ')
    A2, A2_err=data[12].strip('()').split(', ')
    return float(A1), float(A1_err), float(A2), float(A2_err)  



def extract_sum_vals(filename, sources): 
    
    """Filters relevent values from .csv file based on 
       curve fit model. """
    
    _data=read_csv(filename)
    sum_under_peaks=[]    
    for i in range(1,len(_data)): 
        if _data[i][3]=='gaussian line': 
            _A = sum_gaussian_line(_data[i])
            sum_under_peaks.append([_A, _data[i][6], sources[_data[i][6]],
                                    _data[i][5], _data[i][2],PEAKS[_data[i][6]]])
            
            
        elif _data[i][3]=='gaussian':
            _A = sum_gaussian_line(_data[i])
            sum_under_peaks.append([_A, _data[i][6], sources[_data[i][6]],
                                    _data[i][5],_data[i][2],PEAKS[_data[i][6]]])
            
            
        elif _data[i][3]=='double line': 
            _A1 = sum_double_gaussian(_data[i])[0:2]
            _A2 = sum_double_gaussian(_data[i])[2:]
            sum_under_peaks.append([_A1,_data[i][6],sources[_data[i][6]][0],
                                    _data[i][5],_data[i][2],PEAKS[_data[i][6]][0]])
            sum_under_peaks.append([_A2,_data[i][6],sources[_data[i][6]][1],
                                    _data[i][5],_data[i][2],PEAKS[_data[i][6]][1]])
            
        elif _data[i][3]=='double peak': 
            _A1 = sum_double_gaussian(_data[i])[0:2]
            _A2 = sum_double_gaussian(_data[i])[2:]
            sum_under_peaks.append([_A1,_data[i][6],sources[_data[i][6]][0], 
                                    _data[i][5], _data[i][2],PEAKS[_data[i][6]][0]])
            sum_under_peaks.append([_A2,_data[i][6],sources[_data[i][6]][1],
                                    _data[i][5],_data[i][2],PEAKS[_data[i][6]][1]])
    return sum_under_peaks



def sum_list(filename, sources):
    """Takes extracted data and converts to a list
        Excludes lines where Activity=0"""
    x = extract_sum_vals(filename, sources) 
    return [x[i] for i in range(len(x)) if x[i][2][0]!=0]


def organise_sum_values(func):     
    """Organises list of data into columns"""    
    sums=[func[i][0] for i in range(len(func))]
    sources=[func[i][1] for i in range(len(func))]
    source_activity=[func[i][2] for i in range(len(func))]
    times=[func[i][3] for i in range(len(func))]
    angles=[func[i][4] for i in range(len(func))]
    energies=[func[i][5] for i in range(len(func))]
    return sums,sources,source_activity, times, angles, energies




def values_for_plotting(filename, source_box): 
    """Compiles all the values to be plotted"""
    sum_values=sum_list(filename,source_box)
    _sum_values=np.array(organise_sum_values(sum_values))   
    return _sum_values


########################################################################

def activity_mc_sim(act, act_err, lam, lam_err, time, its=10000):    
    """Runs a basic Monte Carlo simulation to determine the mean 
       activity and associated uncertainty for a given source"""
    #find 10000 values for A_0 and λ
    base_act=np.array([np.random.normal(act, act_err) for i in range(its)])
    lam_vals =np.array([np.random.normal(lam, lam_err) for i in range(its)])
    #now we calculate activities with these values of A_0 and lambda
    rand_act = np.array([activity(time, base_act[i], 
                                  lam_vals[i]) for i in range(its)])
    #we take the mean as our value for A and σ as our uncertainty
    return np.mean(rand_act), np.std(rand_act)


def area_under_curve(filename, source_box):
    """Returns area under the peaks from csv file"""
    data=values_for_plotting(filename, source_box)
    return [(data[0][i][0],data[0][i][1]) for i in range(len(data[0]))]

def source_names(filename, source_box):
    """Returns area under the peaks from csv file"""
    data=values_for_plotting(filename, source_box)
    return [data[1][i] for i in range(len(data[0]))]

def source_original_activities(filename, source_box):
    """Returns area under the peaks from csv file"""
    data=values_for_plotting(filename, source_box)
    return [(data[2][i][0],data[2][i][1]) for i in range(len(data[0]))]
             
def detection_times(filename, source_box):
    """Returns detection time from csv file"""
    data=values_for_plotting(filename, source_box)
    return [float(data[3][i]) for i in range(len(data[0]))]

def source_angles(filename, source_box):
    """Returns area under the peaks from csv file"""
    data=values_for_plotting(filename, source_box)
    return [float(data[4][i].strip('Deg')) for i in range(len(data[0]))]

def source_energies(filename, source_box):
    """Returns peak energies from csv file"""
    data=values_for_plotting(filename, source_box)
    return [data[5][i] for i in range(len(data[0]))]


def name_list(filename, source_box):
    """Compiles a list of sources that can be used
       to later find the decay constant"""
    _names = source_names(filename, source_box)
    edited_names=[]
    for i in range(len(_names)): 
        if 'cs' in _names[i]:
            edited_names.append('cs')
        elif 'ka' in _names[i]:
            edited_names.append('cs')
        elif 'am' in _names[i]:
            edited_names.append('am')
        elif 'ba' in _names[i]:
            edited_names.append('ba')            
        elif 'co' in _names[i]:
            edited_names.append('co')
    return edited_names


def get_lambdas(filename, source_box):
    """Extracts decay constants based on input source"""
    _names=name_list(filename, source_box)
    lambda_vals=[LAMBDA[_names[i]] for i in range(len(_names))]
    return lambda_vals   
        
        

def get_activity(filename, source_box):
    """Uses the MC simulation to find the activity
       value for a given source along with associated
       error"""
    act = source_original_activities(filename, source_box)
    time = detection_times(filename, source_box)
    lam = get_lambdas(filename, source_box)
    #run the mc simulation
    activities = [activity_mc_sim(act[i][0], act[i][1], lam[i][0],
                                 lam[i][1], time[i], its=1000) for i in range(len(time))]
    
    return activities
    
    
def error_prop(x, sig_x, y, sig_y):     
    """Returns propagated error added in 
       quadrature for function. """    
    combo = (sig_x/x)**2 + (sig_y/y)**2
    return np.sqrt(combo)*(x/y)

def source_filter(l, cond):
    """Filters list based on condition"""
    return [row for row in l if row[0] == cond]

def get_on_axis(l):
    """Filters list if angle=0Deg"""
    return [row for row in l if row[1] == 0]

def get_abs_eff(filename, source_box): 
    """Calculates absolute efficiency by extracting measured
       area under the peaks and dividing it by the known
       activity of the peak"""    
    detector_counts = area_under_curve(filename, source_box)
    real_counts = get_activity(filename, source_box)
    
    abs_eff = [(detector_counts[i][0]/real_counts[i][0])*100 
               for i in range(len(detector_counts))]
    
    abs_errs = [error_prop(detector_counts[i][0],detector_counts[i][1], 
                           real_counts[i][0],real_counts[i][1])*100 
                           for i in range(len(detector_counts))]
   
    return abs_eff, abs_errs


def compiler(filename, source_box): 
    """Compiles all relevent information extracted
       from file and sorts the data according to angle"""
    _peaks = source_names(filename, source_box)
    _angles = source_angles(filename, source_box)
    _energies = source_energies(filename, source_box)
    abs_eff, abs_errs = get_abs_eff(filename, source_box)
    #zip the coloumns together into list    
    full_list = zip(_peaks, _angles, _energies, abs_eff, abs_errs)
    #sort the list by angle
    return sorted(list(full_list), key=lambda x: x[1])

#################################################################

def convert_to_radian(x):
    """Converts angle in degrees to radian"""
    return x*(PI/180)

def face_geometry_check(detector):
    """Returns True value if input detector has
       a circular face """
    if detector.face == 'circle': 
        return True
    else: 
        return False

def geometric_factor(x,detector):    
    """Calculates the geometric factor for 
       a given detector with input parameters"""
    #x = np.array(x)
    _x=convert_to_radian(x)
    r=detector.radius
    h=detector.height
    l=detector.length
    d=detector.distance  
    if face_geometry_check(detector) == True:
        geo_fact=(PI*r**2/d**2)*np.abs(np.cos(_x))+(2*r*l/d**2)*np.abs(np.sin(_x))
    if face_geometry_check(detector) == False:
        geo_fact=(h**2/d**2)*np.abs(np.cos(_x))+(h*l/d**2)*np.abs(np.sin(_x))
    return  4*PI/geo_fact




def gf_tester(x, detector):    
    """Models the geometric factor over a large 
       number of points"""    
    x_array=np.linspace(x[0],x[-1], 1000)
    geo_array = geometric_factor(x_array, detector)
    return x_array, geo_array



def intrinsic_efficiency(abs_eff,geo_factor):
    """Multiplies absolute efficiency by
       geometric factor """
    return geo_factor*abs_eff


def filter_abs_eff(filename,source_box,source):
    """Returns the geometric factor, intrinisic
       efficiency and associated errors for a given 
       source"""    
    full_set = compiler(filename, source_box)
    filtered = source_filter(full_set, source)    
    angles = [filtered[i][1] for i in range(len(filtered))]    
    abs_eff = [filtered[i][3] for i in range(len(filtered))]
    abs_eff_errs = [filtered[i][4] for i in range(len(filtered))]    
    return angles, abs_eff, abs_eff_errs

def onaxis_abs_eff(filename,source_box,source):
    
    """Returns the geometric factor, intrinisic
       efficiency and associated errors for a given 
       source"""
    
    full_set = compiler(filename, source_box)
    filtered = source_filter(full_set, source)
    on_ax = get_on_axis(filtered)
    angles = [on_ax[i][1] for i in range(len(on_ax))]    
    abs_eff = [on_ax[i][3] for i in range(len(on_ax))]
    abs_eff_errs = [on_ax[i][4] for i in range(len(on_ax))]    
    return angles, abs_eff, abs_eff_errs                                               
                                                     
            
def filter_intrinsic_eff(filename,source_box, detector, source):
    
    """Returns the geometric factor, intrinisic
       efficiency and associated errors for a given 
       source"""
    
    full_set = compiler(filename, source_box)
    filtered = source_filter(full_set, source)    
    angles = [filtered[i][1] for i in range(len(filtered))]
    geo_factor = [geometric_factor(filtered[i][1], detector) for i in range(len(filtered))]
    int_eff = [intrinsic_efficiency(filtered[i][3], geo_factor[i]) for i in range(len(filtered))]
    int_eff_errs = [intrinsic_efficiency(filtered[i][4], geo_factor[i]) for i in range(len(filtered))]
    
    return angles, int_eff, geo_factor, int_eff_errs

def onaxis_intrinsic_eff_full(filename,source_box, detector):
    
    """Returns the geometric factor, intrinisic
       efficiency and associated errors for a given 
       source"""
    
    full_set = compiler(filename, source_box)
     
    on_ax = get_on_axis(full_set)    
    angles = [on_ax[i][1] for i in range(len(on_ax))]
    geo_factor = [geometric_factor(on_ax[i][1], detector) for i in range(len(on_ax))]
    int_eff = [intrinsic_efficiency(on_ax[i][3], geo_factor[i]) for i in range(len(on_ax))]
    int_eff_errs = [intrinsic_efficiency(on_ax[i][4], geo_factor[i]) for i in range(len(on_ax))]
    energies = [on_ax[i][2] for i in range(len(on_ax))]
    
    return angles, int_eff, geo_factor, int_eff_errs, energies


def onaxis_intrinsic_eff_filtered(filename,source_box, detector, source):
    
    """Returns the geometric factor, intrinisic
       efficiency and associated errors for a given 
       source"""
    
    full_set = compiler(filename, source_box)
    filtered = source_filter(full_set, source) 
    on_ax = get_on_axis(filtered)    
    angles = [on_ax[i][1] for i in range(len(on_ax))]
    geo_factor = [geometric_factor(on_ax[i][1], detector) for i in range(len(on_ax))]
    int_eff = [intrinsic_efficiency(on_ax[i][3], geo_factor[i]) for i in range(len(on_ax))]
    int_eff_errs = [intrinsic_efficiency(on_ax[i][4], geo_factor[i]) for i in range(len(on_ax))]
    energies = [on_ax[i][2] for i in range(len(on_ax))]
    
    return angles, int_eff, geo_factor, int_eff_errs, energies
               
                                                
                                                     
def energy_eff(x, a, b, c): 
    """Function to fit energy vs efficiency"""
    return a*(np.log(x))**2 + b*np.log(x) + c


####################################################


def basic_line(ax, x, y, err_y, color, **kwargs): 
    ax.plot(x,y, color+'-', alpha = 0.5,**kwargs)
    ax.errorbar(x,y, yerr = err_y, fmt=color+'.',
                alpha=1,capsize=2, **kwargs)
    
    
def format_plot(ax,
                x_ax,
                y_ax):    
    ax.set_xlabel(x_ax)
    ax.set_ylabel(y_ax)
    ax.grid(True) 



def three_plots(filename, source_box, detector, source):
    onax_abs=onaxis_abs_eff(filename,source_box,source)
    onax_int=onaxis_intrinsic_eff_filtered(filename,source_box, detector, source)
    e_abs = filter_abs_eff(filename, source_box, source)
    e_int = filter_intrinsic_eff(filename, source_box, detector, source)
    geo = gf_tester(e_abs[0],detector)
    return e_abs, geo, e_int, onax_abs, onax_int  


def compare_sources(filename, source_box, detector, source1, source2, source3): 
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, sharex=True, figsize=(8,10))
    s1 = three_plots(filename, source_box, detector, source1)
    s2 = three_plots(filename, source_box, detector, source2)
    s3 = three_plots(filename, source_box, detector, source3)
    basic_line(ax1,s1[0][0], s1[0][1], s1[0][2], 'b',label=source1)
    basic_line(ax2,s1[1][0], s1[1][1], None, 'r')
    basic_line(ax3,s1[2][0], s1[2][1], s1[2][3],'b')
    basic_line(ax1,s2[0][0], s2[0][1], s2[0][2], 'r', label=source2)
    basic_line(ax3,s2[2][0], s2[2][1], s2[2][3],'r')
    basic_line(ax1,s3[0][0], s3[0][1], s3[0][2], 'g',label=source3 )
    basic_line(ax3,s3[2][0], s3[2][1], s3[2][3],'g')
    format_plot(ax1,r'Angle ($^{\circ}$)',r'$\epsilon_{Abs} (\%)$')
    format_plot(ax2,r'Angle ($^{\circ}$)',r'Geometric Factor')
    format_plot(ax3,r'Angle ($^{\circ}$)',r'$\epsilon_{Int} (\%)$')
    plt.subplots_adjust(hspace=.0)
    plt.savefig(detector.name+'_offaxis.png')

    

def final_source_efficiencies(det_name):
    if det_name=='BGO':
        compare_sources(TOTAL_BGO, DOWNSTAIRS_ACTIVITY, BGO, 'am2', 'mid_ba', 'co')
    elif det_name=='HPGe':
        compare_sources(TOTAL_HPGE, UPSTAIRS_ACTIVITY, HPGE, 'am2', 'cs', 'co2')
    elif det_name=='NaI':
        compare_sources(TOTAL_NAI, DOWNSTAIRS_ACTIVITY, NAI, 'am2', 'mid_ba', 'cs') 
    elif det_name=='CdTe':
        compare_sources(TOTAL_CDTE, DOWNSTAIRS_ACTIVITY, CDTE, 'am1', 'am2', 'mid_ba') 
        
        
        
def normalised_eff(filename, source_box, detector, source):
    
    onax_int=onaxis_intrinsic_eff_filtered(filename,source_box, detector, source)
    e_int = filter_intrinsic_eff(filename, source_box, detector, source)
    
    normal = np.array(e_int[1])/onax_int[1]
    normal_errs = np.array(e_int[3])/onax_int[1]
    
    return e_int[0], normal, normal_errs




def off_ax_comparison():
    am2_normal_bgo = normalised_eff(TOTAL_BGO, DOWNSTAIRS_ACTIVITY, BGO, 'am2')
    am2_normal_hpge = normalised_eff(TOTAL_HPGE, UPSTAIRS_ACTIVITY, HPGE, 'am2')
    am2_normal_nai = normalised_eff(TOTAL_NAI, DOWNSTAIRS_ACTIVITY, NAI, 'am2')
    am2_normal_cdte = normalised_eff(TOTAL_CDTE, DOWNSTAIRS_ACTIVITY, CDTE, 'am2')
    fig, ax = plt.subplots(figsize=(12,8))    
    ax.plot(am2_normal_bgo[0],am2_normal_bgo[1],'r.-',alpha=0.5,label='BGO')
    ax.plot(am2_normal_cdte[0],am2_normal_cdte[1],'bx-',alpha=0.5,label='CdTe')
    ax.plot(am2_normal_hpge[0],am2_normal_hpge[1],'g^-',alpha=0.5, label='HPGe')
    ax.plot(am2_normal_nai[0],am2_normal_nai[1],'ks-',alpha=0.5, label='NaI')
    ax.errorbar(am2_normal_bgo[0],am2_normal_bgo[1],yerr=am2_normal_bgo[2],fmt='r.',capsize=2)
    ax.errorbar(am2_normal_cdte[0],am2_normal_cdte[1],yerr=am2_normal_cdte[2],fmt='b.',capsize=2)
    ax.errorbar(am2_normal_hpge[0],am2_normal_hpge[1],yerr=am2_normal_hpge[2], fmt='g.',capsize=2)
    ax.errorbar(am2_normal_nai[0],am2_normal_nai[1],yerr=am2_normal_nai[2],fmt='k.',capsize=2)
    ax.grid(True)
    ax.legend(loc='best')
    ax.set_xlabel(r'Angle ($^{\circ}$)')
    ax.set_ylabel(r'$\epsilon_{int}(\theta)/\epsilon_{int}(0^{\circ})$')
    plt.savefig('total_offaxis.png')
    

def format_log_plot(ax, 
                    x_ax="Peak Energy (keV)",
                    y_ax=r"$\ln(\epsilon_{int})$"):
    
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_xlabel(x_ax)
    ax.set_ylabel(y_ax)
    ax.set_ylim(1,5)
    #ax.set_xlim(50,1300)
    ax.grid(True, which="both")
    ax.legend(loc='best')
    

def basic_scatter(ax, x, y, err_y, **kwargs): 
    ax.scatter(x,y,s=5, **kwargs)
    ax.errorbar(x,y,yerr=err_y, fmt='.', capsize=2, **kwargs) 
    
def make_model(func, x, y, y_err, **kwargs): 
    opt, cov = curve_fit(func, x, y, sigma = y_err, absolute_sigma=True)
    return opt, cov
    
def plot_log_model(ax, func, x, y, ps, **kwargs): 
    _x=np.logspace(1.2,3.2,1000)
    _y=func(_x, *ps)
    ax.plot(_x,_y,'-',**kwargs)

def comparison_plot(ax, filename, source_box, detector, colour):
    on_ax = onaxis_intrinsic_eff_full(filename,source_box, detector)
    _x=on_ax[4]    
    _y=np.log(on_ax[1])
    _y_err=(np.array(on_ax[3])/np.array(on_ax[1]))    
    basic_scatter(ax, _x, _y, _y_err, c=colour)
    _opt,_cov = make_model(energy_eff, _x, _y, _y_err)
    plot_log_model(ax, energy_eff, _x, _y, _opt, c=colour, label=detector.name)
    format_log_plot(ax)
    print(list(zip(on_ax[4],on_ax[1])))
    
def combine(): 
    fig, ax = plt.subplots(figsize=(12,8))
    comparison_plot(ax, TOTAL_BGO, DOWNSTAIRS_ACTIVITY, BGO, 'r')
    comparison_plot(ax, TOTAL_HPGE, UPSTAIRS_ACTIVITY, HPGE, 'g')
    comparison_plot(ax, TOTAL_NAI, DOWNSTAIRS_ACTIVITY, NAI, 'k')
    comparison_plot(ax, TOTAL_CDTE, DOWNSTAIRS_ACTIVITY, CDTE, 'b')
    plt.savefig('efficiency_comparison.png')
    
