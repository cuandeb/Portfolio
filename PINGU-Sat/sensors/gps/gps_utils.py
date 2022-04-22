from datetime import time
import numpy as np


def split_sentence(gps_str): 
    """Splits comma-delimited string into list of strings"""
    return gps_str.split(',')


def check_long_sign(long_float, cardinal):

    """Changes +/- of longitude based on cardinal value"""

    if cardinal == "W":
        return -1*long_float
    else:
        return long_float


def cardinal(gps_str):
    return split_sentence(gps_str)[5]



def raw_lat(gps_str):

    """Extracts latitude, longitude, and altitude from NMEA sentence    
    ---------------------------------------
        latitude, longitude: dddmm.mmmmmmmm
        altitude: m    
    """
    lat=split_sentence(gps_str)[2]
    if lat == '': 
        return None
    else:
        return lat


def raw_long(gps_str):
    """Returns longitude in ddmm.mmmmmm format"""
    long=split_sentence(gps_str)[4]
    if long == '': 
        return None
    else:
        return long


def alt_from_gps(gps_str):
    alt = split_sentence(gps_str)[9]
    if alt == '': 
        return None
    else:
        return float(alt)


def gps_timestamp(gps_str):
    """Extract NMEA sentence timestamp"""

    raw_time=split_sentence(gps_str)[1]
    if raw_time == '':
        return None
    else:
        return time(int(raw_time[0:2]),
                    int(raw_time[2:4]),
                    int(raw_time[4:6]))


def gps_checksum(gps_str):
    """Extracts checksum from NMEA sentence"""
    return split_sentence(gps_str)[-1]

def ddmm2deg(raw_coord):
    """Convert NMEA coordinates to decimal degrees"""
    if raw_coord==None:
        return None
    else:
        idx=raw_coord.find('.')
        degrees =raw_coord[:idx-2]
        minutes = raw_coord[idx-2:]
        float_degrees = np.array(degrees, dtype = np.float64)
        float_minutes = np.array(minutes, dtype = np.float64)/60
        dec_degrees= float_degrees+float_minutes
        return round(dec_degrees,5)


def hdop_from_gps(gps_str):
    hdop=split_sentence(gps_str)[8]
    if hdop == '':
        return None
    else:
        return float(hdop)


def parse_gga(gps_str):
    fields=(
	'latitude',
	'longitude',
	'altitude',
	'hdop',
	'checksum',
	'sentence',
	'timestamp'
	)
    if gps_str != None:
        gps_data=(
        	ddmm2deg(raw_lat(gps_str)),
        	check_long_sign(ddmm2deg(raw_long(gps_str)),cardinal(gps_str)),
        	alt_from_gps(gps_str),
        	hdop_from_gps(gps_str),
        	gps_checksum(gps_str).strip('\r\n'),
        	gps_str.strip('\r\n'),
        	gps_timestamp(gps_str)
        	)

        return dict(zip(fields, gps_data))

    else: 
        none_list = [None]*len(fields)
        return dict(zip(fields,none_list))
