import pandas as pd
from pathlib import Path

CSV_FILE = "data/split01.csv"
df = pd.read_csv(CSV_FILE)
print(df.head())

mf = df[["Laps","Time","Cumulative Time","Distance km","Avg Pace min/km","Avg HR bpm",
         "Max HR bpm","Avg Run Cadence spm","Avg Ground Contact Time ms",
         "Avg Stride Length m","Avg Vertical Oscillation cm","Avg Vertical Ratio %",
         "Best Pace min/km","Max Run Cadence spm"
         ]]
print(mf.head())

p = Path(CSV_FILE)
output_file = f"c:/temp/{p.stem}.out.csv"

print(f"output file is here: [{output_file}]")

mf.to_csv(output_file, index=False)
