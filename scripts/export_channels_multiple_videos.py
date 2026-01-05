import pandas as pd


def main(infile="All_data/all_in_one.csv", outfile="All_data/channels_multiple_videos.csv"):
    cols = ["videoID", "channelID", "title/thumbnail", "Published", "nb_submissions"]
    chunksize = 100_000

    channels = {}  # channelID -> { videoID -> info }

    for chunk in pd.read_csv(infile, usecols=cols, chunksize=chunksize):
        for vid, ch, ttype, pub, nb in zip(chunk["videoID"], chunk["channelID"], chunk["title/thumbnail"], chunk["Published"], chunk["nb_submissions"]):
            if pd.isna(ch) or ch == "":
                continue
            chd = channels.setdefault(ch, {})
            v = chd.get(vid)
            if v is None:
                v = {
                    "published": None,
                    "types": set(),
                    "nb_title_max": None,
                    "nb_thumb_max": None,
                }
                chd[vid] = v

            # published: keep first non-null
            if v["published"] is None and not pd.isna(pub):
                v["published"] = pub

            if not pd.isna(ttype):
                s = str(ttype).strip().lower()
                if s.startswith("title"):
                    v["types"].add("title")
                    try:
                        if not pd.isna(nb):
                            n = int(nb)
                            if v["nb_title_max"] is None or n > v["nb_title_max"]:
                                v["nb_title_max"] = n
                    except Exception:
                        pass
                elif s.startswith("thumb"):
                    v["types"].add("thumbnail")
                    try:
                        if not pd.isna(nb):
                            n = int(nb)
                            if v["nb_thumb_max"] is None or n > v["nb_thumb_max"]:
                                v["nb_thumb_max"] = n
                    except Exception:
                        pass
                else:
                    v["types"].add(s)

    # collect rows for channels with >1 videos
    rows = []
    chan_count = 0
    for ch, vids in channels.items():
        if len(vids) <= 1:
            continue
        chan_count += 1
        for vid, info in vids.items():
            rows.append({
                "channelID": ch,
                "videoID": vid,
                "Published": info["published"],
                "submission_types": ";".join(sorted(info["types"])) if info["types"] else "",
                "nb_title_max": info["nb_title_max"],
                "nb_thumb_max": info["nb_thumb_max"],
            })

    df = pd.DataFrame(rows)
    df.to_csv(outfile, index=False)
    print(f"Wrote {len(df)} rows for {chan_count} channels to {outfile}")


if __name__ == '__main__':
    main()
