# Code to work on hover phase of the the Flight - Rajali 2025

import os,sys
cwd = os.path.dirname(__file__) # current working directory
sys.path.append(os.path.join(cwd, "../../main libraries"))
import matplotlib.pyplot as plt
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yaml

import matplotlib
font={'family':'serif','size':15}
matplotlib.rc('font',**font)



## Reading input yaml file and excel file to get the list of cases to process ##

# read in input yaml file
with open(r"D:\Fly-By-Data\cases\rajali_2025\inputs.yaml", 'r') as file:
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

###########################################################################################################################

## Call function to process files and get indices of hover and descent phases

from driver import process_case

results = []


for sen_file, log_file in cases:
    res = process_case(sen_file, log_file)
    results.append(res)

    print(sen_file, "→ hovers:", res['n_hovers'])
    
    print("Hover start indices:", res['hov_start'])
    print("Hover end indices:", res['hov_end']) 


figures = []

for res in results:

    fig = plt.figure(figsize=(10,5))

    plt.plot(res['alt'], color='tab:blue')

    plt.title(f"Altitude Profile - {res['case_time']}")
    plt.xlabel("Index")
    plt.ylabel("Altitude (m)")

    plt.legend(['Altitude'])
    plt.grid(True)

    figures.append(fig)

plt.show()

## Sample to extract wind data  - 

for res in results:
    # Extract time, wind, and altitude data from the result dictionary
    time = res['time']
    wind = res['wind'] # total wind data array
    alt = res['alt']

    hover_wind=[]
    alt_hover=[]
    
    for i in range(len(res['hov_end'])):
        start_idx = res['hov_start'][i]
        end_idx = res['hov_end'][i]
        
        hover_wind.append(wind[start_idx:end_idx+1])
          
    
    res['hover_wind'] = hover_wind

wind_data=results[0]['hover_wind'][0]

plt.figure(figsize=(10,5))
plt.plot( wind_data, marker='o')   
plt.show()

