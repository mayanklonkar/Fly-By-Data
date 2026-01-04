# ============================================================================
# File Name:        flash.py
# Author:           Vivek23
# Description:      Commonly used definitions is stored here
# Dependencies:     Python >= 3.8
#                       - numpy     (pip install numpy)
#                       - scipy     (pip install scipy)
#                       - datetime  (pip install DateTime)
#                       - pandas    (pip install pandas)
# ============================================================================


import numpy as np
import datetime
from scipy.io import loadmat
import pandas as pd

# interpolate sensor data
def interp_data(sensordata,time,data,inter_time,inter_data):

    for k in range(len(sensordata)):
        for i in range(len(list(inter_data[k].keys()))):
            for j in range(len(list(inter_data[k][str(list(inter_data[k].keys())[i])]))):
                a = list(inter_data[k].keys())[i]
                b = list(inter_data[k][str(list(inter_data[k].keys())[i])])[j]
                inter_data[k][a][b],inter_time[k][a] = inter(sensordata[k]['Timestamp'],time[k][a],data[k][a][b])

    return (inter_data,inter_time)


def inter(stime,time,data):
    c = []
    for i in range(len(time)):
        c.append(((time[i])-(datetime.datetime.strptime(str(time[i].date()) + ' 0-0-0','%Y-%m-%d %H-%M-%S'))).total_seconds())

    dn = np.linspace(min(c),max(c),len(stime))
    n_data = np.interp(dn,c,data)

    n_time = []
    for i in range(len(dn)):
        n_time.append(datetime.datetime.strptime(str((str(time[0].date()) + ' ')+('0:0:0')), '%Y-%m-%d %H:%M:%S')+ datetime.timedelta(seconds= dn[i]))

    return n_data,n_time

def label_test(datafile,params):
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


# calculate power using momentum theory for climb velocity
def momentum(alt,vc):
    n = 6
    r = 0.2256
    area = np.pi * r * r
    rho = 1.2256
    w = 8.5
    g = 9.81
    try:
        time = (alt/vc)/3600
    except:
        pass

    sigma = 0.15
    cd0 = 0.01
    Mtip = 0.3
    ipf = 1.2
    Vtip = 330 * 0.33
    omega = Vtip/r
    thrust = (w * g)/n
    vh = np.sqrt(thrust/(2*rho*area))
    rpm = 4000
    rps = rpm/60
    ct = thrust/(rho*rps**2*(2*r)**4)

    k1 = -1.125
    k2 = -1.372
    k3 = -1.718
    k4 = -0.655

    if vc >= 0:
        vi = -0.5 * vc + np.sqrt(0.25*vc*vc + vh*vh)
    elif (vc > -2*vh) and (vc < 0):
        vv = vc/vh
        vi = vh + vh/ipf*( -1.125*vv -1.372*vv**2 -1.718*vv**3 -0.655*vv**4)
        # vi = vh + vh/ipf*( -1.125 -1.372*vv -1.718*vv**2 -0.655*vv**3)
        # vi = (ipf*vh) + vc * (k1 + k2*vv + k3*vv**2 + k4*vv**3)
    else:
        raise Exception(' descent rate is in windmill brake state. code up equation')
    
    p_ind = ipf * thrust * vi
    p_cli = thrust * vc
    p_pro = 0.125 * sigma * cd0 * rho * area * Vtip ** 3
    p_tot = n * (p_ind + p_pro + p_cli)
    e_cons = round(p_tot * time,4)

    return (e_cons,p_tot)


def timedata_gpscor(datafile,params,diff):
    # datafile = '2023-11-28 10-47-30.bin-363701.mat'
    # params = ['AHR2','ATT','BARO_0','BAT_0','GPS_0','IMU_0','MODE','POS','RATE','RCOU','TERR','VIBE_0','XKF1_0']

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
        # time[str(params[i])] = time[str(params[i])] - diff

    for i in range(len(params)):
        time[str(params[i])] = time[str(params[i])] - diff

    return time