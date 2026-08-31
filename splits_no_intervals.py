"""

This script:
- is specifically for the SPLITS .csv produced by Garmin when you have not pressed the lap button during the run.
- reads a CSV file containing running data, selects specific columns related to the run metrics, and 
  then saves the selected data to a new CSV file.

"""
import pandas as pd
INPUT_FILE = "data/run_31_August_5kflathard.csv"
OUTPUT_FILE = "data/splitsx_out.csv"

a = pd.read_csv(INPUT_FILE)
b = a[["Laps","Time","Cumulative Time","Distance km","Avg Pace min/km","Avg HR bpm","Max HR bpm","Total Ascent m",
       "Total Descent m","Avg Power W","Max Power W","Avg Run Cadence spm","Avg Ground Contact Time ms",
       "Avg Stride Length m","Avg Vertical Oscillation cm","Avg Vertical Ratio %","Best Pace min/km","Max Run Cadence spm"]]
b.to_csv(OUTPUT_FILE, index=False)

print(f"*** output file is here: \n*** [{OUTPUT_FILE}]")    

