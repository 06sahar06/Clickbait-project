import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

print("Loading data...")
titles = pd.read_csv(base / 'titles.csv')
casual_vote_titles = pd.read_csv(base / 'casualVoteTitles.csv')
title_votes = pd.read_csv(base / 'titleVotes.csv')

print("\n" + "="*80)
print("CORRECTED ANALYSIS: VideoID Matching & Title Comparison")
print("="*80)

# Check videoID overlap
titles_videos = set(titles['videoID'].dropna().unique())
casual_videos = set(casual_vote_titles['videoID'].dropna().unique())
overlap_videos = titles_videos.intersection(casual_videos)

print(f"\nUnique videoIDs in titles.csv: {len(titles_videos)}")
print(f"Unique videoIDs in casualVoteTitles.csv: {len(casual_videos)}")
print(f"VideoIDs that appear in BOTH files: {len(overlap_videos)}")
print(f"Overlap percentage: {len(overlap_videos)/len(casual_videos)*100:.2f}% of casualVoteTitles videos")

print("\n" + "="*80)
print("SAMPLE COMPARISON: Same videoID, same or different title text?")
print("="*80)

# Take 5 samples from overlapping videos
sample_videos = list(overlap_videos)[:5]
for vid in sample_videos:
    print(f"\n--- VideoID: {vid} ---")
    
    # Get titles from titles.csv
    titles_data = titles[titles['videoID'] == vid][['videoID', 'title', 'UUID']].head(3)
    print(f"Titles in titles.csv ({len(titles_data)} rows):")
    for idx, row in titles_data.iterrows():
        print(f"  - {row['title']}")
    
    # Get titles from casualVoteTitles
    casual_data = casual_vote_titles[casual_vote_titles['videoID'] == vid][['videoID', 'title', 'id']].head(3)
    print(f"Titles in casualVoteTitles.csv ({len(casual_data)} rows):")
    for idx, row in casual_data.iterrows():
        print(f"  - [id={row['id']}] {row['title']}")

print("\n" + "="*80)
print("CLICKBAIT LABELING STRATEGY")
print("="*80)

# Count videos by category
total_titles = len(titles)
less_clickbaity = titles[titles['videoID'].isin(casual_videos)]
more_clickbaity = titles[~titles['videoID'].isin(casual_videos)]

print(f"\nTotal titles in titles.csv: {total_titles}")
print(f"Titles with videoID in casualVoteTitles (less clickbaity): {len(less_clickbaity)} ({len(less_clickbaity)/total_titles*100:.2f}%)")
print(f"Titles with videoID NOT in casualVoteTitles (more clickbaity): {len(more_clickbaity)} ({len(more_clickbaity)/total_titles*100:.2f}%)")

print("\n" + "="*80)
print("VOTE ANALYSIS: How votes indicate clickbait level")
print("="*80)

# Merge titles with their votes
titles_with_votes = pd.merge(
    titles[['UUID', 'videoID', 'title']], 
    title_votes[['UUID', 'votes']], 
    on='UUID', 
    how='left'
)

print(f"\nTitles with vote data: {titles_with_votes['votes'].notna().sum()}")
print(f"Vote statistics for ALL titles:")
print(titles_with_votes['votes'].describe())

# Compare votes for less vs more clickbaity
less_clickbaity_votes = titles_with_votes[titles_with_votes['videoID'].isin(casual_videos)]['votes']
more_clickbaity_votes = titles_with_votes[~titles_with_votes['videoID'].isin(casual_videos)]['votes']

print(f"\nVote statistics for LESS clickbaity titles (in casualVoteTitles):")
print(less_clickbaity_votes.describe())
print(f"\nVote statistics for MORE clickbaity titles (NOT in casualVoteTitles):")
print(more_clickbaity_votes.describe())

print("\n" + "="*80)
print("DATASET STRUCTURE FOR MODEL TRAINING")
print("="*80)
print("""
Based on this analysis:

1. CLICKBAIT DETECTION:
   - Label = 1 (more clickbaity): videoID NOT in casualVoteTitles
   - Label = 0.5 or lower weight (less clickbaity): videoID in casualVoteTitles
   - Weight by vote count: higher votes = more confident it's clickbait

2. NEUTRALIZATION TASK:
   - We DON'T have ground truth neutral alternatives
   - Need to generate/translate neutral versions OR
   - Use casualVoteTitles as "already acceptable" and only train to neutralize others

3. MULTIMODAL OPTION:
   - Link to thumbnails.csv via videoID
   - Image + text pairs for clickbait detection
""")

print("\n" + "="*80)
print("NEXT STEPS")
print("="*80)
print("1. Check if casualVoteTitles titles actually appear AS-IS in titles.csv")
print("2. Understand what alternative neutral titles look like (if any exist)")
print("3. Check videoInfo.csv for original YouTube titles (ground truth clickbait)")
