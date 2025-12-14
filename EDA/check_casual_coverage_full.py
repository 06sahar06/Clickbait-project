import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

print("Loading data...")
casual_votes = pd.read_csv(base / 'casualVotes.csv')
casual_vote_titles = pd.read_csv(base / 'casualVoteTitles.csv')
video_info = pd.read_csv(base / 'videoInfo.csv')

print("\n" + "="*80)
print("FILE SIZES")
print("="*80)
print(f"casualVotes.csv: {len(casual_votes)} rows, {len(casual_votes['videoID'].unique())} unique videoIDs")
print(f"casualVoteTitles.csv: {len(casual_vote_titles)} rows, {len(casual_vote_titles['videoID'].unique())} unique videoIDs")
print(f"videoInfo.csv: {len(video_info)} rows, {len(video_info['videoID'].dropna().unique())} unique videoIDs")

# Get unique videoIDs from each file
casual_votes_vids = set(casual_votes['videoID'].dropna().unique())
casual_titles_vids = set(casual_vote_titles['videoID'].dropna().unique())
video_info_vids = set(video_info['videoID'].dropna().unique())

print("\n" + "="*80)
print("COMPARISON: casualVotes vs casualVoteTitles")
print("="*80)

overlap_casual = casual_votes_vids.intersection(casual_titles_vids)
only_in_votes = casual_votes_vids - casual_titles_vids
only_in_titles = casual_titles_vids - casual_votes_vids

print(f"\nUnique videoIDs in casualVotes: {len(casual_votes_vids)}")
print(f"Unique videoIDs in casualVoteTitles: {len(casual_titles_vids)}")
print(f"\n📊 Overlap:")
print(f"  - In BOTH files: {len(overlap_casual)} videos")
print(f"  - ONLY in casualVotes: {len(only_in_votes)} videos")
print(f"  - ONLY in casualVoteTitles: {len(only_in_titles)} videos")

print(f"\n📈 Percentages:")
print(f"  - {len(overlap_casual)/len(casual_votes_vids)*100:.2f}% of casualVotes videos are also in casualVoteTitles")
print(f"  - {len(overlap_casual)/len(casual_titles_vids)*100:.2f}% of casualVoteTitles videos are also in casualVotes")

if len(only_in_votes) > 0:
    print(f"\n🔍 Sample videos ONLY in casualVotes (first 5):")
    for vid in list(only_in_votes)[:5]:
        row = casual_votes[casual_votes['videoID'] == vid].iloc[0]
        print(f"  - {vid}: category='{row['category']}', upvotes={row['upvotes']}")

if len(only_in_titles) > 0:
    print(f"\n🔍 Sample videos ONLY in casualVoteTitles (first 5):")
    for vid in list(only_in_titles)[:5]:
        row = casual_vote_titles[casual_vote_titles['videoID'] == vid].iloc[0]
        print(f"  - {vid}: \"{row['title'][:60]}...\"")

print("\n" + "="*80)
print("COVERAGE CHECK: Casual files vs videoInfo.csv")
print("="*80)

# Check casualVotes coverage
casual_votes_in_info = casual_votes_vids.intersection(video_info_vids)
casual_votes_not_in_info = casual_votes_vids - video_info_vids

print(f"\n📋 casualVotes.csv coverage:")
print(f"  - {len(casual_votes_in_info)}/{len(casual_votes_vids)} ({len(casual_votes_in_info)/len(casual_votes_vids)*100:.2f}%) ARE in videoInfo.csv")
print(f"  - {len(casual_votes_not_in_info)}/{len(casual_votes_vids)} ({len(casual_votes_not_in_info)/len(casual_votes_vids)*100:.2f}%) are NOT in videoInfo.csv")

# Check casualVoteTitles coverage
casual_titles_in_info = casual_titles_vids.intersection(video_info_vids)
casual_titles_not_in_info = casual_titles_vids - video_info_vids

print(f"\n📋 casualVoteTitles.csv coverage:")
print(f"  - {len(casual_titles_in_info)}/{len(casual_titles_vids)} ({len(casual_titles_in_info)/len(casual_titles_vids)*100:.2f}%) ARE in videoInfo.csv")
print(f"  - {len(casual_titles_not_in_info)}/{len(casual_titles_vids)} ({len(casual_titles_not_in_info)/len(casual_titles_vids)*100:.2f}%) are NOT in videoInfo.csv")

print("\n" + "="*80)
print("SAMPLES: Videos in casual files but NOT in videoInfo")
print("="*80)

if len(casual_votes_not_in_info) > 0:
    print(f"\n❌ casualVotes videos NOT in videoInfo (first 5):")
    for vid in list(casual_votes_not_in_info)[:5]:
        row = casual_votes[casual_votes['videoID'] == vid].iloc[0]
        print(f"  - {vid}: category='{row['category']}'")

if len(casual_titles_not_in_info) > 0:
    print(f"\n❌ casualVoteTitles videos NOT in videoInfo (first 5):")
    for vid in list(casual_titles_not_in_info)[:5]:
        row = casual_vote_titles[casual_vote_titles['videoID'] == vid].iloc[0]
        print(f"  - {vid}: \"{row['title'][:60]}...\"")

print("\n" + "="*80)
print("SUMMARY & IMPLICATIONS")
print("="*80)
print(f"""
Key findings:
1. casualVotes and casualVoteTitles overlap: {len(overlap_casual)/max(len(casual_votes_vids), len(casual_titles_vids))*100:.1f}%
2. casualVotes in videoInfo: {len(casual_votes_in_info)/len(casual_votes_vids)*100:.1f}%
3. casualVoteTitles in videoInfo: {len(casual_titles_in_info)/len(casual_titles_vids)*100:.1f}%

For training data creation:
- Videos in videoInfo with casual votes/titles: can use original title as clickbait
- Videos NOT in videoInfo: missing original YouTube title (no ground truth)
- casualVotes might track votes on categories, casualVoteTitles tracks alternative titles
""")
