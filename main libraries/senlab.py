# ============================================================================
# File Name:        senlab.py
# Author:           Vivek23
# Description:      Load Sensor Data in Python from .csv file
# Dependencies:     Python >= 3.8
#                       - numpy     (pip install numpy)
#                       - scipy     (pip install scipy)
#                       - datetime  (pip install DateTime)
#                       - pandas    (pip install pandas)
#                       - tqdm      (pip install tqdm)
#                       - mavlab    (mavlab.py -> place it in the same folder)
#
# Usage:            Load Sensor Data (from sensor hub)
#
# Requirements:     These definitions are specific to old sensor files; 
#                   Update it based on formated .csv file
# ============================================================================

import pandas as pd
import datetime
import mavlab
import numpy as np
from tqdm import tqdm
from scipy.ndimage import median_filter
from scipy.interpolate import interp1d
from scipy.interpolate import PchipInterpolator


# ---------------------- TRISONICA MINI ----------------------

# load 'sensor data' from a SINGLE sensor-'datafile'(type: string)
def tsm_data_simple(datafile):

    num_lines = sum(1 for line in open(datafile))

    data = pd.read_csv(datafile)
    data = data.replace({0:np.nan})

    with tqdm(total=num_lines, desc="Loading Data from Sensor File\t\t", ncols=98, bar_format='{l_bar}{bar}') as pbar:
        pbar.update(num_lines)

    return data


# load 'sensor data' from MULTIPLE sensor-'datafiles'(type: list of string)
def multiple_tsm_data_simple(datafiles):

    data = []

    for i in tqdm(range(0,len(datafiles)), desc="Loading Data from Sensor Files\t\t", ncols=99, bar_format='{l_bar}{bar}'):
        dt = pd.read_csv(datafiles[i])
        dt = dt.replace({0:np.nan})
        data.append(dt)

    return data


# load 'sensor data' from a SINGLE sensor-'datafile'(type: string)
# 'offset'(type: integer) is the number of datapoint at which flight data and sensor data aligns
# 'length'(type: integer) is the total datapoints for the particular flight data
# MAINLY USED WITH FLIGHT LOG DATA
def tsm_data_offset(datafile,offset,length):

    # EXAMPLE:
    # datafile = '2024_3_25_15_35_44.csv'
    # offset = 455
    # length = len(data['XKF1_0']['PD'])

    num_lines = sum(1 for line in open(datafile))
    data = pd.read_csv(datafile)
    data = data.replace({0:np.nan})
    data = data[offset:offset+length]
    diff = length - len(data)
    if diff > 0:
        dummy_rows = pd.DataFrame(np.nan,index=range(diff),columns=data.columns)
        data = pd.concat([data,dummy_rows],ignore_index = True)
    data = data.reset_index()
    with tqdm(total=num_lines, desc="Loading Data from Sensor File\t\t", ncols=98, bar_format='{l_bar}{bar}') as pbar:
        pbar.update(num_lines)

    return data

# load 'sensor data' from MULTIPLE sensor-'datafiles'(type: string)
# 'offset'(type: list of integer / array) are number of datapoint at which flight data and sensor data aligns
# 'length'(type: list of integer / array) are total datapoints for the particular flight data
# MAINLY USED WITH FLIGHT LOG DATA
def multiple_tsm_data_offset(datafiles,offsets,lengths):

    data = []
    # for i in range(0,len(datafiles)):
    for i in tqdm(range(0,len(datafiles)), desc="Loading Data from Sensor Files\t\t", ncols=99, bar_format='{l_bar}{bar}'):
        dt = pd.read_csv(datafiles[i])
        dt = dt.replace({0:np.nan})
        dt = dt[offsets[i]:offsets[i]+lengths[i]]
        diff = lengths[i] - len(dt)
        if diff > 0:
            # print(diff)
            dummy_rows = pd.DataFrame(np.nan,index=range(diff),columns=dt.columns)
            dt = pd.concat([dt,dummy_rows],ignore_index=True)      
        # diff_2 = lengths[i] - len(dt)
        # print(diff_2)
        dt = dt.reset_index()
        data.append(dt)

    return data



# ---------------------- FT-742 SM ----------------------

# load 'sensor data' from a SINGLE sensor-'datafile'(type: string)
# 'true_sampling_rate'(type: float): observed sampling rate
# 'converted_sampling_rate'(type: float): target sampling rate
# MAINLY USED FOR FT-742 SM SENSOR FILE AND INTERPOLATE DATA TO 10HZ (to align with flight data)

def read_csv_interp(sensorfile,true_sampling_rate,converted_sampling_rate):
    sensordata = pd.read_csv(sensorfile, encoding='unicode_escape')
    labels = ((sensordata.columns[1:4]).tolist() + (sensordata.columns[5:10]).tolist())
    # labels = ((sensordata.columns[1:5]).tolist())

    filtered_data = {}
    # for col in tqdm(labels, desc="Loading Data from Sensor Files\t\t", ncols=99, bar_format='{l_bar}{bar}'):
    for col in labels:
        ws = np.array(sensordata[col])
        filtered_data[col] = median_filter(ws, size=29)

    def custom_interp(data_b, converted_sampling_rate):
        # time_b = np.arange(len(data_b)) / true_sampling_rate
        # df_b = pd.DataFrame({'time': time_b, 'data': data_b})
        # f_interp = interp1d(df_b['time'], df_b['data'], kind='linear', fill_value='extrapolate')
        # time_common = np.arange(len(data_b) * 2) / converted_sampling_rate 
        # data_b_resampled = f_interp(time_common)
        # return np.array(data_b_resampled)

        time_b = np.arange(len(data_b)) / true_sampling_rate

        # Create PCHIP interpolator
        f_interp = PchipInterpolator(time_b, data_b, extrapolate=True)

        # New time axis (as in your original code)
        time_common = np.arange(len(data_b) * 2) / converted_sampling_rate

        data_b_resampled = f_interp(time_common)
        return np.array(data_b_resampled)

    interpolated_data = {}
    for col in labels:
        interpolated_data[col] = custom_interp(filtered_data[col], converted_sampling_rate)

    sensordata = pd.DataFrame(interpolated_data)
    return sensordata





# ---------------------------------------------------------------
# UNDERCROFT
# ---------------------------------------------------------------

def ft_data(sensorfile,datafile):
    data = pd.read_csv(sensorfile,encoding='unicode_escape')
    data = data.loc[:,'Timestamp':'Absolute_altitude_ms5611']
    data = data.to_dict('list')
    ms = []
    for i in range(len(data['Timestamp'])):
        ms.append(str(data['Timestamp'][i]).split(":")[6])
        ms[i] = float(ms[i])

    time = []
    a = (datafile[0:10]) + ' '
    b = (':'.join(str(data['Timestamp'][i]).split(":")[3:6]))
    for i in range(len(data['Timestamp'])):
        # time.append(datetime.datetime.strptime((':'.join(str(data['Timestamp'][i]).split(":")[3:6])), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(microseconds= ms[i]))
        time.append(datetime.datetime.strptime(str(a+b), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(microseconds= ms[i]))
    data['Timestamp'] = time
    # data = data.to_dict('list')

    return data


def tsm_data(file,sensorfile):
    
    sensordata = pd.read_csv(sensorfile)
    sensordata = sensordata.loc[:,'Time Stamp':'Absolute Pressure (MS5611) (hPa)']

    time_s = []
    for i in range(len(sensordata)):
        time_s.append(datetime.datetime.strptime(str(sensordata['Time Stamp'][i]), '%Y_%m_%d_%H_%M_%S'))
    sensordata['Time Stamp'] = time_s

    time = mavlab.timedata_gpscor(file,['AHR2'])
    time_t = time['AHR2']
    for i in range(len(time_t)):
        time_t[i] = time_t[i].replace(microsecond=0)

    n = 1
    for i in range(len(time_t)):
        if time_t[i] == time_t[i+1]:
            n = n + 1
        else:
            a = i + 1
            break

    for i in range(len(sensordata)):
        if sensordata['Time Stamp'][i] == time_t[a]:
            b = i
            # print(b)
            break

    sensordata = sensordata[b-n:b-n+len(time['AHR2'])].reset_index()

    return sensordata

def tsm_data_cor(file,sensorfile,latency,la):
    sensordata = pd.read_csv(sensorfile)
    sensordata = sensordata.loc[:,'Time Stamp':'Absolute Pressure (MS5611) (hPa)']

    time_s = []
    for i in range(len(sensordata)):
        time_s.append(datetime.datetime.strptime(str(sensordata['Time Stamp'][i]), '%Y_%m_%d_%H_%M_%S') + datetime.timedelta(seconds = latency) + datetime.timedelta(milliseconds = la))
    sensordata['Time Stamp'] = np.array(time_s) 

    n1 = sensordata['Time Stamp'][0] + datetime.timedelta(seconds = 1)

    for i in range(len(sensordata)):
        if sensordata['Time Stamp'][i] == n1:
            print(i)
            n = i
            break

    var = 0
    for i in range(n,len(sensordata)):
        time_s[i] = time_s[i] + datetime.timedelta(milliseconds = var)
        var =  var + 100
        if var > 900:
            var = 000

    sensordata['Time Stamp'] = np.array(time_s)

    time = mavlab.timedata_gpscor(file,['AHR2'])
    time_t = time['AHR2']
    for i in range(len(time_t)):
        time_t[i] = time_t[i].replace(microsecond=0)

    n = 1
    for i in range(len(time_t)):
        if time_t[i] == time_t[i+1]:
            n = n + 1
        else:
            a = i + 1
            break

    # print(a,n)

    for i in range(len(sensordata)):
        if sensordata['Time Stamp'][i].replace(microsecond=0) == time_t[a]:
            b = i
            # print(b)
            break

    sensordata = sensordata[b-n:b-n+len(time['AHR2'])].reset_index()

    return sensordata