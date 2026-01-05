import pandas as pd


def main(fn="All_data/all_in_one.csv"):
    chunksize = 100_000
    total_rows = 0
    nonempty_title = 0
    # map channelID -> set of videoIDs
    ch_map = {}

    usecols = ["videoID", "channelID", "title"]
    for chunk in pd.read_csv(fn, usecols=usecols, chunksize=chunksize):
        total_rows += len(chunk)
        # count non-empty title cells
        t = chunk["title"].fillna("").astype(str).str.strip()
        nonempty_title += (t != "").sum()

        # build channel -> videoID sets
        for ch, vid in zip(chunk["channelID"], chunk["videoID"]):
            if pd.isna(ch) or ch == "":
                continue
            s = ch_map.get(ch)
            if s is None:
                ch_map[ch] = {vid}
            else:
                s.add(vid)

    # channelIDs with >1 distinct videoIDs
    multi = {ch: vids for ch, vids in ch_map.items() if len(vids) > 1}

    print(f"Total rows scanned: {total_rows}")
    print(f"Non-empty `title` cells: {nonempty_title} ({nonempty_title/total_rows:.2%})")
    print("")
    print(f"ChannelIDs present: {len(ch_map)}")
    print(f"ChannelIDs with >1 distinct videoIDs: {len(multi)}")
    if multi:
        print("Sample channelIDs with multiple videoIDs (showing up to 20, format: channelID -> count):")
        cnt = 0
        for ch, vids in list(multi.items())[:20]:
            print(f"{ch} -> {len(vids)}")
            cnt += 1
        if len(multi) > cnt:
            print(f"... (+{len(multi)-cnt} more)")


if __name__ == '__main__':
    main()
