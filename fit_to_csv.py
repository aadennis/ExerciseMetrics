import csv
import fitdecode


def _normalize_value(data, orig_field_name) -> float:
    value = data.get(orig_field_name)
    if orig_field_name == "step_length" and value is not None:
        value = round(value / 1000.0, 2)
    if orig_field_name == "enhanced_altitude":
        value = round(value, 3)
    return value


def _build_normalized_row(data: dict, fields: dict) -> dict:
    row = {name: _normalize_value(data, src) for name, src in fields.items()}
    cadence = row.get("cadence")
    fractional_cadence = data.get("fractional_cadence")
    if cadence is not None:
        row["cadence"] = (cadence + fractional_cadence) * 2
    return row


def convert_fit_to_csv(input_file, output_file):
    rows:list = []
    fields = {
        "speed": "enhanced_speed",
        "altitude":"enhanced_altitude",
        "heart_rate": "heart_rate",
        "step_length": "step_length",
        "distance": "distance",
        "vertical_oscillation": "vertical_oscillation",
        "vertical_ratio": "vertical_ratio",
        "contact_time": "stance_time",
        "cadence": "cadence",
        "timestamp": "timestamp",
    }

    with fitdecode.FitReader(input_file) as fit:
        for frame in fit:
            if not (
                isinstance(frame, fitdecode.FitDataMessage) and frame.name == "record"
            ):
                continue

            input_datarow = {field.name: field.value for field in frame.fields}
            rows.append(_build_normalized_row(input_datarow, fields))

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "cadence",
                "speed",
                "heart_rate",
                "step_length",
                "distance",
                "vertical_oscillation",
                "vertical_ratio",
                "contact_time",
                "altitude"
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {output_file}")


def build_path(file, is_output: bool) -> str:
    folder = "data" if not is_output else "data/output"
    return f"{folder}/{file}"


if __name__ == "__main__":
    input_file = "5k_pb_29m34_ACTIVITY.fit"
    output_file = f"{input_file.rsplit('.', 1)[0]}-fit.csv"
    input_file = build_path(input_file, False)
    output_file = build_path(output_file, True)

    convert_fit_to_csv(input_file, output_file)
