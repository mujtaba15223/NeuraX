import pandas as pd


# ============================================================
# MODEL 1 — DATA EXPLORATION
# ============================================================

# 1. Load dataset
file_path = "data/raw/model1/Model_1.csv"

df = pd.read_csv(file_path)

print("=" * 60)
print("MODEL 1 DATA EXPLORATION")
print("=" * 60)


# ============================================================
# 2. BASIC DATASET INFORMATION
# ============================================================

print("\nDataset loaded successfully!")
print("Shape:", df.shape)


# ============================================================
# 3. COLUMN NAMES
# ============================================================

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# 4. MISSING VALUES
# ============================================================

print("\nMissing values:")
print(df.isnull().sum())


# ============================================================
# 5. DATASET STATISTICS
# ============================================================

print("\nDataset statistics:")

pd.set_option("display.max_columns", None)

print(df.describe())


# ============================================================
# 6. DUPLICATE ROWS
# ============================================================

print("\nDuplicate rows:", df.duplicated().sum())


# ============================================================
# 7. DEMAND VS PARTS PER HOUR
# ============================================================

print("\nDemand vs Parts per Hour:")

demand_analysis = (
    df.groupby("Demand")["Parts per hour"]
    .agg(["count", "mean", "min", "max"])
)

print(demand_analysis)


# ============================================================
# 8. DEMAND VS WAITING TIME
# ============================================================

print("\nDemand vs Waiting Time:")

waiting_analysis = df.groupby("Demand")[
    [
        "Drilling Waiting Time",
        "Milling Waiting Time",
        "Assembly Waiting Time"
    ]
].mean()

print(waiting_analysis)

print("\nDemand vs Station Utilization:")

utilization_analysis = df.groupby("Demand")[
    [
        "Drilling Util",
        "Milling Util",
        "Assembly Util"
    ]
].mean()

print(utilization_analysis)


# ============================================================
# END
# ============================================================

print("\n" + "=" * 60)
print("EXPLORATION COMPLETE")
print("=" * 60)