import csv
import fitdecode

def _normalize_value(data, field_name):
    value = data.get(field_name)
    if field_name == "step_length" and value is not None:
        value = round(value / 1000.0, 2)
    return value


def convert_fit_to_csv(input_file, output_file):
    rows = []
    fields = {
        "speed": "enhanced_speed",
        "heart_rate": "heart_rate",
        "step_length": "step_length",
        "distance": "distance",
        "vertical_oscillation": "vertical_oscillation",
        "vertical_ratio": "vertical_ratio",
        "stance_time": "stance_time",
        "fractional_cadence": "fractional_cadence"
    }

    with fitdecode.FitReader(input_file) as fit:
        for frame in fit:
            if not (
                isinstance(frame, fitdecode.FitDataMessage) and frame.name == "record"
            ):
                continue

            data = {field.name: field.value for field in frame.fields}
            cadence = data.get("cadence")
            if cadence is None:
                continue

            frac = data.get("fractional_cadence", 0)
            cadence_spm = 2 * (cadence + frac)
            
            rows.append(
                {
                    "timestamp": data.get("timestamp"),
                    "cadence_spm": cadence_spm,
                    **{
                        name: _normalize_value(data, src)
                        for name, src in fields.items()
                    },
                }
            )

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "cadence_spm",
                "speed",
                "heart_rate",
                "step_length",
                "distance",
                "vertical_oscillation",
                "vertical_ratio",
                "stance_time",
                "fractional_cadence"
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {output_file}")


def build_path(file, is_output: bool) -> str:
    folder = "data" if not is_output else "data/output"
    return f"{folder}/{file}"


if __name__ == "__main__":
    input_file = "3August_ACTIVITY.fit"
    output_file = f"{input_file.rsplit('.', 1)[0]}-fit.csv"
    input_file = build_path(input_file, False)
    output_file = build_path(output_file, True)

    convert_fit_to_csv(input_file, output_file)
