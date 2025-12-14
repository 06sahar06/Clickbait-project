import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

# Load relevant files
print("Loading data...")
titles = pd.read_csv(base / 'titles.csv')
casual_vote_titles = pd.read_csv(base / 'casualVoteTitles.csv')

print("\n" + "="*80)
print("1. TITLES.CSV STRUCTURE")
print("="*80)
print(f"Shape: {titles.shape}")
print(f"Columns: {titles.columns.tolist()}")
print(f"\nFirst 5 rows:")
print(titles.head())

print("\n" + "="*80)
print("2. CASUALVOTETITLES.CSV STRUCTURE")
print("="*80)
print(f"Shape: {casual_vote_titles.shape}")
print(f"Columns: {casual_vote_titles.columns.tolist()}")
print(f"\nFirst 5 rows:")
print(casual_vote_titles.head())

print("\n" + "="*80)
print("3. VIDEO ID OVERLAP CHECK")
print("="*80)
titles_videos = set(titles['videoID'].unique())
casual_videos = set(casual_vote_titles['videoID'].unique())
overlap = titles_videos.intersection(casual_videos)

print(f"Unique videoIDs in titles.csv: {len(titles_videos)}")
print(f"Unique videoIDs in casualVoteTitles.csv: {len(casual_videos)}")
print(f"Videos with BOTH titles and casual votes: {len(overlap)}")
print(f"Overlap percentage: {len(overlap)/len(titles_videos)*100:.2f}%")

print("\n" + "="*80)
print("4. SAMPLE: Same videoID in both files?")
print("="*80)
if len(overlap) > 0:
    sample_vid = list(overlap)[0]
    print(f"\nSample videoID: {sample_vid}")
    print(f"\nOriginal title from titles.csv:")
    print(titles[titles['videoID'] == sample_vid][['videoID', 'title']].head())
    print(f"\nCasual vote titles for this video from casualVoteTitles.csv:")
    print(casual_vote_titles[casual_vote_titles['videoID'] == sample_vid][['videoID', 'title', 'id']].head(10))

print("\n" + "="*80)
print("5. CASUALVOTETITLES 'id' COLUMN ANALYSIS")
print("="*80)
print(f"Unique values in 'id' column: {casual_vote_titles['id'].nunique()}")
print(f"'id' value counts (first 15):")
print(casual_vote_titles['id'].value_counts().head(15))
print(f"\nDoes 'id' represent ranking/selection? Let's check one videoID:")
if len(overlap) > 0:
    sample_vid = list(overlap)[0]
    sample_data = casual_vote_titles[casual_vote_titles['videoID'] == sample_vid][['videoID', 'id', 'title']].sort_values('id')
    print(f"\nFor videoID {sample_vid}:")
    print(sample_data)

print("\n" + "="*80)
print("6. CONCLUSION")
print("="*80)
print("Key questions to answer:")
print("- Are casual vote titles 'neutral' alternatives or just community-proposed variations?")
print("- Does 'id' in casualVoteTitles refer to the selected/best title?")
print("- Are there multiple alternative titles per video in casualVoteTitles?")
print("- What makes a casualVoteTitle different from the original title quality-wise?")
