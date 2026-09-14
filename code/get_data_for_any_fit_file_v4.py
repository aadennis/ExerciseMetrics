import fitdecode

input_file = r"d:/onedrive/Documents/_ActualDocuments/Exercise/Running/garmin-fit/2026-05-25-intervals.fit"

wanted = {
    "timestamp",
    "start_time",
    "total_elapsed_time",
    "total_timer_time",
    "total_distance",
    "avg_speed",
    "max_speed",
    "avg_heart_rate",
    "lap_trigger",
}

lap_no = 0

with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if (
            isinstance(frame, fitdecode.FitDataMessage)
            and frame.name == "lap"
        ):

            lap_no += 1

            print(f"\n===== LAP {lap_no} =====")

            for field in frame.fields:

                if field.name in wanted:
                    print(f"{field.name:25s} {field.value}")