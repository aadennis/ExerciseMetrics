import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FILE = "data/output/23591045148_ACTIVITY-fit.csv"      # <-- your exported FIT CSV

# ------------------------------
# LOAD DATA
# ------------------------------

df = pd.read_csv(FILE)

# Typical Garmin FIT CSV names
HR = "heart_rate"
CAD = "cadence_spm"
ALT = "enhanced_altitude"
DIST = "distance"

required = [HR, CAD, ALT, DIST]

for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

# ------------------------------
# DERIVED METRICS
# ------------------------------

df["alt_change"] = df[ALT].diff().fillna(0)

# Define climbing samples
df["climbing"] = df["alt_change"] > 0.5

# Estimate stride length
#
# speed(m/s) = distance_delta / time_delta
#
# stride_length ≈ speed * 60 / cadence
#

if "enhanced_speed" in df.columns:
    speed = df["enhanced_speed"]
else:
    dist_delta = df[DIST].diff()
    speed = dist_delta  # assumes 1-second recording

df["stride_length"] = np.where(
    df[CAD] > 0,
    speed * 60 / df[CAD],
    np.nan
)

# ------------------------------
# OVERALL SUMMARY
# ------------------------------

print("\n=== OVERALL ===")

print(f"Average HR       : {df[HR].mean():.1f}")
print(f"Max HR           : {df[HR].max():.0f}")

print(f"Average Cadence  : {df[CAD].mean():.1f}")

pct_target_cad = (
    (df[CAD] >= 155) &
    (df[CAD] <= 165)
).mean() * 100

print(f"% time 155-165spm: {pct_target_cad:.1f}%")

pct_z2 = (df[HR] < 125).mean() * 100

print(f"% time <125 bpm  : {pct_z2:.1f}%")

print(f"Average stride   : {df['stride_length'].mean():.2f} m")

# ------------------------------
# CLIMB ANALYSIS
# ------------------------------

up = df[df["climbing"]]

if len(up):

    print("\n=== CLIMBING ===")

    print(f"Samples climbing : {len(up)}")
    print(f"Avg HR climbing  : {up[HR].mean():.1f}")
    print(f"Max HR climbing  : {up[HR].max():.0f}")

    print(f"Avg cadence      : {up[CAD].mean():.1f}")

    print(
        f"% climb <125 bpm : "
        f"{(up[HR] < 125).mean()*100:.1f}%"
    )

    print(
        f"Avg stride climb : "
        f"{up['stride_length'].mean():.2f} m"
    )

# ------------------------------
# HIGH-HR SEGMENTS
# ------------------------------

high_hr = df[df[HR] > 125]

print("\n=== ABOVE Z2 LIMIT ===")

if len(high_hr):
    print(f"Samples >125 bpm : {len(high_hr)}")
    print(f"Average HR        : {high_hr[HR].mean():.1f}")
    print(f"Average cadence   : {high_hr[CAD].mean():.1f}")
    print(
        f"Average stride    : "
        f"{high_hr['stride_length'].mean():.2f} m"
    )

# ------------------------------
# CORRELATIONS
# ------------------------------

print("\n=== RELATIONSHIPS ===")

corr_hr_stride = df[HR].corr(df["stride_length"])
corr_hr_cad = df[HR].corr(df[CAD])

print(f"HR vs stride length : {corr_hr_stride:.3f}")
print(f"HR vs cadence       : {corr_hr_cad:.3f}")

# ------------------------------
# CHARTS
# ------------------------------

fig, ax = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

ax[0].plot(df[DIST]/1000, df[HR])
ax[0].axhline(125, color="red", linestyle="--")
ax[0].set_ylabel("HR")

ax[1].plot(df[DIST]/1000, df[CAD])
ax[1].axhline(160, color="green", linestyle="--")
ax[1].set_ylabel("Cadence")

ax[2].plot(df[DIST]/1000, df[ALT])
ax[2].set_ylabel("Altitude")
ax[2].set_xlabel("Distance (km)")

plt.tight_layout()
plt.show()