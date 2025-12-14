import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

print("Loading data...")
casual_votes = pd.read_csv(base / 'casualVotes.csv')
casual_vote_titles = pd.read_csv(base / 'casualVoteTitles.csv')

# Get unique videoIDs from each file
casual_votes_vids = set(casual_votes['videoID'].dropna().unique())
casual_titles_vids = set(casual_vote_titles['videoID'].dropna().unique())

# Get videos ONLY in casualVotes
only_in_votes = casual_votes_vids - casual_titles_vids

print(f"\nTotal videos ONLY in casualVotes: {len(only_in_votes)}")
print("\n" + "="*80)
print("Sample of 20 videoIDs that appear ONLY in casualVotes:")
print("="*80)

sample_vids = list(only_in_votes)[:20]
for i, vid in enumerate(sample_vids, 1):
    row = casual_votes[casual_votes['videoID'] == vid].iloc[0]
    print(f"{i:2}. {vid} - category: '{row['category']}', upvotes: {row['upvotes']}")

print("\n" + "="*80)
print("VideoIDs as comma-separated list:")
print("="*80)
print(", ".join(sample_vids))
