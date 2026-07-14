#!/usr/bin/env python3

"""
Run analysis for FIT-derived CSV containing:

timestamp
cadence_spm
enhanced_speed
heart_rate

Outputs:

1. Overall summary
2. Half-vs-half drift
3. Quartile analysis
4. Aerobic decoupling
5. Cadence drift
6. Efficiency-factor drift
7. Speed-per-step efficiency drift
8. Rolling trend analysis
"""

import pandas as pd
import numpy as np

CSV_FILE = "data/output/full 6 July-fit.csv"

# ----------------------------------------------------------------------
# Load
# ----------------------------------------------------------------------

df = pd.read_csv(CSV_FILE)

required = [
    "heart_rate",
    "enhanced_speed",
    "cadence_spm",
]

for col in required:
    if col not in df.columns:
        raise ValueError(f"Missing column: {col}")

df = df[
    (df["heart_rate"] > 0)
    & (df["enhanced_speed"] > 0)
    & (df["cadence_spm"] > 0)
].copy()

if len(df) < 100:
    raise ValueError("Not enough valid samples")

# ----------------------------------------------------------------------
# Derived metrics
# ----------------------------------------------------------------------

df["EF"] = df["enhanced_speed"] / df["heart_rate"]

# metres per step
df["speed_per_spm"] = (
    df["enhanced_speed"] / df["cadence_spm"]
)

# ----------------------------------------------------------------------
# Basic summary
# ----------------------------------------------------------------------

print()
print("=" * 70)
print("OVERALL SUMMARY")
print("=" * 70)

print(f"Samples             : {len(df):,}")
print(f"Average HR          : {df['heart_rate'].mean():.1f} bpm")
print(f"Average Speed       : {df['enhanced_speed'].mean():.3f} m/s")
print(f"Average Cadence     : {df['cadence_spm'].mean():.1f} spm")
print(f"Average EF          : {df['EF'].mean():.6f}")
print(
    f"Average Speed/SPM   : "
    f"{df['speed_per_spm'].mean():.6f}"
)

# ----------------------------------------------------------------------
# Half analysis
# ----------------------------------------------------------------------

n = len(df)
mid = n // 2

first = df.iloc[:mid]
second = df.iloc[mid:]

print()
print("=" * 70)
print("HALF VS HALF")
print("=" * 70)

def drift(name, col):
    a = first[col].mean()
    b = second[col].mean()

    pct = 100 * (b - a) / a

    print(
        f"{name:<16}"
        f"{a:9.3f} -> {b:9.3f}"
        f"   ({pct:+7.2f}%)"
    )

    return pct

hr_half = drift("Heart Rate", "heart_rate")
speed_half = drift("Speed", "enhanced_speed")
cad_half = drift("Cadence", "cadence_spm")
ef_half = drift("EF", "EF")
sps_half = drift("Speed/SPM", "speed_per_spm")

# ----------------------------------------------------------------------
# Quartiles
# ----------------------------------------------------------------------

q1 = df.iloc[: n // 4]
q2 = df.iloc[n // 4 : n // 2]
q3 = df.iloc[n // 2 : 3 * n // 4]
q4 = df.iloc[3 * n // 4 :]

quarters = [q1, q2, q3, q4]

rows = []

for i, q in enumerate(quarters, start=1):

    rows.append(
        {
            "Quartile": f"Q{i}",
            "HR": q["heart_rate"].mean(),
            "Speed": q["enhanced_speed"].mean(),
            "Cadence": q["cadence_spm"].mean(),
            "EF": q["EF"].mean(),
            "Speed/SPM": q["speed_per_spm"].mean(),
        }
    )

quartile_df = pd.DataFrame(rows)

print()
print("=" * 70)
print("QUARTILE ANALYSIS")
print("=" * 70)

print(
    quartile_df.to_string(
        index=False,
        formatters={
            "HR": "{:.1f}".format,
            "Speed": "{:.3f}".format,
            "Cadence": "{:.1f}".format,
            "EF": "{:.6f}".format,
            "Speed/SPM": "{:.6f}".format,
        },
    )
)

# ----------------------------------------------------------------------
# Q1 -> Q4 Drift
# ----------------------------------------------------------------------

print()
print("=" * 70)
print("Q1 TO Q4 DRIFT")
print("=" * 70)

for metric in ["HR", "Speed", "Cadence", "EF", "Speed/SPM"]:

    start = quartile_df.iloc[0][metric]
    end = quartile_df.iloc[-1][metric]

    pct = 100 * (end - start) / start

    print(
        f"{metric:<12}"
        f"{start:10.4f} -> {end:10.4f}"
        f"   ({pct:+7.2f}%)"
    )

# ----------------------------------------------------------------------
# Aerobic Decoupling
# ----------------------------------------------------------------------

early = pd.concat([q1, q2])
late = pd.concat([q3, q4])

early_ratio = (
    early["enhanced_speed"].mean()
    / early["heart_rate"].mean()
)

late_ratio = (
    late["enhanced_speed"].mean()
    / late["heart_rate"].mean()
)

decoupling = (
    100
    * (late_ratio - early_ratio)
    / early_ratio
)

print()
print("=" * 70)
print("AEROBIC DECOUPLING")
print("=" * 70)

print(f"Decoupling: {decoupling:+.2f}%")

if abs(decoupling) < 3:
    print("Interpretation: Excellent aerobic stability")
elif abs(decoupling) < 5:
    print("Interpretation: Moderate aerobic drift")
else:
    print("Interpretation: Significant aerobic drift")

# ----------------------------------------------------------------------
# Rolling trends
# ----------------------------------------------------------------------

WINDOW = 300

rolling = (
    df[
        [
            "heart_rate",
            "enhanced_speed",
            "cadence_spm",
            "EF",
            "speed_per_spm",
        ]
    ]
    .rolling(WINDOW)
    .mean()
    .dropna()
)

x = np.arange(len(rolling))

print()
print("=" * 70)
print("ROLLING TREND CORRELATIONS")
print("=" * 70)

for metric in [
    "heart_rate",
    "enhanced_speed",
    "cadence_spm",
    "EF",
    "speed_per_spm",
]:

    corr = np.corrcoef(
        x,
        rolling[metric]
    )[0, 1]

    print(f"{metric:<15} {corr:+.4f}")

# ----------------------------------------------------------------------
# Useful coaching summary
# ----------------------------------------------------------------------

print()
print("=" * 70)
print("COACHING METRICS")
print("=" * 70)

print(f"Half-HR Drift       : {hr_half:+.2f}%")
print(f"Half-Cadence Drift  : {cad_half:+.2f}%")
print(f"Half-EF Drift       : {ef_half:+.2f}%")
print(f"Half-Speed/SPM      : {sps_half:+.2f}%")
print(f"Aerobic Decoupling  : {decoupling:+.2f}%")

print()
