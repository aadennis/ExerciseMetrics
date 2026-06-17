import fitdecode
import csv

RUN_FILE = "run_5kEmm_260616.fit"
FIELDS = ["cadence", "heart_rate"]


def extract_fields(frame, fields):
    return {f.name: f.value for f in frame.fields if f.name in fields}


rows = []

with fitdecode.FitReader(RUN_FILE) as fit:
    for frame in fit:
        if isinstance(frame, fitdecode.FitDataMessage) and frame.name == "record":
            rows.append(extract_fields(frame, FIELDS))

print("22")
