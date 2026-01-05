import os
import pandas as pd

ALLOWED = ["channelID", "Views", "Published", "likes", "comments"]


def check_file(path):
    counts = {c: 0 for c in ALLOWED}
    total = 0
    chunksize = 100_000
    try:
        for chunk in pd.read_csv(path, chunksize=chunksize):
            total += len(chunk)
            for c in ALLOWED:
                if c in chunk.columns:
                    # treat NaN or empty-string as empty
                    vals = chunk[c].fillna("").astype(str).str.strip()
                    counts[c] += (vals != "").sum()
    except pd.errors.EmptyDataError:
        return path, 0, counts
    return path, total, counts


def main():
    base = "All_data"
    files = [f for f in os.listdir(base) if f.endswith(".csv") and f != "channels_multiple_videos.csv"]
    results = []
    for f in sorted(files):
        path = os.path.join(base, f)
        p, total, counts = check_file(path)
        results.append((f, total, counts))

    print("file,total,channelID,Views,Published,likes,comments")
    for f, total, counts in results:
        row = [f, str(total)] + [str(counts[c]) for c in ALLOWED]
        print(",".join(row))


if __name__ == '__main__':
    main()
