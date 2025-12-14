import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

print("Loading data...")
titles = pd.read_csv(base / 'titles.csv')
casual_vote_titles = pd.read_csv(base / 'casualVoteTitles.csv')

# Get unique videoIDs from both files
titles_videos = set(titles['videoID'].dropna().unique())
casual_videos = set(casual_vote_titles['videoID'].dropna().unique())

print("\n" + "="*80)
print("VIDEOID PRESENCE CHECK")
print("="*80)

print(f"\nUnique videoIDs in titles.csv: {len(titles_videos)}")
print(f"Unique videoIDs in casualVoteTitles.csv: {len(casual_videos)}")

# Check overlap
overlap_videos = titles_videos.intersection(casual_videos)
casual_not_in_titles = casual_videos - titles_videos

print(f"\nVideoIDs in BOTH files: {len(overlap_videos)}")
print(f"VideoIDs in casualVoteTitles but NOT in titles.csv: {len(casual_not_in_titles)}")

print(f"\n📊 Breakdown:")
print(f"  - {len(overlap_videos)}/{len(casual_videos)} ({len(overlap_videos)/len(casual_videos)*100:.2f}%) of casualVoteTitles videos ARE in titles.csv")
print(f"  - {len(casual_not_in_titles)}/{len(casual_videos)} ({len(casual_not_in_titles)/len(casual_videos)*100:.2f}%) of casualVoteTitles videos are NOT in titles.csv")

if len(casual_not_in_titles) > 0:
    print("\n" + "="*80)
    print("EXAMPLES: VideoIDs in casualVoteTitles but NOT in titles.csv")
    print("="*80)
    
    # Show 10 examples
    sample_vids = list(casual_not_in_titles)[:10]
    for i, vid in enumerate(sample_vids, 1):
        casual_data = casual_vote_titles[casual_vote_titles['videoID'] == vid]
        print(f"\n{i}. VideoID: {vid}")
        print(f"   Title: \"{casual_data.iloc[0]['title']}\"")
        print(f"   Number of casual vote entries: {len(casual_data)}")
else:
    print("\n✅ ALL videoIDs from casualVoteTitles.csv exist in titles.csv")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
if len(casual_not_in_titles) > 0:
    print(f"""
⚠️  There are {len(casual_not_in_titles)} videos in casualVoteTitles that do NOT appear in titles.csv
    
This means:
- casualVoteTitles contains alternative titles for videos that don't have entries in titles.csv
- These might be videos where only casual vote alternatives were submitted
- titles.csv is not the complete source of all original titles
""")
else:
    print("""
✅ All videos in casualVoteTitles also appear in titles.csv

This confirms:
- casualVoteTitles is a SUBSET pointing to videos in titles.csv
- casualVoteTitles contains alternative/less clickbaity suggestions for titles in titles.csv
""")
