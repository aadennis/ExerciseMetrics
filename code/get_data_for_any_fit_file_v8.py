import fitdecode
input_file = r"d:/onedrive/Documents/_ActualDocuments/Exercise/Running/garmin-fit/2026-05-25-intervals.fit"

with fitdecode.FitReader(input_file) as fit:

    for frame in fit:

        if (
            isinstance(frame, fitdecode.FitDataMessage)
            and frame.name == "record"
        ):

            print("\nFIRST RECORD\n")

            for field in frame.fields:
                print(f"{field.name:30s} {field.value}")

            break