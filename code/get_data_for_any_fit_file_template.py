import fitdecode
from pathlib import Path
import os

input_dir = Path(os.environ["garmin-fit-dir"])
input_file = f"{input_dir}/2026-05-27-intervals.fit"


laps = []

with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if (
            isinstance(frame, fitdecode.FitDataMessage)
            and frame.name == "lap"
        ):

            values = {
                f.name: f.value
                for f in frame.fields
            }

            dist = values.get("total_distance", 0)
            secs = values.get("total_timer_time", 0)

            if dist > 0:
                pace_sec_km = secs / dist * 1000

                laps.append({
                    "distance": dist,
                    "time": secs,
                    "pace_sec_km": pace_sec_km,
                    "hr": values.get("avg_heart_rate")
                })

print(
    "Lap  Dist  Time(s)  Pace(min/km)  HR"
)

for i, lap in enumerate(laps, start=1):

    mins = int(lap["pace_sec_km"] // 60)
    secs = round(lap["pace_sec_km"] % 60)

    print(
        f"{i:>3}  "
        f"{lap['distance']:>5.0f}  "
        f"{lap['time']:>7.1f}  "
        f"{mins}:{secs:02d}  "
        f"{lap['hr']}"
    )
