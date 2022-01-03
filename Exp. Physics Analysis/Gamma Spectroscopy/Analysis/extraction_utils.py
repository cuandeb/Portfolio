import os
import numpy as np
import datetime


##################################

 

def extract_data(gamma_data):
    
    '''Extracts information about the run
       from file names.
       Returns list of info and file 
       extensions.'''   
    
    info = gamma_data.split('.')    
    return info[0].split('_'), info[1]


def info_from_files(file_list):
    
    '''Takes input list of files and returns
       list with extracted information about 
       each file e.g. Source, Angle, Distance'''  
    
    return [extract_data(i) for i in file_list]



def read_data(gamma_data): 
    
    '''Takes input .txt file, opens and
       reads content line by line'''
    
    with open(gamma_data, "r") as gd:
        lines=gd.readlines()    
        return lines




def data_limits_spe(txt_lines):  
     
    """Takes input file and returns the starting
       point and number of channels"""
    
    line_number=0
    for line in txt_lines: 
        line_number += 1
        if "$DATA:" in line: 
            bounds=txt_lines[line_number].strip('\n')
            _bounds=bounds.split(' ')
            upper_lim=int(_bounds[1])
            return line_number,upper_lim
        
        
        
        
        
def mca_channels(txt_lines):
    
    """Extracts number of channels
       with spectrum information 
       from .mca files"""
    
    for line in txt_lines:
        if 'MCAC=' in line: 
            _split_line=line.split(';')
            channel_num=_split_line[0].split('=')
            channels=int(channel_num[1])
    return channels



def extract_datetime_mca(txt_lines):
    
    """Extracts the date and time the spectrum was 
       recorded and returns a datetime object"""
    
    for line in txt_lines: 
        if "START_TIME" in line: 
            time=line.split('-')
            formatted_time=(time[1].strip('\n')).strip()
            date_time_obj = datetime.datetime.strptime(formatted_time,
                                                       '%m/%d/%Y %H:%M:%S')
            return date_time_obj 
  

    
def extract_datetime_spe(txt_lines):
    
    """Extracts the date and time the spectrum was 
       recorded and returns a datetime object"""
    
    line_number=0
    for line in txt_lines: 
        line_number += 1
        if "$DATE_MEA:" in line:
            time=txt_lines[line_number].strip('\n')
            date_time_obj = datetime.datetime.strptime(time, '%m/%d/%Y %H:%M:%S')
            return date_time_obj 
    
    
    
def extract_time_spe(txt_lines):
    
    """Reads through lines of txt and 
       extracts live time from Spe
       file."""
    
    line_number=0
    for line in txt_lines: 
        line_number += 1
        if "$MEAS_TIM:" in line:
            times=txt_lines[line_number].strip('\n')
            live,real=times.split(' ')
            return float(live)
        

def extract_time_mca(txt_lines): 
    
    """Reads through lines of txt and 
       extracts live time from 
       mca file. """
    
    for line in txt_lines: 
        if "REAL_TIME" in line: 
            times=line.split('-')
            return float(times[1])
        
        
def filter_data_mca(txt_lines):  
     
    """Returns a a channel number list and 
       count list based on the channel numbers 
       established using mca_channels()."""
    
    channel_number=mca_channels(txt_lines)
    
    line_number=0
    for line in txt_lines:
        line_number += 1
        if '<<DATA>>' in line:
            break            
     
    _channels=[x for x in range(channel_number)]
    _counts=[float(line) for line in txt_lines[line_number:line_number+channel_number]]
    
    return _channels, _counts               

       
    
def filter_data_spe(txt_lines):
    
    """Uses the limits defined by 
       data_limits() to extract 
       data from file"""
     
    start_line,upper_lim=data_limits_spe(txt_lines)
    x_ax=[float(x) for x in range(upper_lim)]
    y_ax=[float(line) for line in txt_lines[start_line+1:start_line+upper_lim+1]]
    
    return x_ax, y_ax
            
            
def convert_to_countrate_spe(txt_lines):
    
    """Converts a list of raw counts to 
       an array ofcount rate by dividing
       the by detector live time extracted 
       using the extract_time_spe() function."""    
    
    raw_data=filter_data_spe(txt_lines)[1]
    count_rate=[i/extract_time_spe(txt_lines) for i in raw_data]
    raw_channels=[float(x) for x in range(len(raw_data))]
    return raw_channels, count_rate


            
def convert_to_countrate_mca(txt_lines):
    
    """Converts a list of raw counts to 
       an array ofcount rate by dividing
       the by detector live time extracted 
       using the extract_time_mca() function."""    
    
    raw_data=filter_data_mca(txt_lines)[1]
    count_rate=[i/extract_time_mca(txt_lines) for i in raw_data]
    raw_channels=[float(x) for x in range(len(raw_data))]
    return raw_channels, count_rate    
    
    

def files_from_directory(directory):
    
    '''Takes the files from an input directory
       and returns the file names as strings 
       in a list'''
       
    for filename in os.listdir(directory):
        if filename.endswith('.Spe') or filename.endswith('.mca'):
            files=[filename for filename in os.listdir(directory)]            
    return files     


def info_from_files(file_list):
    
    '''Takes input list of files and returns
       list with extracted information about 
       each file e.g. Source, Angle, Distance'''  
    
    return [extract_data(i) for i in file_list]


def background_count_spe(bg):
    
    """Takes input background file and
       returns array of background count rates
       for each channel"""   
    
    bg_data=read_data(bg)
    bg_channel, bg_counts = convert_to_countrate_spe(bg_data)
    return bg_counts

def background_count_mca(bg):
    
    """Takes input background file and
       returns array of background count rates
       for each channel"""   
    
    bg_data=read_data(bg)
    bg_channel, bg_counts = convert_to_countrate_mca(bg_data)
    return bg_counts

def final_spectrum_spe(txt_lines, bg):
    
    """Returns the detector channels 
       and the background subtracted 
       count rates """
    
    bg_count=background_count_spe(bg)
    source_count= convert_to_countrate_spe(txt_lines)
    positive=[max(0, source_count[1][i]-bg_count[i]) for i in range(len(source_count[0]))]
    return source_count[0], positive


def final_spectrum_mca(txt_lines, bg):
    
    """Returns the detector channels 
       and the background subtracted 
       count rates """
    
    bg_count=background_count_mca(bg)
    source_count= convert_to_countrate_mca(txt_lines)
    positive=[max(0, source_count[1][i]-bg_count[i]) for i in range(len(source_count[0]))]
    return source_count[0], positive




def error_prop_spe(file_list,directory,background):
    
    """Performs error propagation given both 
       detector counts and background counts.       
       The max(1,x) function ensures there
       are no uncertainties equaling 0"""    
    
    _background=read_data(background)
    bg_channels, bg_counts=filter_data_spe(_background)
    bg_time=extract_time_spe(_background)
    
    errors=[]
    
    for i in file_list:
        _spectrum=read_data(directory+'/'+i)
        _live_time=extract_time_spe(_spectrum)
        _channels, _counts=filter_data_spe(_spectrum)
        
        error=[np.sqrt((np.sqrt(max(1,_counts[j]))/_live_time)**2+
                       (np.sqrt(max(1,bg_counts[j]))/bg_time)**2)
                        for j in range(len(_counts))]
        errors.append(error)
        
    return np.array(errors)


def error_prop_mca(file_list,directory,background):
    
    """Performs error propagation given both 
       detector counts and background counts.       
       The max(1,x) function ensures there
       are no uncertainties equaling 0"""    
    
    _background=read_data(background)
    bg_channels, bg_counts=filter_data_mca(_background)
    bg_time=extract_time_mca(_background)
    
    errors=[]
    
    for i in file_list:
        _spectrum=read_data(directory+'/'+i)
        _live_time=extract_time_mca(_spectrum)
        _channels, _counts=filter_data_mca(_spectrum)
        
        error=[np.sqrt((np.sqrt(max(1,_counts[j]))/_live_time)**2+
                       (np.sqrt(max(1,bg_counts[j]))/bg_time)**2)
                        for j in range(len(_counts))]
        errors.append(error)
        
    return np.array(errors)


    
def datetime_difference(dt1, dt2):     
    """Returns the difference between 
       two datetime objects in seconds
       as a float"""    
    return (dt2-dt1).total_seconds()    




def time_in_seconds_spe(filename,source_box):
    
    """Gives the elapsed time in seconds
       between the original source activity 
       and the measured activity """
    
    _lines=read_data(filename)
    recording_date=extract_datetime_spe(_lines)
    seconds_elapsed=datetime_difference(source_box, recording_date)
    return seconds_elapsed
    

    
    
def time_extraction_spe(file_list ,directory, source_box):
    times=[]
    for i in file_list: 
        contents=directory+'/'+i
        times.append(time_in_seconds_spe(contents,source_box))
        
    return times


def time_in_seconds_mca(filename,source_box):
    
    """Gives the elapsed time in seconds
       between the original source activity 
       and the measured activity """
    
    _lines=read_data(filename)
    recording_date=extract_datetime_mca(_lines)
    seconds_elapsed=datetime_difference(source_box, recording_date)
    return seconds_elapsed   

    
    
def time_extraction_mca(file_list ,directory, source_box):
    times=[]
    for i in file_list: 
        contents=directory+'/'+i
        times.append(time_in_seconds_mca(contents,source_box))
        
    return times