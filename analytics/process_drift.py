import pandas as pd


# ============================================================
# PROCESS DRIFT DETECTION
# ============================================================

FILE_PATH = "data/raw/model2/Model_2.csv"


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(FILE_PATH)


# ============================================================
# 2. PROCESS VARIABLES
# ============================================================

process_columns = [
    "Drilling Queue Time",
    "Milling Queue Time",
    "Assembly Queue Time",
    "Part 1 Storage Time",
    "Part 2 Storage Time",
    "Drilling Utilization",
    "Milling Utilization",
    "Assembly Utilization",
]


# ============================================================
# 3. CALCULATE BASELINE
# ============================================================

baseline = df[process_columns].mean()
std_dev = df[process_columns].std()


# ============================================================
# 4. CALCULATE Z-SCORES
# ============================================================

z_scores = (df[process_columns] - baseline) / std_dev


# ============================================================
# 5. DETECT ANOMALIES
# ============================================================

# A value beyond 3 standard deviations is treated
# as a strong process anomaly.

anomaly_mask = z_scores.abs() > 3


# ============================================================
# 6. COUNT ANOMALIES
# ============================================================

anomaly_counts = anomaly_mask.sum()

anomaly_summary = pd.DataFrame({
    "Variable": process_columns,
    "Anomaly Count": [
        anomaly_counts[column]
        for column in process_columns
    ]
})


# ============================================================
# 7. ANOMALY RATE
# ============================================================

anomaly_summary["Anomaly Rate"] = (
    anomaly_summary["Anomaly Count"] / len(df)
)


# ============================================================
# 8. SORT BY ANOMALY COUNT
# ============================================================

anomaly_summary = anomaly_summary.sort_values(
    by="Anomaly Count",
    ascending=False
).reset_index(drop=True)


# ============================================================
# 9. PRINT RESULTS
# ============================================================

print("=" * 70)
print("PROCESS DRIFT DETECTION")
print("=" * 70)


print("\nBaseline Statistics:")

baseline_table = pd.DataFrame({
    "Mean": baseline,
    "Standard Deviation": std_dev
})

print(baseline_table.round(4))


print("\nProcess Anomaly Summary:")

print(anomaly_summary.round(4))


# ============================================================
# 10. IDENTIFY MOST ABNORMAL PROCESS VARIABLE
# ============================================================

top_variable = anomaly_summary.iloc[0]

print("\n" + "=" * 70)
print("TOP PROCESS DRIFT SIGNAL")
print("=" * 70)

print("Variable:", top_variable["Variable"])
print("Anomaly Count:", int(top_variable["Anomaly Count"]))
print(
    "Anomaly Rate:",
    round(top_variable["Anomaly Rate"] * 100, 2),
    "%"
)


# ============================================================
# 11. FIND ANOMALOUS RECORDS
# ============================================================

total_anomalous_rows = anomaly_mask.any(axis=1).sum()

print("\nTotal rows with at least one process anomaly:")
print(int(total_anomalous_rows))


# ============================================================
# 12. END
# ============================================================

print("\n" + "=" * 70)
print("PROCESS DRIFT DETECTION COMPLETE")
print("=" * 70)