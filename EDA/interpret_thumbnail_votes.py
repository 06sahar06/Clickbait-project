import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

print("Loading thumbnailVotes.csv...")
thumbnail_votes = pd.read_csv(base / 'thumbnailVotes.csv')

print("\n" + "="*80)
print("VOTE VALUE DISTRIBUTION")
print("="*80)

vote_counts = thumbnail_votes['votes'].value_counts().sort_index()
print(f"\nTotal rows: {len(thumbnail_votes)}")
print(f"\nVote value distribution:")
print(vote_counts)

print(f"\n\nVote statistics:")
print(thumbnail_votes['votes'].describe())

print("\n" + "="*80)
print("TOP VOTE VALUES (most common)")
print("="*80)
top_votes = thumbnail_votes['votes'].value_counts().head(15)
for vote_val, count in top_votes.items():
    pct = count / len(thumbnail_votes) * 100
    print(f"  votes={vote_val:3d}: {count:6d} rows ({pct:5.2f}%)")

print("\n" + "="*80)
print("NEGATIVE VS POSITIVE VS ZERO")
print("="*80)

negative = len(thumbnail_votes[thumbnail_votes['votes'] < 0])
zero = len(thumbnail_votes[thumbnail_votes['votes'] == 0])
positive = len(thumbnail_votes[thumbnail_votes['votes'] > 0])

print(f"\nNegative votes (< 0): {negative:6d} ({negative/len(thumbnail_votes)*100:5.2f}%)")
print(f"Zero votes    (= 0): {zero:6d} ({zero/len(thumbnail_votes)*100:5.2f}%)")
print(f"Positive votes (> 0): {positive:6d} ({positive/len(thumbnail_votes)*100:5.2f}%)")

print("\n" + "="*80)
print("VOTE INTERPRETATION")
print("="*80)

print(f"""
Based on the distribution, the 'votes' column likely represents:

- Positive values (1, 2, 3...): NET upvotes
  → Community approval of this thumbnail as a better alternative
  → Higher values = more community approval
  
- Zero (0): Neutral or no net votes yet
  → Either no one has voted, or equal up/downvotes
  → Most thumbnails fall into this category ({zero/len(thumbnail_votes)*100:.1f}%)
  
- Negative values (-1, -2, -3...): NET downvotes
  → Community disapproval of this thumbnail
  → Suggests this thumbnail is NOT a good alternative
  → Lower values = more community rejection

The 'downvotes' column likely tracks separate downvote counts.
The 'votes' column appears to be: (upvotes - downvotes) = net score

This is similar to Reddit's voting system where:
- Good content gets positive karma
- Bad content gets negative karma
- Most content hovers around 0
""")

# Check relationship with downvotes column
print("\n" + "="*80)
print("RELATIONSHIP: votes vs downvotes")
print("="*80)

sample_negative = thumbnail_votes[thumbnail_votes['votes'] < 0].head(5)
print("\nSample rows with negative votes:")
print(sample_negative[['UUID', 'votes', 'downvotes', 'locked', 'shadowHidden']])

sample_positive = thumbnail_votes[thumbnail_votes['votes'] > 0].head(5)
print("\nSample rows with positive votes:")
print(sample_positive[['UUID', 'votes', 'downvotes', 'locked', 'shadowHidden']])
