# Fly-By-Data

The repository contains campaigain specific folders under "cases"

The script folder contains preprocess.py, which will process the raw sensor files and remove unwanted columns.

driver.py (for each campaign) takes the cleaned sensor file, log mat files, and an Excel sheet containing names of the files as input and gives the Wind profile graph.

Hover.py extracts the hover start and end index for flights and then data can be used further.

General instructions before running the scripts - 

- Download the "log matlab files" and "Processed sensor files" folders from workstation.
- Append their path in 'log_path' and 'sen_path' respectively in the inputs.yaml file
- The excel file contains the name of Sensor and Log (.mat) files of each flight test.
- User input in yaml file - Enter the number of flights to be displayed in the form "15-20" for multiple files and "5" for a single file.




