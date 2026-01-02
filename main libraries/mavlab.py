# ============================================================================
# File Name:        mavlab.py
# Author:           Vivek23
# Description:      Load Mavlink Data in Python from .mat file
# Dependencies:     Python >= 3.8
#                       - numpy     (pip install numpy)
#                       - scipy     (pip install scipy)
#                       - datetime  (pip install DateTime)
#                       - pandas    (pip install pandas)
#                       - tqdm      (pip install tqdm)
#
# Usage:            After a flight, flight log data can be saved on the system
#                   giving '.bin' file, which can be used to make '.mat' file 
#                   using 'Mission Planner'
#
# Requirements:     Don't change the base '.bin' filename so that you get a 
#                   '.mat' filename as '2023-11-28 10-47-30.bin-363701.mat'
# ============================================================================

from scipy.io import loadmat
import numpy as np
import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
import time


# load 'data' from parameters listed in 'params'(type: list of string elements) from a SINGLE file 'datafile'(type: string)
# all parameters found in a mavlink data are given in a file called 'parameters.html'
def data(datafile,params):
    
    # EXAMPLE:
    # datafile = '2023-11-28 10-47-30.bin-363701.mat'
    # params = ['AHR2','ATT','BARO_0','BAT_0','GPS_0','IMU_0','MODE','POS','RATE','RCOU','TERR','VIBE_0','XKF1_0']

    import warnings
    warnings.filterwarnings('ignore')

    data = loadmat(datafile)

    label = []
    for i in range(len(params)):
        label.append(params[i].split("_")[0] + '_label')

    dt = {}
    for i in tqdm(range(len(params)), desc="Loading Data from Log File\t\t", ncols=95, bar_format='{l_bar}{bar}'):
        dt[str(params[i])] = {}
        for j in range(len(data[str(label[i])])):
            dt[str(params[i])][str(data[str(label[i])][j]).split("'")[1]] = data[str(params[i])][0:len(data[str(params[i])]),j]

    return dt


# load 'data' from parameters listed in 'params'(type: list of string elements) from MULTIPLE files 'datafile'(type: list of string elements)
def multiple_data(datafiles,params):

    # EXAMPLE:
    # datafile = ['2023-11-28 10-47-30.bin-363701.mat', '2023-11-28 10-47-30.bin-363701.mat']
    # params = ['AHR2','ATT','BARO_0','BAT_0','GPS_0','IMU_0','MODE','POS','RATE','RCOU','TERR','VIBE_0','XKF1_0']

    import warnings
    warnings.filterwarnings('ignore')
    
    dtt = []
    
    for i in tqdm(range(0,len(datafiles)), desc="Loading Data from Log Files\t\t", ncols=96, bar_format='{l_bar}{bar}'):
        data = loadmat(datafiles[i])

        label = []
        for i in range(len(params)):
            label.append(params[i].split("_")[0] + '_label')

        dt = {}
        for i in range(len(params)):
            dt[str(params[i])] = {}
            for j in range(len(data[str(label[i])])):
                dt[str(params[i])][str(data[str(label[i])][j]).split("'")[1]] = data[str(params[i])][0:len(data[str(params[i])]),j]
        dtt.append(dt)
    
    return dtt


# load 'timedata' from parameters listed in 'params'(type: list of string elements) from a SINGLE file 'datafile'(type: string)
# def timedata_gpscor(datafile,params):
    
#     # EXAMPLE:
#     # datafile = '2023-11-28 10-47-30.bin-363701.mat'
#     # params = ['AHR2','ATT','BARO_0','BAT_0','GPS_0','IMU_0','MODE','POS','RATE','RCOU','TERR','VIBE_0','XKF1_0']

#     import warnings
#     warnings.filterwarnings('ignore')
    
#     data = loadmat(datafile)

#     flightdatetime = datetime.datetime.strptime(datafile.split("//")[-1][0:19], '%Y-%m-%d %H-%M-%S')
#     missionstarttime = flightdatetime + datetime.timedelta(microseconds=data['AHR2'][0,1])

#     time = {}

#     basedate = datetime.datetime.strptime('1980-01-06','%Y-%m-%d')

#     d1 = basedate + datetime.timedelta(weeks = data['GPS_0'][0,5]) + datetime.timedelta(milliseconds = data['GPS_0'][0,4]) + datetime.timedelta(minutes= 330)
#     d2 = flightdatetime + datetime.timedelta(microseconds = data['AHR2'][0,1])

#     diff = d2 - d1

#     for i in tqdm(range(0,len(params)), desc="Loading Time Data from Log File\t\t", ncols=100, bar_format='{l_bar}{bar}'):
#         time[str(params[i])] = []
#         for j in range(len(data[str(params[i])])):
#             # time[str(params[i])].append(str((missionstarttime + datetime.timedelta(microseconds=data[str(params[i])][j,1])).time()))
#             time[str(params[i])].append((flightdatetime + datetime.timedelta(microseconds=data[str(params[i])][j,1]) - diff))
#         time[str(params[i])] = np.array(time[str(params[i])])

#     return time

def timedata_gpscor(datafile, params):

    import warnings
    warnings.filterwarnings('ignore')

    import os, re, datetime
    import numpy as np
    from scipy.io import loadmat
    from tqdm import tqdm

    data = loadmat(datafile)

    # ---------- Try to get datetime from filename ----------
    fname = os.path.basename(datafile)

    m = re.search(r'\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}', fname)

    if m:
        flightdatetime = datetime.datetime.strptime(
            m.group(), '%Y-%m-%d %H-%M-%S'
        )
    else:
        # ---------- Fallback: use GPS time ----------
        basedate = datetime.datetime.strptime('1980-01-06', '%Y-%m-%d')
        d1 = (basedate
              + datetime.timedelta(weeks=float(data['GPS_0'][0, 5]))
              + datetime.timedelta(milliseconds=float(data['GPS_0'][0, 4]))
              + datetime.timedelta(minutes=330))   # IST offset
        flightdatetime = d1
        print("⚠️ Filename has no timestamp. Using GPS-based start time.")

    # ---------- Mission start from AHR2 ----------
    missionstarttime = flightdatetime + datetime.timedelta(
        microseconds=float(data['AHR2'][0, 1])
    )

    # ---------- GPS vs AHR2 correction ----------
    basedate = datetime.datetime.strptime('1980-01-06', '%Y-%m-%d')

    d1 = (basedate
          + datetime.timedelta(weeks=float(data['GPS_0'][0, 5]))
          + datetime.timedelta(milliseconds=float(data['GPS_0'][0, 4]))
          + datetime.timedelta(minutes=330))

    d2 = flightdatetime + datetime.timedelta(
        microseconds=float(data['AHR2'][0, 1])
    )

    diff = d2 - d1

    # ---------- Build time dictionary ----------
    time = {}

    for i in tqdm(range(len(params)),
                  desc="Loading Time Data from Log File\t\t",
                  ncols=100, bar_format='{l_bar}{bar}'):

        key = str(params[i])
        time[key] = []

        for j in range(len(data[key])):
            t = (flightdatetime
                 + datetime.timedelta(microseconds=float(data[key][j, 1]))
                 - diff)
            time[key].append(t)

        time[key] = np.array(time[key])

    return time



# load 'timedata' from parameters listed in 'params'(type: list of string elements) from MULTIPLE files 'datafile'(type: list of string elements)
def multiple_timedata_gpscor(datafiles,params):

    # EXAMPLE:
    # datafile = ['2023-11-28 10-47-30.bin-363701.mat', '2023-11-28 10-47-30.bin-363701.mat']
    # params = ['AHR2','ATT','BARO_0','BAT_0','GPS_0','IMU_0','MODE','POS','RATE','RCOU','TERR','VIBE_0','XKF1_0']

    import warnings
    warnings.filterwarnings('ignore')

    dt = []
    for i in tqdm(range(0,len(datafiles)), desc="Loading Time Data from Log Files\t", ncols=100, bar_format='{l_bar}{bar}'):
        data = loadmat(datafiles[i])

        flightdatetime = datetime.datetime.strptime(datafiles[i].split("//")[-1][0:19], '%Y-%m-%d %H-%M-%S')
        missionstarttime = flightdatetime + datetime.timedelta(microseconds=data['AHR2'][0,1])

        time = {}

        basedate = datetime.datetime.strptime('1980-01-06','%Y-%m-%d')

        d1 = basedate + datetime.timedelta(weeks = data['GPS_0'][0,5]) + datetime.timedelta(milliseconds = data['GPS_0'][0,4]) + datetime.timedelta(minutes= 330)
        d2 = flightdatetime + datetime.timedelta(microseconds = data['AHR2'][0,1])

        diff = d2 - d1

        for i in range(len(params)):
            time[str(params[i])] = []
            for j in range(len(data[str(params[i])])):
                # time[str(params[i])].append(str((missionstarttime + datetime.timedelta(microseconds=data[str(params[i])][j,1])).time()))
                time[str(params[i])].append((flightdatetime + datetime.timedelta(microseconds=data[str(params[i])][j,1]) - diff))
            time[str(params[i])] = np.array(time[str(params[i])])

        dt.append(time)
    return dt

# gives table of sub-parameters from parameters listed in 'params'(type: list of string elements) from a single file 'datafile'(type: string)
def label(datafile,params):

    # EXAMPLE:
    # datafile = '2023-11-28 10-47-30.bin-363701.mat'
    # params = ['AHR2','ATT','BARO_0','BAT_0','GPS_0','IMU_0','MODE','POS','RATE','RCOU','TERR','VIBE_0','XKF1_0']

    import warnings
    warnings.filterwarnings('ignore')

    data = loadmat(datafile)

    label = []
    for i in range(len(params)):
        label.append(params[i].split("_")[0] + '_label')

    dt = {}
    for i in range(len(params)):
        dt[str(params[i])] = {}
        for j in range(len(data[str(label[i])])):
            dt[str(params[i])][str(data[str(label[i])][j]).split("'")[1]] = data[str(params[i])][0:len(data[str(params[i])]),j]

    lab = {}
    for i in range(len(params)):
        lab[str(params[i])] = list(dt[str(params[i])].keys())

    lab = pd.DataFrame({key: pd.Series(value) for key, value in lab.items()})
    lab = pd.DataFrame.map(lab,lambda x: '' if pd.isna(x) else x)

    return lab

# gives date and time information of a selected datafile -> [flight date and time | flight duration | flight start time | flight end time]
def datetime_info(datafile):

    # datafile = '2023-11-28 10-47-30.bin-363701.mat'
    
    import warnings
    warnings.filterwarnings('ignore')    
    data = loadmat(datafile)

    flightdatetime = datetime.datetime.strptime(datafile[0:19], '%Y-%m-%d %H-%M-%S')
    missionstarttime = flightdatetime + datetime.timedelta(microseconds=data['AHR2'][0,1])
    missionendtime = flightdatetime + datetime.timedelta(microseconds=data['AHR2'][len(data['AHR2'])-1,1])
    missionduration = missionendtime - missionstarttime

    return (flightdatetime,missionduration,missionstarttime,missionendtime)


# ---------------------------------------------------------------
# UNDERCROFT
# ---------------------------------------------------------------

def timedata(datafile,params):

    import warnings
    warnings.filterwarnings('ignore')
    data = loadmat(datafile)

    flightdatetime = datetime.datetime.strptime(datafile[0:19], '%Y-%m-%d %H-%M-%S')
    missionstarttime = flightdatetime + datetime.timedelta(microseconds=data['AHR2'][0,1])

    time = {}

    for i in range(len(params)):
        time[str(params[i])] = []
        for j in range(len(data[str(params[i])])):
            # time[str(params[i])].append(str((missionstarttime + datetime.timedelta(microseconds=data[str(params[i])][j,1])).time()))
            time[str(params[i])].append((flightdatetime + datetime.timedelta(microseconds=data[str(params[i])][j,1])))
        time[str(params[i])] = np.array(time[str(params[i])])

    return time

def label_wd(datafile,params):
    import warnings
    warnings.filterwarnings('ignore')
    data = loadmat(datafile)

    label = []
    for i in range(len(params)):
        label.append(params[i].split("_")[0] + '_label')

    dt = {}
    for i in range(len(params)):
        dt[str(params[i])] = {}
        for j in range(len(data[str(label[i])])):
            dt[str(params[i])][str(data[str(label[i])][j]).split("'")[1]] = data[str(params[i])][0:len(data[str(params[i])]),j]

    lab = {}
    for i in range(len(params)):
        lab[str(params[i])] = list(dt[str(params[i])].keys())

    return lab