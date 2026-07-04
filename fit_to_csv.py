import fitdecode
import csv

DOUBLE_IF_STRIDE = True

def convert_fit_to_csv(input_file, output_file):
    rows = []

    with fitdecode.FitReader(input_file) as fit:
        for frame in fit:
            if isinstance(frame, fitdecode.FitDataMessage) and frame.name == "record":

                data = {f.name: f.value for f in frame.fields}

                cadence = data.get("cadence")
                frac = data.get("fractional_cadence", 0)
                timestamp = data.get("timestamp")

                if cadence is not None:
                    # Combine integer + fractional part
                    cadence_full = cadence + frac

                    # Convert to steps/min if needed
                    cadence_spm = cadence_full * 2 if DOUBLE_IF_STRIDE else cadence_full
                    step_length = data.get("step_length")
                    step_length = round(step_length / 1000.0,2) if step_length is not None else None

                    rows.append({
                        "timestamp": timestamp,
                        "orig_cadence": cadence,
                        "frac": frac,
                        "cadence_raw": cadence_full,
                        "cadence_spm": cadence_spm,
                        "enhanced_speed": data.get("enhanced_speed"),
                        "heart_rate": data.get("heart_rate"),
                        "step_length": step_length
                    })

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "orig_cadence",
                "frac",
                "cadence_raw",
                "cadence_spm",
                "enhanced_speed",
                "heart_rate",
                "step_length"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {output_file}")

def build_path(file) -> str:
    folder = "data"
    return f"{folder}/{file}"

if __name__ == "__main__":
  input_file = "run_recovery_5k_260701.fit"
  output_file = "cadence_output.csv"
  input_file = build_path(input_file)
  output_file = build_path(output_file)

  convert_fit_to_csv(input_file, output_file)
