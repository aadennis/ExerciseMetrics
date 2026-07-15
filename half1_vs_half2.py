import pandas as pd
import numpy as np

CSV_FILE = "data/output/23603839943_ACTIVITY-fit.csv"

df = pd.read_csv(CSV_FILE)

# Adjust column names if needed
hr_col = "heart_rate"
speed_col = "speed"
cad_col = "cadence_spm"

# Remove rows missing key data
df = df[[hr_col, speed_col, cad_col]].dropna()

# Split run into halves
mid = len(df) // 2
first = df.iloc[:mid]
second = df.iloc[mid:]

# Means
hr1 = first[hr_col].mean()
hr2 = second[hr_col].mean()

spd1 = first[speed_col].mean()
spd2 = second[speed_col].mean()

cad1 = first[cad_col].mean()
cad2 = second[cad_col].mean()

# Aerobic decoupling
# Ratio of speed to HR
eff1 = spd1 / hr1
eff2 = spd2 / hr2

decoupling_pct = (eff2 - eff1) / eff1 * 100

# Cadence drift
cadence_drift_pct = (cad2 - cad1) / cad1 * 100

# Pace drift
speed_drift_pct = (spd2 - spd1) / spd1 * 100

print("\n=== Zone 2 Drift Analysis ===")
print(f"HR first half:     {hr1:.1f}")
print(f"HR second half:    {hr2:.1f}")

print(f"\nSpeed first half:  {spd1:.3f} m/s")
print(f"Speed second half: {spd2:.3f} m/s")

print(f"\nCadence first:     {cad1:.1f} spm")
print(f"Cadence second:    {cad2:.1f} spm")

print(f"\nAerobic decoupling: {decoupling_pct:.2f}%")
print(f"Cadence drift:      {cadence_drift_pct:.2f}%")
print(f"Speed drift:        {speed_drift_pct:.2f}%")

if abs(decoupling_pct) < 5:
    print("\n✅ Good Zone 2 stability (<5% decoupling)")
elif abs(decoupling_pct) < 10:
    print("\n⚠️ Moderate drift (5-10%)")
else:
    print("\n❌ Significant drift (>10%)")
