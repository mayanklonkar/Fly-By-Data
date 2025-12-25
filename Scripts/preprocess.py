
## Multiple CSV preprocessing ##

import pandas as pd
import os

# ---------- Base folder with original CSVs ----------
base_folder = r"C:\Users\Mayank\Desktop\RAJALI 2025\Sensor Hub data (27)"

# ---------- Output folder ----------
out_folder = os.path.join(base_folder, "Processed sensor files")
os.makedirs(out_folder, exist_ok=True)

# ---------- Excel file with CSV names ----------
excel_path = r"C:\Users\Mayank\Desktop\RAJALI 2025\Rajali_pre.xlsx"

# Read Excel (first column has filenames)
df_list = pd.read_excel(excel_path)
file_names = df_list.iloc[:, 0].dropna().tolist()

print(f"Found {len(file_names)} files to process.")

# -------- Headers --------
headers = [
    "Time Stamp",
    "Wind Speed (m/s)",
    "Horizontal Wind Direction (Degrees)",
    "U Vector (m/s)",
    "V Vector (m/s)",
    "W Vector (m/s)",
    "Temperature (TSM) (C)",
    "Relative Humidity (TSM) (%)",
    "Absolute Pressure (TSM) (hPa)",
    "Pitch Angle (Degrees)",
    "Roll Angle (Degrees)",
    "Temperature (AHT10) (C)",
    "Relative Humidity (AHT10) (%)",
    "Temperature (MS5611) (C)",
    "Absolute Pressure (MS5611) (hPa)"
]

# Columns to remove (1-based → 0-based)
cols_to_remove_1based = [2,4,6,8,10,12,14,16,18,20,22,23]
cols_to_remove_0based = [c-1 for c in cols_to_remove_1based]

# ---------- Process each file ----------
for name in file_names:
    try:
        sen_path = os.path.join(base_folder, name)

        print(f"\nProcessing: {name}")

        df = pd.read_csv(
            sen_path,
            header=None,
            sep=",",
            engine="python",
            skiprows=2
        )

        # Remove unwanted columns
        valid_cols = [c for c in cols_to_remove_0based if c < df.shape[1]]
        df = df.drop(columns=valid_cols)

        # Assign headers
        df.columns = headers[:df.shape[1]]

        # Output path in new folder
        out_name = "cleaned_" + name
        out_path = os.path.join(out_folder, out_name)

        df.to_csv(out_path, index=False)

        print(f"✅ Saved to: {out_path}")

    except Exception as e:
        print(f"❌ Failed for {name}: {e}")

print("\n All files processed.")


## Single CSV preprocessing  ##


# import pandas as pd
# ---------- Paths ----------
# sen_path = r"C:\Users\Mayank\Desktop\RAJALI 2025\Sensor Hub data (27)\2025_10_10_4_19_22.csv"
# out_path = r"C:\Users\Mayank\Desktop\RAJALI 2025\Sensor Hub data (27)\cleaned_2025_10_10_4_19_22.csv"

# # ---------- Read CSV ----------
# # Skip first two rows since they are messy and not needed


# # -------- Read CSV: skip first 2 problematic rows --------
# df = pd.read_csv(
#     sen_path,
#     header=None,
#     sep=",",
#     engine="python",
#     skiprows=2      # <-- KEY FIX
# )

# print("After read:", df.shape)

# # -------- Remove specific columns (1-based → 0-based) --------
# cols_to_remove_1based = [2,4,6,8,10,12,14,16,18,20,22,23]
# cols_to_remove = [c-1 for c in cols_to_remove_1based if c-1 < df.shape[1]]

# df = df.drop(columns=cols_to_remove)
# print("After column removal:", df.shape)

# # -------- Assign headers --------
# headers = [
#     "Time Stamp",
#     "Wind Speed (m/s)",
#     "Horizontal Wind Direction (Degrees)",
#     "U Vector (m/s)",
#     "V Vector (m/s)",
#     "W Vector (m/s)",
#     "Temperature (TSM) (C)",
#     "Relative Humidity (TSM) (%)",
#     "Absolute Pressure (TSM) (hPa)",
#     "Pitch Angle (Degrees)",
#     "Roll Angle (Degrees)",
#     "Temperature (AHT10) (C)",
#     "Relative Humidity (AHT10) (%)",
#     "Temperature (MS5611) (C)",
#     "Absolute Pressure (MS5611) (hPa)"
# ]

# df.columns = headers[:df.shape[1]]

# # -------- Save --------
# df.to_csv(out_path, index=False)

# print("✅ Cleaned file saved to:", out_path)



# ## Code removing columns detecting alphabet or numeric in 3rd row ##
# not working currently

# import pandas as pd
# df = pd.read_csv(
#     sen_path,
#     header=None,
#     sep=",",          # tab-separated file
#     engine="python",
#     skiprows=2
# )

# # ---------- Step 1: Filter columns using original 3rd row ----------
# third_row = df.iloc[0]

# def is_numeric(val):
#     try:
#         float(val)
#         return True
#     except:
#         return False

# keep_cols = [is_numeric(v) for v in third_row]

# # ---------- Step 2: Explicitly drop faulty column 23 (1-based index) ----------
# faulty_col_index = 22  # Python uses 0-based indexing
# if faulty_col_index < len(keep_cols):
#     keep_cols[faulty_col_index] = False

# # ---------- Step 3: Apply column filter ----------
# df = df.loc[:, keep_cols].reset_index(drop=True)

# # ---------- Step 4: Assign headers ----------
# headers = [
#     "Time Stamp",
#     "Wind Speed (m/s)",
#     "Horizontal Wind Direction (Degrees)",
#     "U Vector (m/s)",
#     "V Vector (m/s)",
#     "W Vector (m/s)",
#     "Temperature (TSM) (C)",
#     "Relative Humidity (TSM) (%)",
#     "Absolute Pressure (TSM) (hPa)",
#     "Pitch Angle (Degrees)",
#     "Roll Angle (Degrees)",
#     "Temperature (AHT10) (C)",
#     "Relative Humidity (AHT10) (%)",
#     "Temperature (MS5611) (C)",
#     "Absolute Pressure (MS5611) (hPa)"
# ]

# df.columns = headers[:df.shape[1]]

# # ---------- Step 5: Save ----------
# df.to_csv(out_path, index=False)

# print("✅ Cleaned file saved to:")
# print(out_path)

