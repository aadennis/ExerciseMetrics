"""Convert Garmin FIT activity data into a simplified CSV file.

This script reads a FIT file, extracts a subset of useful running metrics,
normalizes a few field values for reporting, and writes the results as CSV.
The output is intended for later analysis of running performance data such as
speed, altitude, cadence, heart rate, and pacing-related metrics.
"""

import csv
import fitdecode


def _normalize_value(data, orig_field_name) -> float:
    """Normalize a single FIT field before writing it to CSV.

    Some Garmin FIT fields are stored in units or formats that are inconvenient
    for downstream analysis, so this helper converts them into more readable
    values.
    """
    value = data.get(orig_field_name)
    if orig_field_name == "step_length" and value is not None:
        value = round(value / 1000.0, 2)
    if orig_field_name == "enhanced_altitude":
        value = round(value, 3)
    return value


def _build_normalized_row(data: dict, fields: dict) -> dict:
    """Create a CSV-ready row from a FIT record.

    Args:
        data: A dictionary containing raw field names and values from one FIT
            record frame.
        fields: Mapping of output column names to source FIT field names.

    Returns:
        A dictionary with normalized values for the CSV writer.
    """
    row = {name: _normalize_value(data, src) for name, src in fields.items()}
    cadence = row.get("cadence")
    fractional_cadence = data.get("fractional_cadence")
    if cadence is not None:
        row["cadence"] = (cadence + fractional_cadence) * 2
    return row


def convert_fit_to_csv(input_file, output_file):
    """Read a Garmin FIT file and write selected metrics to CSV.

    The FIT reader walks each "record" message in the source file and extracts a
    curated set of fields. These fields are normalized and stored in a CSV with a
    consistent column order suitable for analysis.

    Args:
        input_file: Path to the source FIT file.
        output_file: Path where the output CSV should be written.
    """
    rows: list = []
    fields = {
        "speed": "enhanced_speed",
        "altitude": "enhanced_altitude",
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
                "altitude",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {output_file}")


def build_path(file, is_output: bool) -> str:
    """Return a path under the project's data folders.

    Args:
        file: File name to append to the chosen directory.
        is_output: If True, store under the output directory; otherwise use the
            source data directory.

    Returns:
        A path string for the requested file.
    """
    folder = "data" if not is_output else "data/output"
    return f"{folder}/{file}"


if __name__ == "__main__":
    """Run the conversion using the default example data file."""
    input_file = "splits 5 July.fit"
    output_file = f"{input_file.rsplit('.', 1)[0]}-fit.csv"
    input_file = build_path(input_file, False)
    output_file = build_path(output_file, True)

    convert_fit_to_csv(input_file, output_file)
