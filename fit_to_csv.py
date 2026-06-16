import fitdecode
import csv

INPUT_FILE = "run_5kEmm_260616.fit"
OUTPUT_FILE = "cadence_output.csv"

# If your data shows ~70–80, set this to True to convert to steps/min
DOUBLE_IF_STRIDE = True

rows = []

with fitdecode.FitReader(INPUT_FILE) as fit:
    for frame in fit:
        if isinstance(frame, fitdecode.FitDataMessage):
            if frame.name == "record":
                timestamp = frame.get_value("timestamp")
                cadence = frame.get_value("cadence")
                pace = frame.get_value("speed")
                heart_rate = frame.get_value("heart_rate")

                if cadence is not None:
                    # Convert stride → steps if needed
                    cadence_spm = cadence * 2 if DOUBLE_IF_STRIDE else cadence

                    rows.append({
                        "timestamp": timestamp,
                        "cadence_raw": cadence,
                        "cadence_spm": cadence_spm,
                        "pace": pace,
                        "heart_rate": heart_rate
                    })

# Write CSV
with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["timestamp", "cadence_raw", "cadence_spm","pace","heart_rate"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} rows to {OUTPUT_FILE}")