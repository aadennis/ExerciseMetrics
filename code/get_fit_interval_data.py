import csv
import os
import fitdecode
from pathlib import Path
from statistics import mean

garmin_fit_dir = Path(os.environ["garmin-fit-dir"])
input_file = f"{garmin_fit_dir}/2026-09-15-intervals.fit"
output_csv = input_file.replace(".fit", "_dynamics.csv")

# ------------------------------------------------------------------
# Read lap boundaries
# ------------------------------------------------------------------

laps = []

for frame in fitdecode.FitReader(input_file):

    if (
        isinstance(frame, fitdecode.FitDataMessage)
        and frame.name == "record"
    ):

        vals = {f.name: f.value for f in frame.fields}

        print(
            vals.get("timestamp"),
            vals.get("distance")
        )

        break

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
                    "wkt_step_index": vals.get("wkt_step_index"),
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
    "msg=", step.get("message_index"),
    "intensity=", step.get("intensity"),
    "duration_step=", step.get("duration_step"),
    "repeat_steps=", step.get("repeat_steps"),
    )     

# for i, step in enumerate(workout_steps):
#     if step.get("repeat_steps") is not None:
#         print(f"\nSTEP {i}")

#         for k, v in step.items():
#            print(f"  {k:30s} {v}")
    
for step in workout_steps:

    if step.get("duration_step") is not None:

        ref = step["duration_step"]

        print(
            f"\nRepeat step {step['message_index']} "
            f"references step {ref}:"
        )

        print(workout_steps[ref])

for i, lap in enumerate(laps):
    print(i, lap["wkt_step_index"])



# ------------------------------------------------------------------
# Calculate lap end times
# ------------------------------------------------------------------

for i in range(len(laps) - 1):
    laps[i]["end"] = laps[i + 1]["start"]

laps[-1]["end"] = None

for lap in laps:

    idx = lap["wkt_step_index"]

    lap["type"] = workout_steps[idx].get("intensity")

for i, lap in enumerate(laps):
    print(i, lap["type"])    


# ------------------------------------------------------------------
# Assign interval numbers
# ------------------------------------------------------------------

interval_no = 0

for lap in laps:

    if lap["type"] == "warmup":
        lap["interval"] = ""

    elif lap["type"] == "active":
        interval_no += 1
        lap["interval"] = interval_no

    elif lap["type"] == "recovery":
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

    lap["step_mtr"] = round(mean(lap["step_length_vals"])/1000, 2) \
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
            "step_length_mtr",
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
                lap["step_mtr"],
            ]
        )

print(f"Written: {output_csv}")