import fitdecode
import csv

RUN_FILE = "run_5kEmm_260616.fit"

rows = []

with fitdecode.FitReader(RUN_FILE) as fit:
    for frame in fit:
        if isinstance(frame, fitdecode.FitDataMessage) and frame.name == "record":
            data = {f.name: f.value for f in frame.fields}
            cadence = data.get('cadence')
            heart_rate = data.get('heart_rate')
            rows.append({'cadence': cadence, 'heart_rate': heart_rate})

print('22')