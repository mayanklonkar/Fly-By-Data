# Fly-By-Data

This repository contains the code required to plot sensor-hub parameters against the altitude extracted from telemetry logs. 

- The telemetry log file should be downloaded in .mat format from the Mission Planner.
- Path for both the sensor (.csv) file and the telemetry log file should be modified in the Sample_Plot.ipynb code.

- The generated CSV files have some header problems due to Trisonica settings.
- Remove all the empty columns or columns having parameter symbols such as "U", "V", "P", etc. ( First few columns marked in Red for reference. )

<img width="1868" height="653" alt="image" src="https://github.com/user-attachments/assets/b6ba2836-1e82-4338-9959-fc6c51def559" />

- After selecting columns containing only the readings, rename the header row accordingly:


'Time Stamp'	 'Wind Speed (m/s)' 	'Horizontal Wind Direction (Degrees)' 	'U Vector (m/s)'	 'V Vector (m/s)' 	'W Vector (m/s)' 	'Temperature (TSM) (C)'	 'Relative Humidity (TSM) (%)'	 'Absolute Pressure (TSM) (hPa)'	 'Pitch Angle (Degrees)' 	'Roll Angle (Degrees)'	 'Temperature (AHT10) (C)' 	'Relative Humidity (AHT10) (%)' 	'Temperature (MS5611) (C)' 'Absolute Pressure (MS5611) (hPa)'

<img width="3106" height="40" alt="image" src="https://github.com/user-attachments/assets/ea43028a-33a2-46d4-8996-4b85b38fe681" />

- The updated CSV file can now be used to create plots using the 'Sample_Plots.ipynb' code.
- The parameters to be plotted are identified using their header names in the code.


