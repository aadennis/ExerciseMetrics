import pandas as pd
import matplotlib.pyplot as plt

# Load your file
df = pd.read_csv("cadence_output.csv")

# Remove stop periods (cadence = 0)
df = df[df["cadence_spm"] > 0].copy()

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# --- Plot ---
fig, ax1 = plt.subplots(figsize=(12,5))

# Cadence (primary axis)
ax1.plot(df["timestamp"], df["cadence_spm"], label="Cadence (spm)", linewidth=1.5)
ax1.set_ylabel("Cadence (spm)")

# Speed (secondary axis)
ax2 = ax1.twinx()
ax2.plot(df["timestamp"], df["enhanced_speed"], linestyle="--", label="Speed (m/s)")
ax2.set_ylabel("Speed (m/s)")

# Heart rate scaled to cadence range (for visual overlay)
hr = df["heart_rate"]
hr_scaled = (hr - hr.min()) / (hr.max() - hr.min())
hr_scaled = hr_scaled * (df["cadence_spm"].max() - df["cadence_spm"].min()) + df["cadence_spm"].min()

ax1.plot(df["timestamp"], hr_scaled, linestyle=":", label="HR (scaled)")

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.title("Cadence vs Speed vs Heart Rate")
plt.xlabel("Time")
plt.tight_layout()
plt.show()

