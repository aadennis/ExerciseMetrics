import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt

# --- Load TCX file ---
file_path = "C:/temp/downloads/activity_23247479983.tcx.csv"   # <- change to your filename

tree = ET.parse(file_path)
root = tree.getroot()

# Garmin namespaces
NS_TC = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
NS_EXT = "http://www.garmin.com/xmlschemas/ActivityExtension/v2"

# -----------------------------
# 2. EXTRACT TRACKPOINT DATA
# -----------------------------
rows = []

for tp in root.iter(f"{{{NS_TC}}}Trackpoint"):
    time = tp.find(f"{{{NS_TC}}}Time")
    dist = tp.find(f"{{{NS_TC}}}DistanceMeters")
    speed = tp.find(f".//{{{NS_EXT}}}Speed")  # nested in extensions

    if time is not None and dist is not None and speed is not None:
        rows.append({
            "time": time.text,
            "distance": float(dist.text),
            "speed": float(speed.text)  # m/s
        })

# Build dataframe
df = pd.DataFrame(rows)

if df.empty:
    raise ValueError("No valid data found — check file or namespaces")

df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)

# -----------------------------
# 3. CONVERT TO PACE
# -----------------------------
# speed (m/s) -> pace (min/km)
df["pace"] = (1000 / df["speed"]) / 60

# -----------------------------
# 4. DEFINE FAST SEGMENTS
# -----------------------------
threshold = 6.5  # minutes per km

df["fast"] = df["pace"] < threshold

# -----------------------------
# 5. GROUP INTO STRIDE BLOCKS
# -----------------------------
# Create block IDs when fast/slow changes
df["block_id"] = (df["fast"] != df["fast"].shift()).cumsum()

# Keep only "fast" blocks
blocks = df[df["fast"]].groupby("block_id")

stride_results = []

for i, (_, seg) in enumerate(blocks, 1):

    # Filter out tiny noise spikes
    if len(seg) < 3:
        continue

    start_time = seg["time"].iloc[0]
    end_time = seg["time"].iloc[-1]

    duration = (end_time - start_time).total_seconds()
    distance = seg["distance"].iloc[-1] - seg["distance"].iloc[0]

    stride_results.append({
        "stride": i,
        "start": start_time,
        "end": end_time,
        "duration_s": duration,
        "distance_m": distance
    })

stride_df = pd.DataFrame(stride_results)

# -----------------------------
# 6. PRINT RESULTS
# -----------------------------
print("\nStride Summary:\n")
print(stride_df.to_string(index=False))

# -----------------------------
# 7. PLOT
# -----------------------------
plt.figure(figsize=(12, 6))

# Full pace curve
plt.plot(df["time"], df["pace"], color="lightgray", label="Pace")

# Highlight stride segments
for _, row in stride_df.iterrows():
    mask = (df["time"] >= row["start"]) & (df["time"] <= row["end"])
    plt.plot(df["time"][mask], df["pace"][mask], linewidth=3)

# Highlight all fast points
plt.scatter(
    df["time"][df["fast"]],
    df["pace"][df["fast"]],
    s=10,
    color="red",
    label="Faster than 6:30/km"
)

# Threshold line
plt.axhline(threshold, linestyle="--", label="6:30/km")

# Formatting
plt.gca().invert_yaxis()
plt.xlabel("Time")
plt.ylabel("Pace (min/km)")
plt.title("Pace Curve with Stride Segments")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()