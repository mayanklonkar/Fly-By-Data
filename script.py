import sys
sys.path.insert(0,r"C:\Users\Mayank\Desktop\RAJALI 2025\Fly-By-Data-main\main libraries") # folder which has main loading libs
import mavlab
import senlab
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd
import matplotlib.dates as mdates


# Preprocessing Sensor Data

# sen_filename = '2025_10_10_4_19_22.csv'

# cols_to_remove = [2,4,6,8,10,12,14,16,18,20]
# cols_to_remove = [c-1 for c in cols_to_remove]

# df = pd.read_csv(sen_filename, encoding='unicode_escape')

# # Drop by index
# df_clean = df.drop(df.columns[cols_to_remove], axis=1)

# print(df_clean.head())

# out_file = sen_path + '\\cleaned_2025_10_10_4_19_22.csv'
# df_clean.to_csv(out_file, index=False)


sen_path = r'C:\Users\Mayank\Desktop\RAJALI 2025\Sensor Hub data (27)\Processed sensor files'
log_path = r'C:\Users\Mayank\Desktop\RAJALI 2025\log matlab files'
params = ['AHR2','ATT','BARO_0','BAT_0','GPS_0','XKF1_0','RATE','RCOU']



cases = [
    ('cleaned_2025_10_9_13_12_26.csv','2025-10-09 14-43-07.bin-1608525.mat'),
    ('cleaned_2025_10_9_14_24_15.csv', '2025-10-09 15-58-08.bin-1778367.mat'),
    ('cleaned_2025_10_9_15_31_56.csv', '2025-10-09 17-12-00.bin-1460430.mat'),
    ('cleaned_2025_10_9_16_55_48.csv', '2025-10-09 18-30-34.bin-414162.mat'),
    ('cleaned_2025_10_9_21_31_39.csv', '2025-10-09 23-06-46.bin-777215.mat')
]



def process_case(sen_filename, log_filename):

    sen_file = sen_path + '\\' + sen_filename
    # log_file = log_path + '\\' + log_filename
    log_file='//'.join(log_path.split('\\')[:]) + '//' + log_filename

    sen_data = senlab.tsm_data_simple(sen_file)
    sen_data_inter = senlab.read_csv_interp(sen_file, 5, 10)

    data = mavlab.data(log_file, params)
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
    alt = -1*np.array(data['XKF1_0']['PD'])
    vel = -np.array(data['XKF1_0']['VD'])

    if t2 < 0:
        n = (t1 + t2) * 10
        pressure2 = pressure[n:n+len(alt)]
        alt2 = alt[:len(pressure2)]
        vel2 = vel[:len(pressure2)]
        wind2 = wind[n:n+len(alt)]
    if t1 <0:
        n=-(t1+t2)*10
        pressure2 = pressure[:len(alt)]
        alt2 = alt[n:n+len(pressure2)]
        vel2 = vel[n:n+len(pressure2)]
        wind2 = wind[n:n+len(alt)]

    else:
        n = t1 * 10
        pressure2 = pressure[n:n+len(alt)]
        alt2 = alt[:len(pressure2)]
        vel2 = vel[:len(pressure2)]
        wind2 = wind[n:n+len(alt)]

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
        'n_hovers': len(des_start),
        'case_time': case_time

    }

results = []

for sen_file, log_file in cases:
    res = process_case(sen_file, log_file)
    results.append(res)

    print(sen_file, "→ hovers:", res['n_hovers'])







import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np

# fig, ax = plt.subplots(figsize=(12, 6))

# # Turn off main axes since we don't want background plot
# ax.axis('off')
# ax.set_title('Ascent wind profiles (3 cases)', fontsize=14)

# # Common altitude limits
# alt_min, alt_max = 0,600

# # ---- Equal positions for profiles ----
# xs = np.linspace(0.15, 0.85, len(results))

# colors = ['tab:blue', 'tab:orange', 'tab:green']

# for xp, res, c in zip(xs, results, colors):

#     ax_in = inset_axes(
#         ax,
#         width="20%",     # wider since it's the only content
#         height="70%",
#         loc='lower left',
#         bbox_to_anchor=(xp-0.10, 0.15, 1, 1),
#         bbox_transform=ax.transAxes,
#         borderpad=0
#     )

#     ax_in.plot(res['wind_as'], res['alt_as'], lw=2, color=c)
#     ax_in.set_xlim(-5, 10)              # wind range
#     ax_in.set_ylim(alt_min, alt_max)  # common altitude scale
#     ax_in.set_xlabel('Wind (m/s)', fontsize=9)
#     ax_in.set_ylabel('Altitude (m)', fontsize=9)
#     ax_in.grid(True)

# plt.show()
# ============================================================================

# trying exact plot with time steps #
#working, minor changes needed

# case_times = [res['case_time'] for res in results]
# xvals = mdates.date2num(case_times)


# # --------------------------------------------------
# # Plot: wind profiles as bars over time
# # --------------------------------------------------
# fig, ax = plt.subplots(figsize=(12, 6))

# ax.set_title('Ascent Wind Profiles over Time (3 cases)')
# ax.set_xlabel('Time')
# ax.set_ylabel('Altitude (m)')
# ax.set_ylim(0, 600)

# ax.set_xlim(min(xvals) - 0.05, max(xvals) + 0.05)
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
# fig.autofmt_xdate()

# colors = ['tab:blue', 'tab:orange', 'tab:green']

# for xv, res, c in zip(xvals, results, colors):

#     # map time position to axes fraction
#     xp = (xv - ax.get_xlim()[0]) / (ax.get_xlim()[1] - ax.get_xlim()[0])

#     ax_in = inset_axes(
#         ax,
#         width="10%",
#         height="80%",
#         loc='lower left',
#         bbox_to_anchor=(xp-0.05, 0.1, 1, 1),
#         bbox_transform=ax.transAxes,
#         borderpad=0
#     )

#     ax_in.plot(res['wind_as'], res['alt_as'], lw=2, color=c)
#     ax_in.set_xlim(-5, 15)
#     ax_in.set_ylim(0, 600)
#     # ax_in.set_xticks([])
#     # ax_in.set_yticks([])
#     ax_in.set_xticks([-5, 0, 5, 10])
#     ax_in.tick_params(axis='x', labelsize=8)
#     ax_in.set_yticks([])

#     ax_in.set_xlabel('Wind', fontsize=8)

#     ax_in.grid(True)

# # label ticks as Case + time
# ax.set_xticks(xvals)
# ax.set_xticklabels([f'Case {i+1}\n{t.strftime("%H:%M:%S")}'
#                      for i, t in enumerate(case_times)])

# plt.show()
#----------------------------------------------------------#

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.dates as mdates
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

ax.set_title('Ascent Wind Profiles over Time')
ax.set_xlabel('Time')
ax.set_ylabel('Altitude (m)')


alt_min_plot = 0
alt_max_plot = 650

ax.set_ylim(alt_min_plot, alt_max_plot)
ax.set_yticks(np.arange(alt_min_plot, alt_max_plot + 1, 50))


# ---- Build time axis from results ----
case_times = [res['case_time'] for res in results]
xvals = mdates.date2num(case_times)

ax.set_xlim(min(xvals) - 0.05, max(xvals) + 0.05)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
fig.autofmt_xdate()

# ---- Common altitude range from data ----
all_alt = np.concatenate([res['alt_as'] for res in results])
alt_min, alt_max = all_alt.min(), all_alt.max()
ax.set_ylim(alt_min, alt_max)

# ---- Plot profiles as vertical bars ----
colors = plt.cm.tab10.colors
width_frac = 0.10  # width of each profile "bar"

for xv, res, c in zip(xvals, results, colors):

    # map data x to axis fraction (0–1)
    xp = (xv - ax.get_xlim()[0]) / (ax.get_xlim()[1] - ax.get_xlim()[0])

    # wind limits from that profile
    wmin, wmax = np.min(res['wind_as']), np.max(res['wind_as'])
    pad = 0.1 * (wmax - wmin + 1e-6)
    wmin -= pad
    wmax += pad

    ax_in = inset_axes(
        ax,
        width=f"{width_frac*100:.1f}%",
        height="100%",
        loc='lower left',
        bbox_to_anchor=(xp - width_frac/2, 0.0, 1, 1),
        bbox_transform=ax.transAxes,
        borderpad=0
    )

    ax_in.plot(res['wind_as'], res['alt_as'], lw=2, color=c)
    ax_in.set_xlim(wmin, wmax)
    ax_in.set_ylim(alt_min, alt_max)

    # Show wind axis, hide altitude ticks inside
    # ax_in.set_xlabel('Wind (m/s)', fontsize=8)
    ax_in.tick_params(axis='x', labelsize=8)
    ax_in.set_yticks([])
    ax_in.grid(True)


# ---- Label x ticks as Case + time ----
ax.set_xticks(xvals)
ax.set_xticklabels([f'{t.strftime("%H:%M:%S")}'
                     for i, t in enumerate(case_times)])
ax.tick_params(axis='x', rotation=0, pad=20)

plt.show()













