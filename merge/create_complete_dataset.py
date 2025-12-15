import pandas as pd
import numpy as np

# Load all three merged files
casual_merged = pd.read_csv('casual_merged.csv')
titles_with_votes = pd.read_csv('titles_with_votes.csv')
thumbnails_complete = pd.read_csv('thumbnails_complete.csv')

print("=" * 80)
print("LOADING DATA")
print("=" * 80)
print(f"casual_merged: {casual_merged.shape}")
print(f"titles_with_votes: {titles_with_votes.shape}")
print(f"thumbnails_complete: {thumbnails_complete.shape}")

# Step 1: Start with titles_with_votes as base (most comprehensive)
base = titles_with_votes.copy()

# Rename title columns to avoid confusion
base = base.rename(columns={
    'votes': 'title_votes',
    'downvotes': 'title_downvotes',
    'locked': 'title_locked',
    'shadowHidden': 'title_shadowHidden',
    'verification': 'title_verification',
    'removed': 'title_removed',
    'UUID': 'title_UUID',
    'timeSubmitted': 'title_timeSubmitted',
    'original': 'title_is_original',
    'casualMode': 'title_casualMode'
})

print(f"\nBase dataset (from titles): {base.shape}")

# Step 2: Add casual submission information
# Create a mapping of videoID -> is_casual
casual_videos = set(casual_merged['videoID'].unique())
base['is_casual_submission'] = base['videoID'].isin(casual_videos).astype(int)

# Add casual title info (for videos that have casual submissions)
casual_info = casual_merged.groupby('videoID').agg({
    'upvotes': 'max',  # Max upvotes across casual submissions for this video
    'category': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],  # Most common category
}).reset_index()

casual_info = casual_info.rename(columns={
    'upvotes': 'casual_upvotes',
    'category': 'casual_category'
})

base = base.merge(casual_info, on='videoID', how='left')

print(f"After adding casual info: {base.shape}")
print(f"  Videos with casual submissions: {base['is_casual_submission'].sum()}")

# Step 3: Add thumbnail information
# Aggregate thumbnails by videoID (a video can have multiple thumbnails)
thumbnail_info = thumbnails_complete.groupby('videoID').agg({
    'UUID': 'count',  # Number of thumbnails
    'votes': 'sum',   # Total thumbnail votes
    'downvotes': 'sum',  # Total thumbnail downvotes
    'timestamp': lambda x: x[x >= 0].mean() if (x >= 0).any() else -1,  # Average timestamp (excluding -1)
    'original': 'max',  # Has any original thumbnail
    'casualMode': 'max'  # Has any casual thumbnail
}).reset_index()

thumbnail_info = thumbnail_info.rename(columns={
    'UUID': 'thumbnail_count',
    'votes': 'thumbnail_votes_total',
    'downvotes': 'thumbnail_downvotes_total',
    'timestamp': 'thumbnail_avg_timestamp',
    'original': 'thumbnail_has_original',
    'casualMode': 'thumbnail_casualMode'
})

base = base.merge(thumbnail_info, on='videoID', how='left')

# Add has_thumbnail flag
base['has_thumbnail'] = base['thumbnail_count'].notna().astype(int)
base['thumbnail_count'] = base['thumbnail_count'].fillna(0).astype(int)
base['thumbnail_votes_total'] = base['thumbnail_votes_total'].fillna(0)
base['thumbnail_downvotes_total'] = base['thumbnail_downvotes_total'].fillna(0)
base['thumbnail_avg_timestamp'] = base['thumbnail_avg_timestamp'].fillna(-1)
base['thumbnail_has_original'] = base['thumbnail_has_original'].fillna(0).astype(int)
base['thumbnail_casualMode'] = base['thumbnail_casualMode'].fillna(0).astype(int)

print(f"After adding thumbnail info: {base.shape}")
print(f"  Videos with thumbnails: {base['has_thumbnail'].sum()}")

# Step 4: Select final columns in logical order
final_columns = [
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
    'title_removed',
    
    # Thumbnail info
    'has_thumbnail',
    'thumbnail_count',
    'thumbnail_votes_total',
    'thumbnail_downvotes_total',
    'thumbnail_avg_timestamp',
    'thumbnail_has_original',
    'thumbnail_casualMode'
]

final_dataset = base[final_columns].copy()

print("\n" + "=" * 80)
print("FINAL DATASET SUMMARY")
print("=" * 80)
print(f"Total rows: {len(final_dataset)}")
print(f"Total unique videos: {final_dataset['videoID'].nunique()}")
print(f"\nData completeness:")
print(f"  Casual submissions: {final_dataset['is_casual_submission'].sum()} ({100*final_dataset['is_casual_submission'].sum()/len(final_dataset):.1f}%)")
print(f"  Has thumbnails: {final_dataset['has_thumbnail'].sum()} ({100*final_dataset['has_thumbnail'].sum()/len(final_dataset):.1f}%)")
print(f"  Multimodal (casual + thumbnail): {((final_dataset['is_casual_submission']==1) & (final_dataset['has_thumbnail']==1)).sum()}")

print(f"\nColumn list:")
for i, col in enumerate(final_columns, 1):
    print(f"  {i:2}. {col}")

# Save to CSV
output_file = 'complete_dataset.csv'
final_dataset.to_csv(output_file, index=False)
print(f"\n✓ Saved complete dataset to {output_file}")

# Show sample
print(f"\nSample rows:")
print(final_dataset.head(3))

# Show statistics
print(f"\nKey statistics:")
print(final_dataset[['title_votes', 'title_downvotes', 'thumbnail_votes_total', 'casual_upvotes']].describe())
