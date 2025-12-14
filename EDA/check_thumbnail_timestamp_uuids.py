import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

print("Loading data...")
thumbnails = pd.read_csv(base / 'thumbnails.csv')
thumbnail_timestamps = pd.read_csv(base / 'thumbnailTimestamps.csv')

# Get unique UUIDs
thumbnails_uuids = set(thumbnails['UUID'].dropna().unique())
timestamps_uuids = set(thumbnail_timestamps['UUID'].dropna().unique())

print("\n" + "="*80)
print("FILE SIZES")
print("="*80)
print(f"thumbnails.csv: {len(thumbnails)} rows, {len(thumbnails_uuids)} unique UUIDs")
print(f"thumbnailTimestamps.csv: {len(thumbnail_timestamps)} rows, {len(timestamps_uuids)} unique UUIDs")

print("\n" + "="*80)
print("THUMBNAILTIMESTAMPS → THUMBNAILS (Are timestamp UUIDs in thumbnails?)")
print("="*80)

timestamps_in_thumbs = timestamps_uuids.intersection(thumbnails_uuids)
timestamps_not_in_thumbs = timestamps_uuids - thumbnails_uuids

print(f"\n📊 thumbnailTimestamps.csv vs thumbnails.csv:")
print(f"  - {len(timestamps_in_thumbs)}/{len(timestamps_uuids)} ({len(timestamps_in_thumbs)/len(timestamps_uuids)*100:.2f}%) of timestamp UUIDs ARE in thumbnails")
print(f"  - {len(timestamps_not_in_thumbs)}/{len(timestamps_uuids)} ({len(timestamps_not_in_thumbs)/len(timestamps_uuids)*100:.2f}%) of timestamp UUIDs are NOT in thumbnails")

if len(timestamps_not_in_thumbs) > 0:
    print(f"\n⚠️  Sample UUIDs in timestamps but NOT in thumbnails (first 5):")
    for uuid in list(timestamps_not_in_thumbs)[:5]:
        print(f"  - {uuid}")

print("\n" + "="*80)
print("THUMBNAILS → THUMBNAILTIMESTAMPS (Are thumbnail UUIDs in timestamps?)")
print("="*80)

thumbs_in_timestamps = thumbnails_uuids.intersection(timestamps_uuids)
thumbs_not_in_timestamps = thumbnails_uuids - timestamps_uuids

print(f"\n📊 thumbnails.csv vs thumbnailTimestamps.csv:")
print(f"  - {len(thumbs_in_timestamps)}/{len(thumbnails_uuids)} ({len(thumbs_in_timestamps)/len(thumbnails_uuids)*100:.2f}%) of thumbnail UUIDs ARE in timestamps")
print(f"  - {len(thumbs_not_in_timestamps)}/{len(thumbnails_uuids)} ({len(thumbs_not_in_timestamps)/len(thumbnails_uuids)*100:.2f}%) of thumbnail UUIDs are NOT in timestamps")

if len(thumbs_not_in_timestamps) > 0:
    print(f"\n⚠️  Sample UUIDs in thumbnails but NOT in timestamps (first 5):")
    sample_missing = list(thumbs_not_in_timestamps)[:5]
    for uuid in sample_missing:
        thumb_row = thumbnails[thumbnails['UUID'] == uuid].iloc[0]
        print(f"  - {uuid}: videoID={thumb_row['videoID']}, original={thumb_row['original']}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if len(timestamps_not_in_thumbs) == 0 and len(thumbs_not_in_timestamps) == 0:
    print("\n✅ PERFECT MATCH - All UUIDs match in both files!")
    print("   thumbnailTimestamps and thumbnails have identical UUID sets.")
elif len(timestamps_not_in_thumbs) == 0:
    print(f"\n✅ thumbnailTimestamps is a SUBSET of thumbnails")
    print(f"   {len(thumbs_not_in_timestamps)} thumbnails have no timestamp data")
elif len(thumbs_not_in_timestamps) == 0:
    print(f"\n❌ thumbnailTimestamps has EXTRA UUIDs not in thumbnails")
    print(f"   {len(timestamps_not_in_thumbs)} orphaned timestamp records")
else:
    print(f"\n⚠️  PARTIAL OVERLAP - Both files have unique UUIDs")
    print(f"   - {len(thumbs_not_in_timestamps)} thumbnails missing timestamps")
    print(f"   - {len(timestamps_not_in_thumbs)} timestamps without thumbnails")

print(f"\nInterpretation:")
print(f"  - Thumbnails with original=1 may not need timestamps (using YouTube's thumbnail)")
print(f"  - Timestamps specify which frame of the video to use as thumbnail")
