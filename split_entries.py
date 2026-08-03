import pandas as pd

# Load Garmin splits CSV
df = pd.read_csv("data/splitsx.csv")

# Columns we care about most
cols = [
    "Step Type",
    "Lap",
    "Time",
    "Distance",
    "Avg Pace",
    "Avg HR",
    "Max HR",
    "Avg Run Cadence",
    "Avg Power"
]

# Keep only Run and Recovery intervals
intervals = (
    df[cols]
    .reset_index(drop=True)
)

print(intervals)