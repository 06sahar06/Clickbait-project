import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

print("Loading data...")
titles = pd.read_csv(base / 'titles.csv')
casual_votes = pd.read_csv(base / 'casualVotes.csv')
casual_vote_titles = pd.read_csv(base / 'casualVoteTitles.csv')

# Get unique videoIDs
titles_vids = set(titles['videoID'].dropna().unique())
casual_votes_vids = set(casual_votes['videoID'].dropna().unique())
casual_titles_vids = set(casual_vote_titles['videoID'].dropna().unique())

# Combine casual files
casual_all_vids = casual_votes_vids.union(casual_titles_vids)

print("\n" + "="*80)
print("FILE SIZES")
print("="*80)
print(f"titles.csv: {len(titles)} rows, {len(titles_vids)} unique videoIDs")
print(f"casualVotes.csv: {len(casual_votes)} rows, {len(casual_votes_vids)} unique videoIDs")
print(f"casualVoteTitles.csv: {len(casual_vote_titles)} rows, {len(casual_titles_vids)} unique videoIDs")
print(f"casualVotes + casualVoteTitles (union): {len(casual_all_vids)} unique videoIDs")

print("\n" + "="*80)
print("TITLES → CASUAL FILES")
print("="*80)

titles_in_casual_votes = titles_vids.intersection(casual_votes_vids)
titles_in_casual_titles = titles_vids.intersection(casual_titles_vids)
titles_in_any_casual = titles_vids.intersection(casual_all_vids)
titles_not_in_any_casual = titles_vids - casual_all_vids

print(f"\n📊 Are titles.csv videoIDs in casual files?")
print(f"  - {len(titles_in_casual_votes)}/{len(titles_vids)} ({len(titles_in_casual_votes)/len(titles_vids)*100:.2f}%) in casualVotes")
print(f"  - {len(titles_in_casual_titles)}/{len(titles_vids)} ({len(titles_in_casual_titles)/len(titles_vids)*100:.2f}%) in casualVoteTitles")
print(f"  - {len(titles_in_any_casual)}/{len(titles_vids)} ({len(titles_in_any_casual)/len(titles_vids)*100:.2f}%) in EITHER casual file")
print(f"  - {len(titles_not_in_any_casual)}/{len(titles_vids)} ({len(titles_not_in_any_casual)/len(titles_vids)*100:.2f}%) in NEITHER casual file")

print("\n" + "="*80)
print("CASUAL FILES → TITLES")
print("="*80)

casual_votes_in_titles = casual_votes_vids.intersection(titles_vids)
casual_votes_not_in_titles = casual_votes_vids - titles_vids

print(f"\n📊 Are casualVotes videoIDs in titles.csv?")
print(f"  - {len(casual_votes_in_titles)}/{len(casual_votes_vids)} ({len(casual_votes_in_titles)/len(casual_votes_vids)*100:.2f}%) ARE in titles")
print(f"  - {len(casual_votes_not_in_titles)}/{len(casual_votes_vids)} ({len(casual_votes_not_in_titles)/len(casual_votes_vids)*100:.2f}%) are NOT in titles")

casual_titles_in_titles = casual_titles_vids.intersection(titles_vids)
casual_titles_not_in_titles = casual_titles_vids - titles_vids

print(f"\n📊 Are casualVoteTitles videoIDs in titles.csv?")
print(f"  - {len(casual_titles_in_titles)}/{len(casual_titles_vids)} ({len(casual_titles_in_titles)/len(casual_titles_vids)*100:.2f}%) ARE in titles")
print(f"  - {len(casual_titles_not_in_titles)}/{len(casual_titles_vids)} ({len(casual_titles_not_in_titles)/len(casual_titles_vids)*100:.2f}%) are NOT in titles")

casual_all_in_titles = casual_all_vids.intersection(titles_vids)
casual_all_not_in_titles = casual_all_vids - titles_vids

print(f"\n📊 Are ANY casual file videoIDs in titles.csv?")
print(f"  - {len(casual_all_in_titles)}/{len(casual_all_vids)} ({len(casual_all_in_titles)/len(casual_all_vids)*100:.2f}%) ARE in titles")
print(f"  - {len(casual_all_not_in_titles)}/{len(casual_all_vids)} ({len(casual_all_not_in_titles)/len(casual_all_vids)*100:.2f}%) are NOT in titles")

print("\n" + "="*80)
print("SAMPLE ANALYSIS")
print("="*80)

if len(titles_not_in_any_casual) > 0:
    print(f"\nSample titles NOT in any casual file (first 5):")
    for vid in list(titles_not_in_any_casual)[:5]:
        row = titles[titles['videoID'] == vid].iloc[0]
        title_text = row['title'][:60] if pd.notna(row['title']) else "N/A"
        print(f"  - {vid}: \"{title_text}...\" (original={row['original']})")

if len(casual_all_not_in_titles) > 0:
    print(f"\nSample casual videos NOT in titles.csv (first 5):")
    for vid in list(casual_all_not_in_titles)[:5]:
        if vid in casual_titles_vids:
            row = casual_vote_titles[casual_vote_titles['videoID'] == vid].iloc[0]
            print(f"  - {vid}: \"{row['title'][:60]}...\" (from casualVoteTitles)")
        elif vid in casual_votes_vids:
            row = casual_votes[casual_votes['videoID'] == vid].iloc[0]
            print(f"  - {vid}: category='{row['category']}' (from casualVotes)")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"""
Key findings:
1. titles.csv contains {len(titles_vids)} unique videos
2. Casual files contain {len(casual_all_vids)} unique videos
3. Overlap: {len(titles_in_any_casual)} videos ({len(titles_in_any_casual)/len(titles_vids)*100:.1f}% of titles)

Interpretation:
- titles.csv is the MAIN repository of user-submitted alternative titles
- casualVotes/casualVoteTitles are SUBSETS focused on "casual" mode submissions
- Only ~{len(titles_in_any_casual)/len(titles_vids)*100:.0f}% of title submissions are marked as "casual"
- The casual files represent informal/unverified submissions
- Most titles ({len(titles_not_in_any_casual)/len(titles_vids)*100:.0f}%) are regular verified submissions
""")
