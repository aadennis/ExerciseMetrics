import csv
from statistics import mean
import fitdecode

input_file = r"d:/onedrive/Documents/_ActualDocuments/Exercise/Running/garmin-fit/2026-05-25-intervals.fit"

output_csv = input_file.replace(".fit", "_dynamics.csv")

# ------------------------------------------------------------------
# Read lap boundaries
# ------------------------------------------------------------------

laps = []

with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if (
            isinstance(frame, fitdecode.FitDataMessage)
            and frame.name == "lap"
        ):

            vals = {f.name: f.value for f in frame.fields}

            dist = vals.get("total_distance", 0)

            # Ignore Garmin session-end lap
            if dist < 50:
                continue

            laps.append(
                {
                    "start": vals.get("start_time"),
                    "distance": dist,
                    "time_s": vals.get("total_timer_time"),
                    "avg_hr": vals.get("avg_heart_rate"),
                }
            )

# ------------------------------------------------------------------
# Read workout definition
# ------------------------------------------------------------------

workout_steps = []

with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if (
            isinstance(frame, fitdecode.FitDataMessage)
            and frame.name == "workout_step"
        ):

            vals = {f.name: f.value for f in frame.fields}

            workout_steps.append(vals)

print("\nWorkout Steps Found:")
for i, step in enumerate(workout_steps):
    print(
        i,
        step.get("intensity"),
        step.get("duration_type"),
        step.get("duration_distance"),
        step.get("repeat_steps"),
    )            

# ------------------------------------------------------------------
# Calculate lap end times
# ------------------------------------------------------------------

for i in range(len(laps) - 1):
    laps[i]["end"] = laps[i + 1]["start"]

laps[-1]["end"] = None

# ------------------------------------------------------------------
# Build lap sequence from workout definition
# ------------------------------------------------------------------

lap_types = []

for step in workout_steps:

    intensity = step.get("intensity")
    repeat_steps = step.get("repeat_steps")

    if intensity == "warmup":
        lap_types.append("Warmup")

    elif intensity == "active":
        active_step = "Active"

    elif intensity == "recovery":
        recovery_step = "Recovery"

    elif repeat_steps is not None:

        for _ in range(repeat_steps):
            lap_types.append(active_step)
            lap_types.append(recovery_step)

# ------------------------------------------------------------------
# Apply classifications
# ------------------------------------------------------------------

if len(lap_types) != len(laps):
    print(
        f"WARNING: Workout definition generated "
        f"{len(lap_types)} lap types but file contains "
        f"{len(laps)} laps"
    )

for lap, lap_type in zip(laps, lap_types):

    lap["type"] = lap_type

# ------------------------------------------------------------------
# Assign interval numbers
# ------------------------------------------------------------------

interval_no = 0

for lap in laps:

    if lap["type"] == "Warmup":
        lap["interval"] = ""

    elif lap["type"] == "Active":
        interval_no += 1
        lap["interval"] = interval_no

    elif lap["type"] == "Recovery":
        lap["interval"] = interval_no

# ------------------------------------------------------------------
# Create storage for dynamics
# ------------------------------------------------------------------

for lap in laps:

    lap["stance_time_vals"] = []
    lap["vertical_osc_vals"] = []
    lap["vertical_ratio_vals"] = []
    lap["step_length_vals"] = []
    lap["cadence_vals"] = []

# ------------------------------------------------------------------
# Read record stream
# ------------------------------------------------------------------

with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if not (
            isinstance(frame, fitdecode.FitDataMessage)
            and frame.name == "record"
        ):
            continue

        vals = {f.name: f.value for f in frame.fields}

        ts = vals.get("timestamp")

        if ts is None:
            continue

        for lap in laps:

            start = lap["start"]
            end = lap["end"]

            if ts < start:
                continue

            if end and ts >= end:
                continue

            if vals.get("stance_time") is not None:
                lap["stance_time_vals"].append(vals["stance_time"])

            if vals.get("vertical_oscillation") is not None:
                lap["vertical_osc_vals"].append(vals["vertical_oscillation"])

            if vals.get("vertical_ratio") is not None:
                lap["vertical_ratio_vals"].append(vals["vertical_ratio"])

            if vals.get("step_length") is not None:
                lap["step_length_vals"].append(vals["step_length"])

            cad = vals.get("cadence")
            frac = vals.get("fractional_cadence")

            if cad is not None:

                true_cadence = float(cad)

                if frac is not None:
                    true_cadence += float(frac)

                true_cadence *= 2

                lap["cadence_vals"].append(true_cadence)

             

            break

# ------------------------------------------------------------------
# Aggregate
# ------------------------------------------------------------------

for lap in laps:

    lap["gct_ms"] = round(mean(lap["stance_time_vals"]), 1) \
        if lap["stance_time_vals"] else None

    lap["vo_mm"] = round(mean(lap["vertical_osc_vals"]), 1) \
        if lap["vertical_osc_vals"] else None

    lap["vr_pct"] = round(mean(lap["vertical_ratio_vals"]), 2) \
        if lap["vertical_ratio_vals"] else None

    lap["step_mm"] = round(mean(lap["step_length_vals"]), 1) \
        if lap["step_length_vals"] else None

    lap["cadence"] = round(mean(lap["cadence_vals"]), 1) \
        if lap["cadence_vals"] else None

# ------------------------------------------------------------------
# Export
# ------------------------------------------------------------------

with open(output_csv, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow(
        [
            "interval",
            "type",
            "distance_m",
            "time_s",
            "avg_hr",
            "cadence",
            "gct_ms",
            "vert_osc_mm",
            "vert_ratio_pct",
            "step_length_mm",
        ]
    )

    for lap in laps:

        writer.writerow(
            [
                lap["interval"],
                lap["type"],
                round(lap["distance"], 1),
                round(lap["time_s"], 1),
                lap["avg_hr"],
                lap["cadence"],
                lap["gct_ms"],
                lap["vo_mm"],
                lap["vr_pct"],
                lap["step_mm"],
            ]
        )

print(f"Written: {output_csv}")