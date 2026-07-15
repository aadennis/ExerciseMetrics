import pandas as pd
import numpy as np

CSV_FILE = "data/output/23567118490_ACTIVITY-fit.csv"

df = pd.read_csv(CSV_FILE)

# Adjust these names if needed
time_col = "timestamp"
hr_col = "heart_rate"
speed_col = "speed"
cad_col = "cadence_spm"

# Convert timestamp
df[time_col] = pd.to_datetime(df[time_col])

# Keep only rows with required data
df = df[[time_col, hr_col, speed_col, cad_col]].dropna()

# Remove first and last 5 minutes
start_time = df[time_col].min() + pd.Timedelta(minutes=5)
end_time = df[time_col].max() - pd.Timedelta(minutes=5)

df_trim = df[
    (df[time_col] >= start_time) &
    (df[time_col] <= end_time)
].copy()

if len(df_trim) < 20:
    raise ValueError("Not enough data remaining after trimming.")

# Split remaining run into halves
mid = len(df_trim) // 2
first = df_trim.iloc[:mid]
second = df_trim.iloc[mid:]

# Means
hr1 = first[hr_col].mean()
hr2 = second[hr_col].mean()

spd1 = first[speed_col].mean()
spd2 = second[speed_col].mean()

cad1 = first[cad_col].mean()
cad2 = second[cad_col].mean()

# Efficiency metric
eff1 = spd1 / hr1
eff2 = spd2 / hr2

decoupling_pct = (eff2 - eff1) / eff1 * 100
speed_drift_pct = (spd2 - spd1) / spd1 * 100
cadence_drift_pct = (cad2 - cad1) / cad1 * 100

print("=== Zone 2 Drift Analysis (5 min trimmed) ===")
print(f"HR first half:        {hr1:.1f}")
print(f"HR second half:       {hr2:.1f}")
print()
print(f"Speed first half:     {spd1:.3f} m/s")
print(f"Speed second half:    {spd2:.3f} m/s")
print()
print(f"Cadence first half:   {cad1:.1f} spm")
print(f"Cadence second half:  {cad2:.1f} spm")
print()
print(f"Aerobic decoupling:   {decoupling_pct:.2f}%")
print(f"Speed drift:          {speed_drift_pct:.2f}%")
print(f"Cadence drift:        {cadence_drift_pct:.2f}%")

if abs(decoupling_pct) < 5:
    print("\n✅ Excellent aerobic stability (<5%)")
elif abs(decoupling_pct) < 10:
    print("\n⚠️ Moderate drift (5-10%)")
else:
    print("\n❌ Significant drift (>10%)")
