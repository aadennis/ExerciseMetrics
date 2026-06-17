import fitdecode
import csv

def extract_all_fields(frame) -> dict:
    return {f.name: f.value for f in frame.fields}

def main(fit_file):
    rows = []
    all_fields = set()

    with fitdecode.FitReader(fit_file) as fit:
        for frame in fit:
            if isinstance(frame, fitdecode.FitDataMessage) and frame.name == "record":
                data = extract_all_fields(frame)
                rows.append(data)
                all_fields.update(data.keys())

    # Ensure consistent column order
    all_fields = sorted(all_fields)

    # Write to CSV
    with open("output.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    run_file = "run_5kEmm_260616.fit"
    main(run_file)