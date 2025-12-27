#--------------------------------------
# Filename: script.py
# Description: Sample script to load multiple cases from excel and plot ascent wind profiles over time
# Dependencies: numpy, pandas, matplotlib, mavlab, senlab
# Instructions: Change paths as per your folder structure
# User Input: Specify rows from excel (Flights) to process
# Example : "24" or "1-5" for single or range of rows
#--------------------------------------



import os,sys
cwd = os.path.dirname(__file__) # current working directory
sys.path.append(os.path.join(cwd, "../../main libraries"))
import mavlab
import senlab
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import yaml
from matplotlib.backends.backend_pdf import PdfPages

import matplotlib
font={'family':'serif','size':15}
matplotlib.rc('font',**font)

# read in input yaml file
with open('inputs.yaml', 'r') as file:
    input_file = yaml.safe_load(file)

inputs = input_file['Inputs']

# path relative to the current working directory to the sens and log folders
sen_path = os.path.join(cwd,inputs['path']['sen_path']) #'Processed sensor files')
log_path = os.path.join(cwd,inputs['path']['log_path']) #'log matlab files')

params = ['AHR2','ATT','BARO_0','BAT_0','GPS_0','XKF1_0','RATE','RCOU']

## Reading Flight from excel files

# Path to Excel file 
excel_file = os.path.join(cwd,inputs['path']['excel_file'])

# Read Excel (expects headers: 'Sensor file', 'Log file') 
df = pd.read_excel(excel_file)

# Check columns exist
required_cols = ['Sensor Filename', 'Log Filename']
if not all(col in df.columns for col in required_cols):
    raise ValueError(f"Excel must contain columns: {required_cols}")

print(f"\nExcel file loaded with {len(df)} cases.")
print("Columns found:", list(df.columns))

# case list
row_input = inputs['case_list']
##User input for rows
#row_input = input(
#    "\nEnter rows to use (e.g. 1-5 for first 5 rows, or 24 for only 24th row): "
#).strip()

if '-' in row_input:
    start, end = row_input.split('-')
    start = int(start)
    end = int(end)
    rows = list(range(start, end + 1))
else:
    rows = [int(row_input)]

# Validate row numbers
max_row = len(df)
for r in rows:
    if r < 1 or r > max_row:
        raise ValueError(f"Row {r} is out of range. Valid rows: 1 to {max_row}")

# Select rows (convert to 0-based indexing)
rows_idx = [r - 1 for r in rows]
df_sel = df.iloc[rows_idx]

# Build cases list
cases = list(zip(
    df_sel['Sensor Filename'].astype(str).str.strip(),
    df_sel['Log Filename'].astype(str).str.strip()
))

print("\nSelected cases:")
for i, (s, l) in zip(rows, cases):
    print(f"Row {i}: {s} , {l}")


def process_case(sen_filename, log_filename):

    sen_file = os.path.join(sen_path,sen_filename)
    log_file='//'.join(log_path.split('\\')[:]) + '//' + log_filename

    try:
        sen_data = senlab.tsm_data_simple(sen_file)
    except:
        raise Exception('sensor file is not present')

    sen_data_inter = senlab.read_csv_interp(sen_file, 5, 10)

    try:
        data = mavlab.data(log_file, params)
    except:
        raise Exception('log file is not present')

    time = mavlab.timedata_gpscor(log_file, params)

    # sen_time = np.array(sen_data['Time Stamp'])
    # for i in range(len(sen_time)):
    #     sen_time[i] = datetime.datetime.strptime(
    #         sen_time[i], '%Y_%m_%d_%H_%M_%S'
    #     ) + datetime.timedelta(minutes=92, seconds=50)

    # bad = sen_data['Time Stamp'][~valid_idx]
    # print("Bad timestamps:", bad.unique()[:5])

    sen_time_raw = np.array(sen_data['Time Stamp'])
    sen_time = []

    for ts in sen_time_raw:
        try:
            t = datetime.datetime.strptime(ts, '%Y_%m_%d_%H_%M_%S')
            t = t + datetime.timedelta(minutes=92, seconds=50)
            sen_time.append(t)
        except ValueError:
            # invalid timestamps like '1900_0_0_0_0_0'
            sen_time.append(None)

    sen_time = np.array(sen_time)



    t1 = round((time['XKF1_0'][0] - sen_time[0]).total_seconds())
    t2 = round((sen_time[-1] - time['XKF1_0'][-1]).total_seconds())


    pressure = np.array(sen_data_inter['Absolute Pressure (TSM) (hPa)'])
    wind = np.array(sen_data_inter['Wind Speed (m/s)'])
    temp = np.array(sen_data_inter['Temperature (TSM) (C)'])
    alt = -1*np.array(data['XKF1_0']['PD'])
    vel = -np.array(data['XKF1_0']['VD'])

    if t2 < 0:
        n = (t1 + t2) * 10
        pressure2 = pressure[n:n+len(alt)]
        alt2 = alt[:len(pressure2)]
        vel2 = vel[:len(pressure2)]
        wind2 = wind[n:n+len(alt)]
        temp2 = temp[n:n+len(alt)]
    if t1 <0:
        n=-(t1+t2)*10
        pressure2 = pressure[:len(alt)]
        alt2 = alt[n:n+len(pressure2)]
        vel2 = vel[n:n+len(pressure2)]
        wind2 = wind[n:n+len(alt)]
        temp2 = temp[n:n+len(alt)]

    else:
        n = t1 * 10
        pressure2 = pressure[n:n+len(alt)]
        alt2 = alt[:len(pressure2)]
        vel2 = vel[:len(pressure2)]
        wind2 = wind[n:n+len(alt)]
        temp2 = temp[n:n+len(alt)]

    # --- Extract signals ---

    # pressure = np.array(sen_data_inter['Absolute Pressure (TSM) (hPa)'])
    # wind = np.array(sen_data_inter['Wind Speed (m/s)'])
    # alt = -1*np.array(data['XKF1_0']['PD'])
    # vel = -np.array(data['XKF1_0']['VD'])

    # pressure2 = pressure[n:n+len(alt)]
    # alt2 = alt[:len(pressure2)]
    # vel2 = vel[:len(pressure2)]
    # wind2 = wind[n:n+len(alt)]

    time_main = np.arange(len(alt2)) / 10.0  # 10 Hz

    # --- Detect phases ---
    as_start=as_end=None

    t = 0
    for i in range(1, pressure2.size):
        if vel2[i] > 0.1:
            t += 1
            if t == 500:
                as_start = i - 499
                break

    t = 0
    for i in range(as_start, pressure2.size):
        if vel2[i] < 0.1:
            t += 1
            if t == 200:
                as_end = i - 199
                break

    hov_start, des_start, des_end = [], [], []
    k = a = b = 0
    in_hover = False
    in_descent = False

    for i in range(as_end, vel2.size):

        if not in_hover and -0.2 < vel2[i] < 0.2:
            k += 1
            if k == 50:
                hov_start.append(i - 49)
                k = 0
                in_hover = True
        else:
            k = 0

        if not in_descent and vel2[i] < -2.5:
            a += 1
            if a == 20:
                des_start.append(i - 19)
                a = 0
                in_descent = True
                in_hover = False
        else:
            a = 0

        if in_descent and vel2[i] > -2.5:
            b += 1
            if b == 20:
                des_end.append(i - 19)
                b = 0
                in_descent = False
        else:
            b = 0
    
    alt_as = alt2[as_start:as_end]
    wind_as = wind2[as_start:as_end] 
    temp_as = temp2[as_start:as_end] 
        # ---- case time from log ----
    case_time = time['XKF1_0'][0].replace(microsecond=0)

    return {
        # 'sensor_file': sen_filename,
        'log_file': log_filename,
        # 'hov_start': hov_start,
        # 'des_start': des_start,
        # 'des_end': des_end,
        # 'time': time_main,
        # 'alt': alt2,
        'as_start': as_start,
        'as_end': as_end,
        'alt_as': alt_as,
        'wind_as': wind_as,
        'temp_as': temp_as,
        'n_hovers': len(des_start),
        'case_time': case_time

    }

results = []

for sen_file, log_file in cases:
    res = process_case(sen_file, log_file)
    results.append(res)

    print(sen_file, "→ hovers:", res['n_hovers'])




# Plotting ascent profiles over time 
with PdfPages('test.pdf') as pdf:
    fig, ax = plt.subplots(figsize=(20, 6))
    
    # ax.set_title('Ascent Wind Profiles over Time')
    ax.set_xlabel('Time')
    ax.set_ylabel('Altitude (m)')
    
    # ---- Y axis: 0–600 every 100 m ----
    alt_min_plot = 0
    alt_max_plot = 600
    ax.set_ylim(alt_min_plot, alt_max_plot)
    ax.set_yticks(np.arange(alt_min_plot, alt_max_plot + 1, 100))
    
    # ---- Build time axis ----
    case_times = [res['case_time'] for res in results]
    xvals = mdates.date2num(case_times)
    
    tmin = min(case_times).replace(minute=0, second=0, microsecond=0)
    tmax = (max(case_times) + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    plotter = inputs['plotter']
    if plotter['auto_time'] == False:
        min_time = plotter['min_time']
        time_dict = {'year':min_time[0],'month':min_time[1],'day':min_time[2],'hour':min_time[3],'minute':min_time[4],'second':min_time[5]}
        tmin=datetime.datetime(**time_dict) #'2025-10-09T15:00:00')

        max_time = plotter['max_time']
        time_dict = {'year':max_time[0],'month':max_time[1],'day':max_time[2],'hour':max_time[3],'minute':max_time[4],'second':max_time[5]}
        tmax=datetime.datetime(**time_dict) #'2025-10-09T15:00:00')

    ax.set_xlim(mdates.date2num(tmin), mdates.date2num(tmax))
    
    # ---- Hourly ticks ----
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.tick_params(axis='x', rotation=0, pad=15)
    
    # ax.grid(True)
    
    # ---- Plot profiles as vertical bars ----
    width_frac = 0.10
    
    for xv, res in zip(xvals, results):
    
        xp = (xv - ax.get_xlim()[0]) / (ax.get_xlim()[1] - ax.get_xlim()[0])
    
        ax_in = inset_axes(
            ax,
            width=f"{width_frac*100:.1f}%",
            height="100%",
            loc='lower left',
            bbox_to_anchor=(xp, 0.0, 1, 1),
            bbox_transform=ax.transAxes,
            borderpad=0,
        )
    
        ax_in.plot(res['wind_as'], res['alt_as'], lw=2, color='k')
        #ax_in.plot(res['temp_as'], res['alt_as'], lw=2, color='k')
        ax_in.plot([xp,xp],[0,600],'--',color='gray',lw=1)
        ax_in.set_xlim(0, 15)
        ax_in.set_ylim(alt_min_plot, alt_max_plot)
        ax_in.set_frame_on(False)
    
        ax_in.set_xticks([0, 5, 10, 15])
    
        ax_in.xaxis.set_ticks_position('top')
        ax_in.xaxis.set_label_position('top')
        ax_in.tick_params(axis='x', top=True, labeltop=True,
        bottom=False, labelbottom=False, labelsize=10)
        ax_in.tick_params(axis='x', labelsize=10)
        ax_in.set_yticks([])
        # ax_in.grid(True)
    
    #pdf.savefig(dpi=300)
    plt.show()














