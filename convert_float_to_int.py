import pandas as pd
import numpy as np

p = r'c:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\All_data\all_in_one.csv'
df = pd.read_csv(p, dtype={'category': str, 'original_title': str})

# Identify columns to convert: those that are numeric but stored as float
numeric_cols = df.select_dtypes(include=['float64']).columns.tolist()

print(f"Float columns found: {numeric_cols}")

for col in numeric_cols:
    # Convert to numeric, coerce errors to NaN
    df[col] = pd.to_numeric(df[col], errors='coerce')
    # Round to nearest integer if needed, then convert to Int64
    df[col] = df[col].round(0).astype('Int64')

df.to_csv(p, index=False)
print(f"Converted {len(numeric_cols)} float columns to Int64")
print(f"Total rows: {len(df)}")

# Sample verification
sample = df[numeric_cols].head(5)
print("\nSample of converted columns:")
print(sample.to_string(index=False))
