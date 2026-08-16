"""
Get values from a Garmin splits csv file and save those to another csv file.
This reduces the full set to those values which are available from a 
Forerunner 255 watch. That translates to these fields:
  Laps,Time,Cumulative Time,Distance km,Avg Pace min/km,Avg HR bpm,
  Max HR bpm,Avg Run Cadence spm,Avg Ground Contact Time ms,Avg Stride Length m,
  Avg Vertical Oscillation cm,Avg Vertical Ratio %,Best Pace min/km,Max Run Cadence 

I make a naive check that the input file is in Splits format, by checking that 
a column 'Avg Ground Contact Time ms' is found after reading the file. 
If it is not found, an exception is thrown, and we exit.
"""
import pandas as pd
from pathlib import Path

CSV_FILE = "c:/temp/run_splits_30m30.csv"

LOCAL_OUTPUT = True
GCT = 'Avg Ground Contact Time ms'
df = pd.read_csv(CSV_FILE)

try:
    gct_col = df[GCT]
except KeyError:
    raise ValueError(f"Expected column {GCT} not found — wrong dataframe?")

mf = df[["Laps","Time","Cumulative Time","Distance km","Avg Pace min/km","Avg HR bpm",
         "Max HR bpm","Avg Run Cadence spm","Avg Ground Contact Time ms",
         "Avg Stride Length m","Avg Vertical Oscillation cm","Avg Vertical Ratio %",
         "Best Pace min/km","Max Run Cadence spm"
         ]]

p = Path(CSV_FILE)
if LOCAL_OUTPUT:
  output_file = f"data/output/{p.stem}.out.csv"
else:
  output_file = f"c:/temp/{p.stem}.out.csv"

mf.to_csv(output_file, index=False)
print(f"*** output file is here: \n*** [{output_file}]")