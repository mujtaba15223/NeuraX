import pandas as pd

file_path = "data/raw/model1/Model_1.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDataset statistics:")
pd.set_option("display.max_columns", None)
print(df.describe())
print("\nDataset statistics:")

pd.set_option("display.max_columns", None)

print(df.describe())

print("\nDuplicate rows:", df.duplicated().sum())