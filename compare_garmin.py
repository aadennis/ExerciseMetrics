import pandas as pd
import re
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.chart import LineChart, Reference

# === FILES ===
file1 = "run_260608_cadence.csv"
file2 = "run_Cadence_260610.csv"
output_file = "garmin_analysis.xlsx"

# === HELPERS ===
def extract_date(filename):
    match = re.search(r'(\d{6})', filename)
    if match:
        d = match.group(1)
        return f"20{d[:2]}-{d[2:4]}-{d[4:]}"
    return "Unknown"


def load_file(path):
    df = pd.read_csv(path)

    # Remove summary row
    df = df[df["Laps"] != "Summary"]

    # Remove tiny final lap (<0.5 km)
    df = df[df["Distance km"] >= 0.5]

    return df.reset_index(drop=True)


def pace_to_seconds(p):
    m, s = p.split(":")
    return int(m) * 60 + float(s)


# === LOAD ===
df1 = load_file(file1)
df2 = load_file(file2)

date1 = extract_date(file1)
date2 = extract_date(file2)

# Align lap count
min_len = min(len(df1), len(df2))
df1 = df1.iloc[:min_len]
df2 = df2.iloc[:min_len]

# Convert pace
df1["pace_sec"] = df1["Avg Pace min/km"].apply(pace_to_seconds)
df2["pace_sec"] = df2["Avg Pace min/km"].apply(pace_to_seconds)

# === METRICS ===
metrics = {
    "Pace": ("pace_sec", True),
    "HR": ("Avg HR bpm", False),
    "Power": ("Avg Power W", False),
    "Cadence": ("Avg Run Cadence spm", False),
    "GCT": ("Avg Ground Contact Time ms", True),
    "Stride": ("Avg Stride Length m", False),
    "Vert Osc": ("Avg Vertical Oscillation cm", True),
    "Vert Ratio": ("Avg Vertical Ratio %", True),
}

# === BUILD COMPARISON ===
result = pd.DataFrame()
result["Lap"] = df1["Laps"]

for label, (col, lower_is_better) in metrics.items():
    r1 = df1[col].astype(float)
    r2 = df2[col].astype(float)

    result[f"{label} {date1}"] = r1
    result[f"{label} {date2}"] = r2

    diff = r2 - r1
    pct = diff / r1

    # Improvement score
    if lower_is_better:
        score = -pct
    else:
        score = pct

    result[f"{label} Diff"] = diff
    result[f"{label} %"] = pct
    result[f"{label} Score"] = score

# === FATIGUE / EFFICIENCY ANALYSIS ===
analysis = pd.DataFrame({
    "Lap": df1["Laps"],
    "Pace1": df1["pace_sec"],
    "HR1": df1["Avg HR bpm"],
    "Pace2": df2["pace_sec"],
    "HR2": df2["Avg HR bpm"],
})

analysis["Efficiency1"] = analysis["HR1"] / analysis["Pace1"]
analysis["Efficiency2"] = analysis["HR2"] / analysis["Pace2"]

# === SUMMARY ===
summary = pd.DataFrame({
    "Metric": list(metrics.keys()),
    "Avg % Change": [result[f"{m} %"].mean() for m in metrics],
    "Avg Score": [result[f"{m} Score"].mean() for m in metrics]
})

summary.loc[len(summary)] = [
    "Overall Score",
    "",
    summary["Avg Score"].mean()
]

# === WRITE TO EXCEL ===
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    result.to_excel(writer, sheet_name="Lap Comparison", index=False)
    summary.to_excel(writer, sheet_name="Summary", index=False)
    analysis.to_excel(writer, sheet_name="Analysis", index=False)

# === FORMAT EXCEL ===
wb = load_workbook(output_file)
ws = wb["Lap Comparison"]

green = PatternFill(start_color="C6EFCE", fill_type="solid")
red = PatternFill(start_color="FFC7CE", fill_type="solid")

for col in ws.iter_cols(min_row=2):
    header = ws.cell(row=1, column=col[0].column).value

    for cell in col:
        if isinstance(cell.value, (int, float)):

            # Format numbers
            if "%" in str(header):
                cell.number_format = "0.00%"
            else:
                cell.number_format = "0.00"

            # Colour only % columns
            if "%" in str(header):
                if cell.value > 0:
                    cell.fill = green
                else:
                    cell.fill = red

# === FORMAT SUMMARY ===
ws2 = wb["Summary"]

for col in ws2.iter_cols(min_row=2):
    header = ws2.cell(row=1, column=col[0].column).value

    for cell in col:
        if isinstance(cell.value, (int, float)):
            if "%" in str(header):
                cell.number_format = "0.00%"
            else:
                cell.number_format = "0.00"

# === ADD CHART ===
chart = LineChart()
chart.title = "Pace Comparison"

data = Reference(ws, min_col=2, max_col=3, min_row=1, max_row=min_len+1)
cats = Reference(ws, min_col=1, min_row=2, max_row=min_len+1)

chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)

ws.add_chart(chart, "Z2")

# === SAVE ===
wb.save(output_file)

print(f"✅ Analysis complete: {output_file}")

