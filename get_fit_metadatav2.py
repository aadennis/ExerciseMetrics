"""Print the available FIT record fields relevant to run analysis.

This script opens a sample FIT file and prints the key/value pairs from the
first record message, excluding the fields in the EXCLUSIONS tuple.
Such fields are not relevant for me, right now.
The script is useful for discovering which columns are available before 
building more specialized analysis scripts.
"""

import fitdecode

EXCLUSIONS = ("unknown","stance","frac","cycle")

input_file = "data/5k_ACTIVITY.fit"

with fitdecode.FitReader(input_file) as f:
    for frame in f:
        if isinstance(frame, fitdecode.FitDataMessage) and frame.name == "record":
            data = {field.name: field.value for field in frame.fields}

            # Print the available columns in a stable, readable order.

            for name, value in sorted(data.items()):
                if not name.startswith(EXCLUSIONS):
                    print(f"{name}:{value}")
            break
