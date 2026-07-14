import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/full 6 July-fit.csv")

# --- shape data ---
# Remove stop periods (cadence = 0)
df = df[df["cadence_spm"] > 0].copy()
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Heart rate scaled to cadence range (for visual overlay)
hr = df["heart_rate"]
hr_scaled = (hr - hr.min()) / (hr.max() - hr.min())
hr_scaled = hr_scaled * (df["cadence_spm"].max() - df["cadence_spm"].min()) + df["cadence_spm"].min()

# --- Plot ---
fig, ax1 = plt.subplots(figsize=(12,5))

# Cadence (primary axis)
ax1.plot(df["timestamp"], df["cadence_spm"],
         color="tab:blue", label="Cadence")
ax1.set_ylabel("Cadence (spm)")

ax2 = ax1.twinx()
ax2.set_ylabel("Speed (m/s)")

# Speed (secondary axis)
ax2.plot(df["timestamp"], df["enhanced_speed"],
         color="tab:orange", linestyle="--", label="Speed")

ax1.plot(df["timestamp"], hr_scaled,
         color="tab:green", linestyle=":", linewidth=2,
         label="HR (scaled)")

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.title("Cadence vs Speed vs Heart Rate")
plt.xlabel("Time")
plt.tight_layout()
plt.show()

