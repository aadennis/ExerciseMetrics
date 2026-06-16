import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import os

'''
  get_pace: given a time and a distance covered, 
  return the pace. Inputs are in seconds and metres,
  return value is seconds per kilometer
'''
def get_pace_as_seconds(time_in_secs: float, distance_in_mtrs: float) -> float:
    return round(time_in_secs * (1000/ distance_in_mtrs) , 2)

def seconds_to_minutes(time_in_secs: float) -> str:
    whole_minutes, remaining_seconds = divmod(int(time_in_secs), 60)
    return f"{whole_minutes}:{remaining_seconds:02d}"

# --- Load TCX file ---
dir = r"D:\onedrive\Documents\_ActualDocuments\Exercise\Running\Garmin splits/tcx"
file = "run_5kEmm_260616.tcx"
file_path = f"{dir}/{file}"   # <- change to your filename
print(file_path)

file_name = os.path.basename(file_path)


start_offset = 1200        # seconds from start (e.g. 600)
end_offset = 1800      # seconds (e.g. 900) or None = full run
threshold = 6.5         # min/km

# -----------------------------
# LOAD TCX
# -----------------------------
# if start_offset is None:
#     start_offset = 0



tree = ET.parse(file_path)
root = tree.getroot()

NS_TC = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
NS_EXT = "http://www.garmin.com/xmlschemas/ActivityExtension/v2"

# -----------------------------
# EXTRACT DATA
# -----------------------------
activity = root.find(f".//{{{NS_TC}}}Activity")
activity_id = activity.find(f"{{{NS_TC}}}Id") if activity is not None else None

date_str = ""
if activity_id is not None and activity_id.text is not None:
    date = pd.to_datetime(activity_id.text)
    date_str = date.strftime("%Y-%m-%d %H:%M")

creator = root.find(f".//{{{NS_TC}}}Creator")
device_name = "Unknown device"

if creator is not None:
    name_elem = creator.find(f"{{{NS_TC}}}Name")
    if name_elem is not None:
        device_name = name_elem.text
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
        "distance_m": round(distance, 1),
        "pace mins/km": seconds_to_minutes(get_pace_as_seconds(duration, distance))
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
#plt.title(f"Pace Curve ({start_offset}s to {end_offset}s)")
plt.title(f"{device_name} | {date_str}\nPace Curve ({start_offset} secs to {end_offset} secs)")


plt.gca().text(
  0.01, 0.01,
  file_name,
  transform=plt.gca().transAxes,
  fontsize=9,
  verticalalignment='bottom'
)
plt.legend()
plt.tight_layout()

plt.show()
