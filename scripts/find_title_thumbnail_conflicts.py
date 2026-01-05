import pandas as pd


def main():
    fn = "All_data/all_in_one.csv"
    chunksize = 100_000
    mask = {}

    for chunk in pd.read_csv(fn, usecols=["videoID", "title/thumbnail"], chunksize=chunksize):
        for vid, t in zip(chunk["videoID"], chunk["title/thumbnail"]):
            if pd.isna(t):
                continue
            key = vid
            v = mask.get(key, 0)
            tt = str(t).strip().lower()
            if tt.startswith("title"):
                v |= 1
            elif tt.startswith("thumb"):
                v |= 2
            mask[key] = v

    both = [k for k, v in mask.items() if v == 3]
    print(f"Found {len(both)} videoIDs with both title and thumbnail submissions")
    if both:
        print("Sample (up to 20):")
        for vid in both[:20]:
            print(vid)


if __name__ == "__main__":
    main()
