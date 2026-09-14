from collections import Counter
import fitdecode

counter = Counter()

dir = "d:/onedrive/Documents/_ActualDocuments/Exercise/Running/garmin-fit"
input_file = f"{dir}/2026-05-25-intervals.fit"

with fitdecode.FitReader(input_file) as fit:
    for frame in fit:
        if isinstance(frame, fitdecode.FitDataMessage):
            counter[frame.name] += 1

print("\nMessage counts:\n")

for name, count in counter.most_common():
    print(f"{name:20s} {count}")