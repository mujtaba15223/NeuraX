import pandas as pd


# ============================================================
# MODEL 2 — DATA EXPLORATION
# ============================================================

file_path = "data/raw/model2/Model_2.csv"

df = pd.read_csv(file_path)

print("=" * 70)
print("MODEL 2 DATA EXPLORATION")
print("=" * 70)


# ============================================================
# 1. BASIC INFORMATION
# ============================================================

print("\nDataset loaded successfully!")
print("Shape:", df.shape)


# ============================================================
# 2. COLUMNS
# ============================================================

print("\nColumns:")

for i, column in enumerate(df.columns):
    print(i, column)


# ============================================================
# 3. DATA TYPES
# ============================================================

print("\nData Types:")
print(df.dtypes)


# ============================================================
# 4. MISSING VALUES
# ============================================================

print("\nMissing Values:")
print(df.isnull().sum())


# ============================================================
# 5. DUPLICATE ROWS
# ============================================================

print("\nDuplicate Rows:", df.duplicated().sum())


# ============================================================
# 6. BASIC STATISTICS
# ============================================================

print("\nDataset Statistics:")

pd.set_option("display.max_columns", None)

print(df.describe())


# ============================================================
# 7. DEMAND VS PRODUCTION FLOW
# ============================================================

print("\nDemand vs Production Flow:")

production_analysis = df.groupby("Demand")[
    [
        "Entities In Part 1",
        "Entities In Part 2",
        "Entities Out"
    ]
].mean()

print(production_analysis)


# ============================================================
# 8. DEMAND VS QUEUE TIMES
# ============================================================

print("\nDemand vs Queue Times:")

queue_analysis = df.groupby("Demand")[
    [
        "Drilling Queue Time",
        "Milling Queue Time",
        "Assembly Queue Time"
    ]
].mean()

print(queue_analysis)


# ============================================================
# 9. DEMAND VS STORAGE
# ============================================================

print("\nDemand vs Storage:")

storage_analysis = df.groupby("Demand")[
    [
        "Part 1 Storage Time",
        "Part 1 Stored",
        "Part 2 Storage Time",
        "Part 2 Stored"
    ]
].mean()

print(storage_analysis)


# ============================================================
# 10. DEMAND VS STATION UTILIZATION
# ============================================================

print("\nDemand vs Station Utilization:")

utilization_analysis = df.groupby("Demand")[
    [
        "Drilling Utilization",
        "Milling Utilization",
        "Assembly Utilization"
    ]
].mean()

print(utilization_analysis)


# ============================================================
# 11. DEMAND VS VALUE-ADDED TIME
# ============================================================

print("\nDemand vs Value-Added Time:")

va_analysis = df.groupby("Demand")[
    [
        "Part 1 VA Time",
        "Part 2 VA Time",
        "Assembly Time"
    ]
].mean()

print(va_analysis)


# ============================================================
# 12. OVERALL FLOW METRICS
# ============================================================

print("\nOverall Flow Metrics:")

flow_metrics = pd.DataFrame({
    "Average Queue Time": [
        df["Drilling Queue Time"].mean(),
        df["Milling Queue Time"].mean(),
        df["Assembly Queue Time"].mean()
    ],
    "Average Utilization": [
        df["Drilling Utilization"].mean(),
        df["Milling Utilization"].mean(),
        df["Assembly Utilization"].mean()
    ]
}, index=["Drilling", "Milling", "Assembly"])

print(flow_metrics)


# ============================================================
# 13. HIGHEST UTILIZATION
# ============================================================

average_utilization = {
    "Drilling": df["Drilling Utilization"].mean(),
    "Milling": df["Milling Utilization"].mean(),
    "Assembly": df["Assembly Utilization"].mean()
}

highest_utilization_station = max(
    average_utilization,
    key=average_utilization.get
)

print("\nHighest Average Utilization Station:")
print(
    highest_utilization_station,
    "->",
    round(average_utilization[highest_utilization_station], 4)
)


# ============================================================
# 14. HIGHEST QUEUE
# ============================================================

average_queue = {
    "Drilling": df["Drilling Queue Time"].mean(),
    "Milling": df["Milling Queue Time"].mean(),
    "Assembly": df["Assembly Queue Time"].mean()
}

highest_queue_station = max(
    average_queue,
    key=average_queue.get
)

print("\nHighest Average Queue Station:")
print(
    highest_queue_station,
    "->",
    round(average_queue[highest_queue_station], 4)
)


# ============================================================
# END
# ============================================================

print("\n" + "=" * 70)
print("MODEL 2 EXPLORATION COMPLETE")
print("=" * 70)