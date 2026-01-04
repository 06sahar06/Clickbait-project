import pandas as pd

df = pd.read_csv('All_data/all_in_one.csv', low_memory=False)

print(f'Total rows: {len(df)}')

# Check what values are in the missing rows
missing_mask = (
    df['videoID'].notna() & (
        df['channelID'].isna() |
        df['Views'].isna() |
        df['Published'].isna() |
        df['likes'].isna() |
        df['comments'].isna()
    )
)

missing_df = df[missing_mask]
print(f'\nRows missing stats: {len(missing_df)}')
print(f'Unique videoIDs still needing stats: {missing_df["videoID"].nunique()}')

# Check if any have -1 values
print(f'\nRows with Views = -1: {(df["Views"] == -1).sum()}')
print(f'Rows with channelID = -1: {(df["channelID"] == -1).sum()}')
print(f'Rows with likes = -1: {(df["likes"] == -1).sum()}')

# Show sample of missing data
print(f'\nSample of rows missing data:')
print(missing_df[['videoID', 'channelID', 'Views', 'likes', 'Published', 'comments']].head(10))

# Check unique values in Views column for missing rows
print(f'\nUnique values in Views column for missing rows:')
print(missing_df['Views'].unique()[:20])
