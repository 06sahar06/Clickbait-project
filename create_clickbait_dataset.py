import pandas as pd
import numpy as np

"""
Create a dataset with:
- videoID
- original_title
- is_clickbait (based on casual votes classification)
- alternative_title (submitted new title when it's casual/clickbait)
"""

# Load necessary data files
print("Loading data files...")
titles_df = pd.read_csv('data/titles.csv')
casual_votes_df = pd.read_csv('data/casualVotes.csv')
casual_vote_titles_df = pd.read_csv('data/casualVoteTitles.csv')

print(f"Titles shape: {titles_df.shape}")
print(f"Casual votes shape: {casual_votes_df.shape}")
print(f"Casual vote titles shape: {casual_vote_titles_df.shape}")

# Step 1: Identify videos that have been classified as casual (clickbait)
# A video is considered to have a casual classification if it has entries in casualVotes
casual_videos = casual_votes_df['videoID'].unique()
print(f"Videos with casual classifications: {len(casual_videos)}")

# Step 2: Create a mapping of videoID to whether it's clickbait
# A video is clickbait if it has casual submissions (meaning users voted it as casual/clickbait)
clickbait_mapping = pd.DataFrame({
    'videoID': casual_videos,
    'is_clickbait': 1
})

# Step 3: Add all videos (including non-clickbait ones)
all_videos = pd.DataFrame({
    'videoID': titles_df['videoID'].unique()
})
all_videos = all_videos.merge(clickbait_mapping, on='videoID', how='left')
all_videos['is_clickbait'] = all_videos['is_clickbait'].fillna(0).astype(int)

print(f"Total unique videos: {len(all_videos)}")
print(f"Clickbait videos: {all_videos['is_clickbait'].sum()}")
print(f"Non-clickbait videos: {(all_videos['is_clickbait'] == 0).sum()}")

# Step 4: Get the original titles (title where original=1)
original_titles = titles_df[titles_df['original'] == 1][['videoID', 'title']].copy()
original_titles = original_titles.rename(columns={'title': 'original_title'})
original_titles = original_titles.drop_duplicates(subset=['videoID'], keep='first')

print(f"Videos with original titles: {len(original_titles)}")

# Step 5: Merge original titles with clickbait status
result_df = all_videos.merge(original_titles, on='videoID', how='left')

# Step 6: Add alternative titles (casual submissions) for clickbait videos
# For clickbait videos, get the most upvoted casual alternative title
casual_alternatives = casual_vote_titles_df.copy()
casual_alternatives = casual_alternatives.rename(columns={'title': 'alternative_title'})

# Group by videoID and select the title with highest upvotes (or first if no upvotes data)
# Merge with casual votes to get upvote info
casual_with_votes = casual_alternatives.merge(
    casual_votes_df[['videoID', 'upvotes']],
    on='videoID',
    how='left'
)

# For each videoID, get the alternative title with most upvotes
casual_best = casual_with_votes.loc[casual_with_votes.groupby('videoID')['upvotes'].idxmax()][
    ['videoID', 'alternative_title']
].drop_duplicates(subset=['videoID'], keep='first')

print(f"Alternative titles available: {len(casual_best)}")

# Merge alternative titles only for clickbait videos
result_df = result_df.merge(casual_best, on='videoID', how='left')

# Step 7: For non-clickbait videos, set alternative_title as empty/NaN
result_df.loc[result_df['is_clickbait'] == 0, 'alternative_title'] = ''

# Step 8: Reorder and select final columns
final_df = result_df[['videoID', 'original_title', 'is_clickbait', 'alternative_title']].copy()

# Clean up: keep only rows with original_title
final_df = final_df.dropna(subset=['original_title'])

# Replace NaN with empty string for alternative_title
final_df['alternative_title'] = final_df['alternative_title'].fillna('')

print(f"\nFinal dataset shape: {final_df.shape}")
print(f"Columns: {final_df.columns.tolist()}")
print("\nFirst few rows:")
print(final_df.head(10))

# Save the dataset
output_file = 'merge/clickbait_dataset.csv'
final_df.to_csv(output_file, index=False)
print(f"\nDataset saved to: {output_file}")

# Print summary statistics
print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)
print(f"Total videos: {len(final_df)}")
print(f"Clickbait videos: {(final_df['is_clickbait'] == 1).sum()}")
print(f"Non-clickbait videos: {(final_df['is_clickbait'] == 0).sum()}")
print(f"Videos with alternative titles: {(final_df['alternative_title'] != '').sum()}")
print(f"Percentage clickbait: {(final_df['is_clickbait'].sum() / len(final_df) * 100):.2f}%")
