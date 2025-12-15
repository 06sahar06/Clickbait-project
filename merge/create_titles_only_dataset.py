import pandas as pd

# Load the complete dataset
complete = pd.read_csv('complete_dataset.csv')

print("=" * 80)
print("CREATING TITLE-ONLY DATASET")
print("=" * 80)
print(f"Complete dataset: {complete.shape}")

# Select only title and casual-related columns (exclude all thumbnail columns)
title_only_columns = [
    # Identifiers
    'videoID',
    'title_UUID',
    'title',
    
    # Casual submission info
    'is_casual_submission',
    'casual_category',
    'casual_upvotes',
    
    # Title properties
    'title_is_original',
    'title_casualMode',
    'title_votes',
    'title_downvotes',
    'title_timeSubmitted',
    'title_locked',
    'title_shadowHidden',
    'title_verification',
    'title_removed'
]

titles_only = complete[title_only_columns].copy()

# Rename columns to simpler names
column_mapping = {
    'title_UUID': 'uuid',
    'is_casual_submission': 'is_casual',
    'casual_category': 'category',
    'casual_upvotes': 'upvotes',
    'title_is_original': 'is_original',
    'title_casualMode': 'casual_mode',
    'title_votes': 'votes',
    'title_downvotes': 'downvotes',
    'title_timeSubmitted': 'time_submitted',
    'title_locked': 'locked',
    'title_shadowHidden': 'shadow_hidden',
    'title_verification': 'verification',
    'title_removed': 'removed'
}

titles_only = titles_only.rename(columns=column_mapping)

# Add UUID count per video
uuid_counts = titles_only.groupby('videoID')['uuid'].count().reset_index()
uuid_counts.columns = ['videoID', 'uuid_count']
titles_only = titles_only.merge(uuid_counts, on='videoID', how='left')

# Drop the UUID column
titles_only = titles_only.drop(columns=['uuid'])

print(f"\nTitle-only dataset: {titles_only.shape}")
print(f"Columns included: {len(title_only_columns)}")
print(f"\nColumn list:")
for i, col in enumerate(title_only_columns, 1):
    print(f"  {i:2}. {col}")

print(f"\nData summary:")
print(f"  Total titles: {len(titles_only)}")
print(f"  Unique videos: {titles_only['videoID'].nunique()}")
print(f"  With casual submissions: {titles_only['is_casual'].sum()} ({100*titles_only['is_casual'].sum()/len(titles_only):.1f}%)")
print(f"  Original titles: {titles_only['is_original'].sum()} ({100*titles_only['is_original'].sum()/len(titles_only):.1f}%)")
print(f"  Casual mode titles: {titles_only['casual_mode'].sum()} ({100*titles_only['casual_mode'].sum()/len(titles_only):.1f}%)")
print(f"\nUUID count per video:")
print(titles_only['uuid_count'].describe())

# Save to CSV
output_file = 'titles_only_dataset.csv'
titles_only.to_csv(output_file, index=False)
print(f"\n✓ Saved title-only dataset to {output_file}")

# Show sample
print(f"\nSample rows:")
print(titles_only.head(3))

# Show statistics
print(f"\nVote statistics:")
print(titles_only[['votes', 'downvotes', 'upvotes']].describe())

print(f"\nCasual category distribution:")
print(titles_only['category'].value_counts())
