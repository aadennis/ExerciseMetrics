import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_fit_per_km(fit_file):
    print(f"input file is {fit_file}")

    # --------------------------------------------------
    # Load data
    # --------------------------------------------------

    df = pd.read_csv(fit_file)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # elapsed time
    df["elapsed_s"] = (
        df["timestamp"] - df["timestamp"].iloc[0]
    ).dt.total_seconds()

    # pace in sec/km
    df["pace_sec_km"] = 1000 / df["speed"]

    # --------------------------------------------------
    # Helper function
    # --------------------------------------------------

    def pace_to_str(sec):
        mins = int(sec // 60)
        secs = int(round(sec % 60))
        return f"{mins}:{secs:02d}"

    # --------------------------------------------------
    # 1. KM SPLITS
    # --------------------------------------------------

    kms = [1000, 2000, 3000, 4000, 5000]

    splits = []

    prev_time = 0

    for km in kms:
        idx = (df["distance"] - km).abs().idxmin()

        current_time = df.loc[idx, "elapsed_s"]

        split_time = current_time - prev_time

        splits.append({
            "km": km // 1000,
            "split_s": split_time,
            "split_pace": pace_to_str(split_time)
        })

        prev_time = current_time

    splits_df = pd.DataFrame(splits)

    print("\nKM SPLITS")
    print(splits_df)

    # --------------------------------------------------
    # 2. SUMMARY TABLE
    # --------------------------------------------------

    distance = df["distance"].max()

    elapsed = df["elapsed_s"].iloc[-1]

    avg_speed = df["speed"].mean()

    avg_pace = 1000 / avg_speed

    summary = pd.DataFrame([{
        "Distance_m": round(distance, 1),
        "Time_min": round(elapsed / 60, 2),
        "Avg Pace": pace_to_str(avg_pace),
        "Avg HR": round(df["heart_rate"].mean(), 1),
        "Max HR": int(df["heart_rate"].max()),
        "Avg Cadence": round(df["cadence_spm"].mean(), 1),
        "Avg Step Length": round(df["step_length"].mean(), 3)
    }])

    print("\nSUMMARY")
    print(summary)

    # --------------------------------------------------
    # 3. CHARTS
    # --------------------------------------------------

    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    axs[0].plot(df["distance"]/1000, df["pace_sec_km"])
    axs[0].invert_yaxis()
    axs[0].set_ylabel("Pace sec/km")
    axs[0].set_title("Pace")

    axs[1].plot(df["distance"]/1000, df["heart_rate"], color="red")
    axs[1].set_ylabel("Heart Rate")

    axs[2].plot(df["distance"]/1000, df["cadence_spm"], color="green")
    axs[2].set_ylabel("Cadence")
    axs[2].set_xlabel("Distance (km)")

    plt.tight_layout()
    plt.savefig("5k_analysis_charts.png", dpi=150)

    # --------------------------------------------------
    # 4. FINISH KICK ANALYSIS
    # --------------------------------------------------

    final500 = df[df["distance"] >= (distance - 500)]

    before500 = df[
        (df["distance"] >= distance - 1500) &
        (df["distance"] < distance - 500)
    ]

    kick_speed_gain = (
        final500["speed"].mean() -
        before500["speed"].mean()
    )

    kick_stride_gain = (
        final500["step_length"].mean() -
        before500["step_length"].mean()
    )

    kick_cadence_gain = (
        final500["cadence_spm"].mean() -
        before500["cadence_spm"].mean()
    )

    print("\nFINAL 500m KICK")

    print(f"Speed gain        : {kick_speed_gain:.3f} m/s")
    print(f"Cadence change    : {kick_cadence_gain:.2f} spm")
    print(f"Stride change     : {kick_stride_gain:.3f} m")

    # --------------------------------------------------
    # 5. CORRELATION ANALYSIS
    # --------------------------------------------------

    corr_cols = [
        "speed",
        "heart_rate",
        "cadence_spm",
        "step_length"
    ]

    corr = df[corr_cols].corr()

    print("\nCORRELATION MATRIX")
    print(corr)

    # efficiency score
    df["efficiency"] = df["speed"] / df["heart_rate"]

    print("\nEFFICIENCY")

    print(
        f"Mean speed/HR ratio: "
        f"{df['efficiency'].mean():.4f}"
    )

    # --------------------------------------------------
    # NEGATIVE SPLIT TEST
    # --------------------------------------------------

    first_half = df[df["distance"] <= 2500]
    second_half = df[df["distance"] > 2500]

    pace1 = 1000 / first_half["speed"].mean()
    pace2 = 1000 / second_half["speed"].mean()

    print("\nHALF COMPARISON")

    print("First half pace :", pace_to_str(pace1))
    print("Second half pace:", pace_to_str(pace2))

    if pace2 < pace1:
        print("NEGATIVE SPLIT: YES")
    else:
        print("NEGATIVE SPLIT: NO")
    
    print(f"input file is [{fit_file}]")

if __name__ == "__main__":
    CSV_FILE = "data/output/3August_ACTIVITY-fit.csv"
    get_fit_per_km(CSV_FILE)
