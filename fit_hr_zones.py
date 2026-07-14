import pandas as pd

# Garmin zones
ZONES = {
    "Z1": (89, 106),
    "Z2": (107, 124),
    "Z3": (125, 141),
    "Z4": (142, 159),
    "Z5": (160, 999),
}

# Change filename as required
df = pd.read_csv("data/output/23567118490_ACTIVITY-fit.csv")

# Try to identify columns automatically
hr_col = next(c for c in df.columns if "heart" in c.lower() or c.lower() == "hr")
dist_col = next(c for c in df.columns if "distance" in c.lower())

# Distance: FIT CSV exports are often in metres
distance_km = df[dist_col].max() / 1000

# Time per sample
if "timestamp" in [c.lower() for c in df.columns]:
    ts_col = next(c for c in df.columns if c.lower() == "timestamp")
    df[ts_col] = pd.to_datetime(df[ts_col])
    sample_sec = df[ts_col].diff().dt.total_seconds().median()
else:
    sample_sec = 1  # assume 1-second recording

# Zone analysis
results = {}
for zone, (lo, hi) in ZONES.items():
    secs = ((df[hr_col] >= lo) & (df[hr_col] <= hi)).sum() * sample_sec
    results[zone] = secs / 60

avg_hr = df[hr_col].mean()
max_hr = df[hr_col].max()

print(f"Distance: {distance_km:.2f} km")
print(f"Average HR: {avg_hr:.0f} bpm")
print(f"Max HR: {max_hr:.0f} bpm")
print("\nTime in zones:")

total_mins = sum(results.values())
for z, mins in results.items():
    pct = 100 * mins / total_mins if total_mins else 0
    print(f"{z}: {mins:.1f} min ({pct:.1f}%)")

# Fat-burn assessment
z1_z2 = results["Z1"] + results["Z2"]
pct_fatburn = 100 * z1_z2 / total_mins if total_mins else 0

print(f"\nZ1+Z2 (fat-burn range): {z1_z2:.1f} min ({pct_fatburn:.1f}%)")

if pct_fatburn >= 80:
    print("Excellent fat-burn run.")
elif pct_fatburn >= 60:
    print("Mostly fat-burn aerobic run.")
else:
    print("Significant time above fat-burn range.")
