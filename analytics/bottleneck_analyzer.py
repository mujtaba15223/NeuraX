import pandas as pd


# ============================================================
# BOTTLENECK ANALYZER
# ============================================================

FILE_PATH = "data/raw/model2/Model_2.csv"


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(FILE_PATH)


# ============================================================
# 2. DEFINE STATIONS
# ============================================================

stations = {
    "Drilling": {
        "queue": "Drilling Queue Time",
        "utilization": "Drilling Utilization",
    },
    "Milling": {
        "queue": "Milling Queue Time",
        "utilization": "Milling Utilization",
    },
    "Assembly": {
        "queue": "Assembly Queue Time",
        "utilization": "Assembly Utilization",
    },
}


# ============================================================
# 3. CALCULATE AVERAGE METRICS
# ============================================================

results = []

for station, columns in stations.items():

    avg_queue = df[columns["queue"]].mean()
    avg_utilization = df[columns["utilization"]].mean()

    results.append({
        "Station": station,
        "Average Queue Time": avg_queue,
        "Average Utilization": avg_utilization,
    })


results_df = pd.DataFrame(results)


# ============================================================
# 4. NORMALIZE QUEUE PRESSURE
# ============================================================

max_queue = results_df["Average Queue Time"].max()

if max_queue > 0:
    results_df["Queue Pressure"] = (
        results_df["Average Queue Time"] / max_queue
    )
else:
    results_df["Queue Pressure"] = 0


# ============================================================
# 5. NORMALIZE UTILIZATION PRESSURE
# ============================================================

max_utilization = results_df["Average Utilization"].max()

if max_utilization > 0:
    results_df["Utilization Pressure"] = (
        results_df["Average Utilization"] / max_utilization
    )
else:
    results_df["Utilization Pressure"] = 0


# ============================================================
# 6. BOTTLENECK SCORE
# ============================================================
#
# We combine:
#
# 60% Queue Pressure
# 40% Utilization Pressure
#
# This prevents utilization alone from deciding
# the bottleneck.
# ============================================================

results_df["Bottleneck Score"] = (
    0.60 * results_df["Queue Pressure"]
    + 0.40 * results_df["Utilization Pressure"]
)


# ============================================================
# 7. SORT STATIONS
# ============================================================

results_df = results_df.sort_values(
    by="Bottleneck Score",
    ascending=False
).reset_index(drop=True)


# ============================================================
# 8. RANK
# ============================================================

results_df["Rank"] = results_df.index + 1


# ============================================================
# 9. PRINT RESULTS
# ============================================================

print("=" * 70)
print("BOTTLENECK ANALYSIS")
print("=" * 70)

print("\nStation Metrics:")

print(
    results_df[
        [
            "Rank",
            "Station",
            "Average Queue Time",
            "Average Utilization",
            "Queue Pressure",
            "Utilization Pressure",
            "Bottleneck Score",
        ]
    ].round(4)
)


# ============================================================
# 10. IDENTIFY TOP BOTTLENECK CANDIDATE
# ============================================================

top_station = results_df.iloc[0]

print("\n" + "=" * 70)
print("BOTTLENECK CANDIDATE")
print("=" * 70)

print("Station:", top_station["Station"])
print("Bottleneck Score:", round(top_station["Bottleneck Score"], 4))
print("Average Queue:", round(top_station["Average Queue Time"], 4))
print(
    "Average Utilization:",
    round(top_station["Average Utilization"], 4)
)


# ============================================================
# 11. INTERPRETATION
# ============================================================

print("\nInterpretation:")

print(
    f"{top_station['Station']} has the highest combined "
    "queue-pressure and utilization-pressure score."
)

print(
    "This is a bottleneck CANDIDATE based on the available "
    "process evidence, not proof of causality."
)


# ============================================================
# END
# ============================================================

print("\n" + "=" * 70)
print("BOTTLENECK ANALYSIS COMPLETE")
print("=" * 70)