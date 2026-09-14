import fitdecode

input_file = r"d:/onedrive/Documents/_ActualDocuments/Exercise/Running/garmin-fit/2026-05-25-intervals.fit"


laps = []

with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if (
            isinstance(frame, fitdecode.FitDataMessage)
            and frame.name == "lap"
        ):

            values = {f.name: f.value for f in frame.fields}

            dist = values.get("total_distance", 0)
            secs = values.get("total_timer_time", 0)

            if dist < 50:
                continue

            pace_sec_km = secs / dist * 1000

            if dist >= 350:
                lap_type = "Warmup"
            elif dist >= 175:
                lap_type = "Active"
            else:
                lap_type = "Recovery"

            laps.append(
                {
                    "type": lap_type,
                    "distance_m": round(dist, 1),
                    "time_s": round(secs, 1),
                    "pace_s_per_km": round(pace_sec_km, 1),
                    "hr": values.get("avg_heart_rate"),
                }
            )

for i, lap in enumerate(laps, start=1):
    print(i, lap)