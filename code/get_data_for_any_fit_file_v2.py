import fitdecode

input_file = r"d:/onedrive/Documents/_ActualDocuments/Exercise/Running/garmin-fit/2026-05-25-intervals.fit"

interesting = {
    "workout",
    "workout_step",
    "lap",
    "split",
    "split_summary",
    "session",
    "event",
}

with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if not isinstance(frame, fitdecode.FitDataMessage):
            continue

        if frame.name not in interesting:
            continue

        print("\n" + "=" * 80)
        print(frame.name.upper())

        for field in frame.fields:
            print(f"{field.name:30s} {field.value}")