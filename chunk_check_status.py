import pandas as pd
from pathlib import Path

CSV_PATH = Path("All_data/all_in_one.csv")
CHUNKSIZE = 50_000
STAT_COLS = ["channelID", "Views", "Published", "likes", "comments"]

if not CSV_PATH.exists():
    print(f"Missing file: {CSV_PATH}")
    raise SystemExit(1)

bad_video_ids = set()
bad_rows = 0
total_rows = 0

for chunk in pd.read_csv(CSV_PATH, usecols=["videoID", *STAT_COLS], dtype=str, chunksize=CHUNKSIZE):
    chunk = chunk.fillna("")
    stats = chunk[STAT_COLS]

    # Good if all stats are present and not -1
    all_filled = stats.ne("").all(axis=1) & stats.ne("-1").all(axis=1)
    # Also good if all stats are exactly -1 (unavailable/private/deleted)
    all_neg1 = stats.eq("-1").all(axis=1)

    good_mask = all_filled | all_neg1
    bad_mask = ~good_mask

    total_rows += len(chunk)
    bad_rows += int(bad_mask.sum())
    bad_video_ids.update(chunk.loc[bad_mask & chunk["videoID"].ne(""), "videoID"])

print(f"Total rows checked: {total_rows}")
print(f"Rows not satisfying filled-or--1 rule: {bad_rows}")
print(f"Unique videoIDs needing attention: {len(bad_video_ids)}")
