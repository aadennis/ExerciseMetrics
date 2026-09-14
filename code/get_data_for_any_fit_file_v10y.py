import fitdecode
input_file = r"d:/onedrive/Documents/_ActualDocuments/Exercise/Running/garmin-fit/2026-05-25-intervals.fit"



with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if (
            isinstance(frame, fitdecode.FitDataMessage)
            and frame.name == "record"
        ):

            values = {f.name: f.value for f in frame.fields}

            if values.get("cadence", 0) > 0:

                print("\nFIRST MOVING RECORD\n")

                for name in (
                    "timestamp",
                    "distance",
                    "enhanced_speed",
                    "heart_rate",
                    "cadence",
                    "vertical_oscillation",
                    "vertical_ratio",
                    "stance_time",
                    "stance_time_percent",
                    "stance_time_balance",
                    "step_length",
                ):
                    print(f"{name:25s} {values.get(name)}")

                break