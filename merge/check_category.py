import pandas as pd

df = pd.read_csv('titles_only_dataset.csv')

print(f"Total rows: {len(df)}")
print(f"Non-null categories: {df['category'].notna().sum()}")
print(f"Null categories: {df['category'].isna().sum()}")
print(f"Percentage with category: {100 * df['category'].notna().sum() / len(df):.2f}%")

print(f"\nCategory distribution:")
print(df['category'].value_counts())

print(f"\nSample rows with category:")
print(df[df['category'].notna()][['videoID', 'title', 'category', 'is_casual']].head(10))
