import pandas as pd


CSV_FILE = "data/split01.csv"
df = pd.read_csv(CSV_FILE)
print(df.head())

mf = df[["Laps","Time","Cumulative Time","Distance km","Avg Pace min/km","Avg HR bpm",
         "Max HR bpm","Avg Run Cadence spm","Avg Ground Contact Time ms",
         "Avg Stride Length m","Avg Vertical Oscillation cm","Avg Vertical Ratio %"]]
print(mf.head())

mf.to_csv("c:/temp/aaa.csv", index=False)
