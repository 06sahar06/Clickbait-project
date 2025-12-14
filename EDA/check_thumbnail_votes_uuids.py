import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

print("Loading data...")
thumbnails = pd.read_csv(base / 'thumbnails.csv')
thumbnail_timestamps = pd.read_csv(base / 'thumbnailTimestamps.csv')
thumbnail_votes = pd.read_csv(base / 'thumbnailVotes.csv')

# Get unique UUIDs
thumbnails_uuids = set(thumbnails['UUID'].dropna().unique())
timestamps_uuids = set(thumbnail_timestamps['UUID'].dropna().unique())
votes_uuids = set(thumbnail_votes['UUID'].dropna().unique())

print("\n" + "="*80)
print("FILE SIZES")
print("="*80)
print(f"thumbnails.csv: {len(thumbnails)} rows, {len(thumbnails_uuids)} unique UUIDs")
print(f"thumbnailTimestamps.csv: {len(thumbnail_timestamps)} rows, {len(timestamps_uuids)} unique UUIDs")
print(f"thumbnailVotes.csv: {len(thumbnail_votes)} rows, {len(votes_uuids)} unique UUIDs")

print("\n" + "="*80)
print("THUMBNAILVOTES → THUMBNAILS")
print("="*80)

votes_in_thumbs = votes_uuids.intersection(thumbnails_uuids)
votes_not_in_thumbs = votes_uuids - thumbnails_uuids

print(f"\n📊 Are thumbnailVotes UUIDs in thumbnails.csv?")
print(f"  - {len(votes_in_thumbs)}/{len(votes_uuids)} ({len(votes_in_thumbs)/len(votes_uuids)*100:.2f}%) ARE in thumbnails")
print(f"  - {len(votes_not_in_thumbs)}/{len(votes_uuids)} ({len(votes_not_in_thumbs)/len(votes_uuids)*100:.2f}%) are NOT in thumbnails")

if len(votes_not_in_thumbs) > 0:
    print(f"\n⚠️  Sample UUIDs in votes but NOT in thumbnails (first 5):")
    for uuid in list(votes_not_in_thumbs)[:5]:
        vote_row = thumbnail_votes[thumbnail_votes['UUID'] == uuid].iloc[0]
        print(f"  - {uuid}: votes={vote_row['votes']}, locked={vote_row['locked']}")

print("\n" + "="*80)
print("THUMBNAILVOTES → THUMBNAILTIMESTAMPS")
print("="*80)

votes_in_timestamps = votes_uuids.intersection(timestamps_uuids)
votes_not_in_timestamps = votes_uuids - timestamps_uuids

print(f"\n📊 Are thumbnailVotes UUIDs in thumbnailTimestamps.csv?")
print(f"  - {len(votes_in_timestamps)}/{len(votes_uuids)} ({len(votes_in_timestamps)/len(votes_uuids)*100:.2f}%) ARE in timestamps")
print(f"  - {len(votes_not_in_timestamps)}/{len(votes_uuids)} ({len(votes_not_in_timestamps)/len(votes_uuids)*100:.2f}%) are NOT in timestamps")

print("\n" + "="*80)
print("REVERSE: THUMBNAILS → THUMBNAILVOTES")
print("="*80)

thumbs_in_votes = thumbnails_uuids.intersection(votes_uuids)
thumbs_not_in_votes = thumbnails_uuids - votes_uuids

print(f"\n📊 Are thumbnails UUIDs in thumbnailVotes.csv?")
print(f"  - {len(thumbs_in_votes)}/{len(thumbnails_uuids)} ({len(thumbs_in_votes)/len(thumbnails_uuids)*100:.2f}%) ARE in votes")
print(f"  - {len(thumbs_not_in_votes)}/{len(thumbnails_uuids)} ({len(thumbs_not_in_votes)/len(thumbnails_uuids)*100:.2f}%) are NOT in votes")

print("\n" + "="*80)
print("REVERSE: THUMBNAILTIMESTAMPS → THUMBNAILVOTES")
print("="*80)

timestamps_in_votes = timestamps_uuids.intersection(votes_uuids)
timestamps_not_in_votes = timestamps_uuids - votes_uuids

print(f"\n📊 Are thumbnailTimestamps UUIDs in thumbnailVotes.csv?")
print(f"  - {len(timestamps_in_votes)}/{len(timestamps_uuids)} ({len(timestamps_in_votes)/len(timestamps_uuids)*100:.2f}%) ARE in votes")
print(f"  - {len(timestamps_not_in_votes)}/{len(timestamps_uuids)} ({len(timestamps_not_in_votes)/len(timestamps_uuids)*100:.2f}%) are NOT in votes")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if len(votes_in_thumbs) == len(votes_uuids):
    print(f"\n✅ All thumbnailVotes UUIDs are in thumbnails.csv")
else:
    print(f"\n⚠️  {len(votes_not_in_thumbs)} vote UUIDs are NOT in thumbnails ({len(votes_not_in_thumbs)/len(votes_uuids)*100:.1f}%)")

if abs(len(thumbs_in_votes) - len(thumbnails_uuids)) < 10:
    print(f"✅ Nearly all thumbnails have votes")
else:
    print(f"⚠️  Only {len(thumbs_in_votes)/len(thumbnails_uuids)*100:.1f}% of thumbnails have vote records")

print(f"\nInterpretation:")
print(f"  - thumbnailVotes tracks community voting on submitted thumbnails")
print(f"  - Not all thumbnails may have votes yet (newly submitted)")
print(f"  - Votes may be stored separately from the thumbnail/timestamp submission data")
