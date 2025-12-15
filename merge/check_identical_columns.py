import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('titles_only_dataset.csv')

print("=" * 80)
print("CHECKING FOR IDENTICAL COLUMNS")
print("=" * 80)
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}\n")

# Get all column names
columns = df.columns.tolist()

# Find pairs of columns with identical values
identical_pairs = []

for i in range(len(columns)):
    for j in range(i + 1, len(columns)):
        col1, col2 = columns[i], columns[j]
        
        # Compare columns (handling NaN values)
        if df[col1].equals(df[col2]):
            identical_pairs.append((col1, col2))
            print(f"✓ IDENTICAL: '{col1}' == '{col2}'")
        elif (df[col1].fillna(-999) == df[col2].fillna(-999)).all():
            identical_pairs.append((col1, col2))
            print(f"✓ IDENTICAL (with NaN handling): '{col1}' == '{col2}'")

if not identical_pairs:
    print("✗ No identical column pairs found")
else:
    print(f"\nTotal identical pairs: {len(identical_pairs)}")
    print("\nSummary:")
    for col1, col2 in identical_pairs:
        print(f"  - {col1} = {col2}")
        # Show value counts for verification
        print(f"    {col1} values: {df[col1].value_counts().to_dict()}")
        print(f"    {col2} values: {df[col2].value_counts().to_dict()}")
        print()

# Additional check: columns that are highly correlated (for numeric columns)
print("\n" + "=" * 80)
print("CHECKING NUMERIC COLUMN CORRELATIONS")
print("=" * 80)

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"Numeric columns: {numeric_cols}\n")

if len(numeric_cols) > 1:
    correlation_matrix = df[numeric_cols].corr()
    
    # Find pairs with correlation = 1.0 (excluding diagonal)
    high_corr_pairs = []
    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            col1, col2 = numeric_cols[i], numeric_cols[j]
            corr = correlation_matrix.loc[col1, col2]
            
            if abs(corr) == 1.0:
                high_corr_pairs.append((col1, col2, corr))
                print(f"Perfect correlation: '{col1}' <-> '{col2}' (r = {corr:.3f})")
    
    if not high_corr_pairs:
        print("✗ No perfect correlations found among numeric columns")
