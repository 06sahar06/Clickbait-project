import sys
from pathlib import Path
import pandas as pd


def find_uuid_col(df):
    cols = list(df.columns)
    # Prefer columns containing 'uuid' (case-insensitive)
    for c in cols:
        if 'uuid' in str(c).lower():
            return c
    # Fallbacks
    for cand in ['id', 'ID', 'Id']:
        if cand in cols:
            return cand
    return None


def main():
    root = Path(__file__).resolve().parents[1]
    titles_csv = root / 'All_data' / 'titles_only.csv'
    votes_csv = root / 'deArrow_data' / 'titleVotes.csv'

    if not titles_csv.exists():
        print(f"ERROR: File not found: {titles_csv}")
        sys.exit(1)
    if not votes_csv.exists():
        print(f"ERROR: File not found: {votes_csv}")
        sys.exit(1)

    print(f"Reading: {titles_csv}")
    titles_df = pd.read_csv(titles_csv, low_memory=False)
    print(f"Reading: {votes_csv}")
    votes_df = pd.read_csv(votes_csv, low_memory=False)

    titles_col = find_uuid_col(titles_df)
    votes_col = find_uuid_col(votes_df)

    if not titles_col:
        print("ERROR: Could not detect UUID column in titles_only.csv")
        print(f"Columns: {list(titles_df.columns)[:20]} ...")
        sys.exit(2)
    if not votes_col:
        print("ERROR: Could not detect UUID column in titleVotes.csv")
        print(f"Columns: {list(votes_df.columns)[:20]} ...")
        sys.exit(2)

    print(f"Detected UUID columns -> titles_only: '{titles_col}', titleVotes: '{votes_col}'")

    titles_set = set(titles_df[titles_col].dropna().astype(str))
    votes_set = set(votes_df[votes_col].dropna().astype(str))

    total_titles = len(titles_set)
    total_votes = len(votes_set)
    overlap = len(titles_set & votes_set)
    missing_in_votes = titles_set - votes_set

    print("\nUUID coverage:")
    print(f"- titles_only unique UUIDs: {total_titles}")
    print(f"- titleVotes unique UUIDs: {total_votes}")
    print(f"- Overlap: {overlap} ({(overlap/total_titles*100 if total_titles else 0):.2f}% of titles)")
    print(f"- Missing in titleVotes: {len(missing_in_votes)}")

    if missing_in_votes:
        sample = list(missing_in_votes)[:10]
        print(f"\nSample missing UUIDs ({len(sample)}):")
        for s in sample:
            print(f"- {s}")

if __name__ == '__main__':
    main()
