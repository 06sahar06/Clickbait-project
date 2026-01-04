import pandas as pd

df = pd.read_csv('All_data/all_in_one.csv')
print(f'Total rows: {len(df)}')
print(f'Rows with Views: {df["Views"].notna().sum()}')
print(f'Rows with channelID: {df["channelID"].notna().sum()}')
print(f'Rows with likes: {df["likes"].notna().sum()}')
print(f'Rows missing stats: {df[df["Views"].isna() & df["videoID"].notna()].shape[0]}')

# Check unique videoIDs
missing_mask = (
    df['videoID'].notna() & (
        df['channelID'].isna() |
        df['Views'].isna() |
        df['Published'].isna() |
        df['likes'].isna() |
        df['comments'].isna()
    )
)
unique_videos = df.loc[missing_mask, 'videoID'].dropna().unique()
print(f'Unique videoIDs still needing stats: {len(unique_videos)}')
