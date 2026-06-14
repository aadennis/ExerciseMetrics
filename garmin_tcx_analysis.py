import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt

# --- Load TCX file ---
file_path = "C:/temp/downloads/activity_23247479983.tcx.csv"   # <- change to your filename



start_offset = 1200        # seconds from start (e.g. 600)
end_offset = 1800      # seconds (e.g. 900) or None = full run

threshold = 6.5         # min/km

# -----------------------------
# LOAD TCX
# -----------------------------
tree = ET.parse(file_path)
root = tree.getroot()

NS_TC = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
NS_EXT = "http://www.garmin.com/xmlschemas/ActivityExtension/v2"

# -----------------------------
# EXTRACT DATA
# -----------------------------
rows = []

for tp in root.iter(f"{{{NS_TC}}}Trackpoint"):
    time = tp.find(f"{{{NS_TC}}}Time")
    dist = tp.find(f"{{{NS_TC}}}DistanceMeters")
    speed = tp.find(f".//{{{NS_EXT}}}Speed")

    if time is not None and dist is not None and speed is not None:
        rows.append({
            "time": time.text,
            "distance": float(dist.text),
            "speed": float(speed.text)
        })

df = pd.DataFrame(rows)

if df.empty:
    raise ValueError("No valid data found")

df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)

# -----------------------------
# ELAPSED TIME
# -----------------------------
start_time = df["time"].iloc[0]
df["elapsed_s"] = (df["time"] - start_time).dt.total_seconds()

# -----------------------------
# APPLY USER WINDOW
# -----------------------------
if end_offset is None:
    end_offset = df["elapsed_s"].max()

df = df[(df["elapsed_s"] >= start_offset) & (df["elapsed_s"] <= end_offset)].copy()

if df.empty:
    raise ValueError("No data in selected time window")

# Re-zero time so plot starts at 0
df["elapsed_s"] = df["elapsed_s"] - df["elapsed_s"].iloc[0]

# -----------------------------
# PACE
# -----------------------------
df["pace"] = (1000 / df["speed"]) / 60

# -----------------------------
# FAST SEGMENTS
# -----------------------------
df["fast"] = df["pace"] < threshold

# -----------------------------
# GROUP STRIDES
# -----------------------------
df["block_id"] = (df["fast"] != df["fast"].shift()).cumsum()

blocks = df[df["fast"]].groupby("block_id")

stride_results = []

for i, (_, seg) in enumerate(blocks, 1):

    if len(seg) < 3:
        continue

    start_t = seg["elapsed_s"].iloc[0]
    end_t = seg["elapsed_s"].iloc[-1]

    duration = end_t - start_t
    distance = seg["distance"].iloc[-1] - seg["distance"].iloc[0]

    stride_results.append({
        "stride": i,
        "start_s": round(start_t, 1),
        "end_s": round(end_t, 1),
        "duration_s": round(duration, 1),
        "distance_m": round(distance, 1)
    })

stride_df = pd.DataFrame(stride_results)

# -----------------------------
# OUTPUT
# -----------------------------
print("\nStride Summary (within selected window):\n")
print(stride_df.to_string(index=False))

# -----------------------------
# PLOT
# -----------------------------
plt.figure(figsize=(12, 6))

# Full curve
plt.plot(df["elapsed_s"], df["pace"], color="lightgray", label="Pace")

# Highlight strides
for _, row in stride_df.iterrows():
    mask = (df["elapsed_s"] >= row["start_s"]) & (df["elapsed_s"] <= row["end_s"])
    plt.plot(df["elapsed_s"][mask], df["pace"][mask], linewidth=3)

# Fast points
plt.scatter(
    df["elapsed_s"][df["fast"]],
    df["pace"][df["fast"]],
    s=10,
    color="red",
    label="Faster than threshold"
)

# Threshold
plt.axhline(threshold, linestyle="--", label=f"{threshold} min/km")

# Formatting
plt.gca().invert_yaxis()
plt.xlabel("Elapsed Time (seconds)")
plt.ylabel("Pace (min/km)")
plt.title(f"Pace Curve ({start_offset}s to {end_offset}s)")
plt.legend()
plt.tight_layout()

plt.show()
