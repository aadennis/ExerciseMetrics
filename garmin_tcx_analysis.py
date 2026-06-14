import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt

# --- Load TCX file ---
file_path = "C:/temp/downloads/activity_23247479983.tcx.csv"   # <- change to your filename
tree = ET.parse(file_path)
root = tree.getroot()

# Namespaces
ns_tc = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
ns_ext = "http://www.garmin.com/xmlschemas/ActivityExtension/v2"

# --- Extract trackpoint data ---
rows = []

for tp in root.iter(f"{{{ns_tc}}}Trackpoint"):
    time = tp.find(f"{{{ns_tc}}}Time")
    dist = tp.find(f"{{{ns_tc}}}DistanceMeters")
    speed = tp.find(f".//{{{ns_ext}}}Speed")  # IMPORTANT: nested

    if time is not None and dist is not None and speed is not None:
        rows.append({
            "time": time.text,
            "distance": float(dist.text),
            "speed": float(speed.text)  # m/s
        })

# --- Build dataframe ---
df = pd.DataFrame(rows)

df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time")

# Convert speed (m/s) -> pace (min/km)
df["pace"] = (1000 / df["speed"]) / 60

# --- Define threshold ---
threshold = 6.5  # minutes per km

# Identify fast segments
df["fast"] = df["pace"] < threshold

# --- Plot ---
plt.figure(figsize=(10, 5))

# Full pace curve
plt.plot(df["time"], df["pace"], label="Pace")

# Highlight fast segments
plt.scatter(
    df["time"][df["fast"]],
    df["pace"][df["fast"]],
    s=10,
    label="Faster than 6:30/km"
)

# Threshold line
plt.axhline(threshold, linestyle="--", label="6:30/km")

# Style
plt.gca().invert_yaxis()  # faster = higher
plt.xlabel("Time")
plt.ylabel("Pace (min/km)")
plt.title("Run Pace with Stride Highlights")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()