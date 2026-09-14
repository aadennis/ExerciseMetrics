import csv
import fitdecode

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

input_file = r"d:/onedrive/Documents/_ActualDocuments/Exercise/Running/garmin-fit/2026-05-25-intervals.fit"
output_csv = r"d:/onedrive/Documents/_ActualDocuments/Exercise/Running/garmin-fit/2026-05-25-intervals.csv"

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def classify_lap(distance_m):
    """
    Categorise laps by distance.
    Adjust thresholds if future workouts use different distances.
    """

    if distance_m > 350:
        return "Warmup"

    if distance_m > 175:
        return "Active"

    if distance_m > 100:
        return "Recovery"

    return "Other"


def pace_string(pace_sec_per_km):
    mins = int(pace_sec_per_km // 60)
    secs = round(pace_sec_per_km % 60)

    if secs == 60:
        mins += 1
        secs = 0

    return f"{mins}:{secs:02d}"


# -----------------------------------------------------------------------------
# Extract laps
# -----------------------------------------------------------------------------

laps = []
interval_no = 0

with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if not isinstance(frame, fitdecode.FitDataMessage):
            continue

        if frame.name != "lap":
            continue

        values = {f.name: f.value for f in frame.fields}

        distance = values.get("total_distance", 0)
        elapsed = values.get("total_timer_time", 0)

        # Ignore Garmin's tiny session-end lap
        if distance < 50:
            continue

        lap_type = classify_lap(distance)

        if distance > 0:
            pace_sec_per_km = elapsed / distance * 1000
        else:
            pace_sec_per_km = None

        if lap_type == "Active":
            interval_no += 1

        if lap_type in ("Active", "Recovery"):
            interval = interval_no
        else:
            interval = ""

        laps.append(
            {
                "interval": interval,
                "type": lap_type,
                "distance_m": round(distance, 1),
                "time_s": round(elapsed, 1),
                "pace_s_per_km": round(pace_sec_per_km, 1),
                "pace": pace_string(pace_sec_per_km),
                "avg_hr": values.get("avg_heart_rate"),
                "start_time": values.get("start_time"),
            }
        )

# -----------------------------------------------------------------------------
# Write CSV
# -----------------------------------------------------------------------------

with open(output_csv, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "interval",
            "type",
            "distance_m",
            "time_s",
            "pace_s_per_km",
            "pace",
            "avg_hr",
            "start_time",
        ],
    )

    writer.writeheader()

    for row in laps:
        writer.writerow(row)

# -----------------------------------------------------------------------------
# Print summary
# -----------------------------------------------------------------------------

print()
print("Interval Type      Dist(m)   Time(s)   Pace     HR")
print("-" * 55)

for lap in laps:

    interval = str(lap["interval"]) if lap["interval"] != "" else ""

    print(
        f"{interval:>8} "
        f"{lap['type']:<10} "
        f"{lap['distance_m']:>8.0f} "
        f"{lap['time_s']:>9.1f} "
        f"{lap['pace']:>8} "
        f"{lap['avg_hr']}"
    )

print()
print(f"{len(laps)} laps written to:")
print(output_csv)

active = [r for r in laps if r["type"] == "Active"]
recovery = [r for r in laps if r["type"] == "Recovery"]

avg_active_pace = sum(r["pace_s_per_km"] for r in active) / len(active)
avg_recovery_pace = sum(r["pace_s_per_km"] for r in recovery) / len(recovery)

fastest_rep = min(active, key=lambda r: r["pace_s_per_km"])
slowest_rep = max(active, key=lambda r: r["pace_s_per_km"])

print("\nSUMMARY")
print("-------")
print(f"Active reps   : {len(active)}")
print(f"Recovery reps : {len(recovery)}")
print(f"Average active pace   : {avg_active_pace:.1f} s/km")
print(f"Average recovery pace : {avg_recovery_pace:.1f} s/km")
print(f"Fastest rep pace      : {fastest_rep['pace']}")
print(f"Slowest rep pace      : {slowest_rep['pace']}")