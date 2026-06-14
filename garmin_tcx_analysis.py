import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt

# --- Load TCX file ---
file_path = "C:/temp/downloads/activity_23247479983.tcx.csv"   # <- change to your filename


tree = ET.parse(file_path)
root = tree.getroot()

NS_TC = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
NS_EXT = "http://www.garmin.com/xmlschemas/ActivityExtension/v2"

# -----------------------------
# 2. EXTRACT DATA
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
# 3. ELAPSED TIME (seconds)
# -----------------------------
start_time = df["time"].iloc[0]
df["elapsed_s"] = (df["time"] - start_time).dt.total_seconds()

# -----------------------------
# 4. PACE CALCULATION
# -----------------------------
df["pace"] = (1000 / df["speed"]) / 60  # min/km

# -----------------------------
# 5. FAST SEGMENT DETECTION
# -----------------------------
threshold = 6.5
df["fast"] = df["pace"] < threshold

# -----------------------------
# 6. GROUP INTO STRIDE BLOCKS
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
        "start_s": start_t,
        "end_s": end_t,
        "duration_s": duration,
        "distance_m": distance
    })

stride_df = pd.DataFrame(stride_results)

# -----------------------------
# 7. PRINT RESULTS
# -----------------------------
print("\nStride Summary (Elapsed Time):\n")
print(stride_df.to_string(index=False))

# -----------------------------
# 8. PLOT
# -----------------------------
plt.figure(figsize=(12, 6))

# Full pace curve
plt.plot(df["elapsed_s"], df["pace"], color="lightgray", label="Pace")

# Highlight stride segments
for _, row in stride_df.iterrows():
    mask = (df["elapsed_s"] >= row["start_s"]) & (df["elapsed_s"] <= row["end_s"])
    plt.plot(df["elapsed_s"][mask], df["pace"][mask], linewidth=3)

# Fast points
plt.scatter(
    df["elapsed_s"][df["fast"]],
    df["pace"][df["fast"]],
    s=10,
    color="red",
    label="Faster than 6:30/km"
)

# Threshold
plt.axhline(threshold, linestyle="--", label="6:30/km")

# Formatting
plt.gca().invert_yaxis()
plt.xlabel("Elapsed Time (seconds)")
plt.ylabel("Pace (min/km)")
plt.title("Pace Curve with Stride Segments (Elapsed Time)")
plt.legend()
plt.tight_layout()

plt.show()