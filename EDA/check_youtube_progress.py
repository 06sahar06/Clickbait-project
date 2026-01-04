import os
import argparse
from pathlib import Path
import pandas as pd


REQUIRED_COLS = ['channelID', 'Views', 'Published', 'likes', 'comments']


def summarize_csv(csv_path: Path):
    df = pd.read_csv(csv_path, low_memory=False)

    present = [c for c in REQUIRED_COLS if c in df.columns]
    if not present:
        return {
            'file': csv_path.name,
            'total': 0,
            'complete': 0,
            'missing': 0,
            'pct': 0.0,
        }

    if 'videoID' not in df.columns:
        return {
            'file': csv_path.name,
            'total': 0,
            'complete': 0,
            'missing': 0,
            'pct': 0.0,
        }

    def is_complete(group):
        return all(group[c].notna().any() for c in present)

    complete_series = df.groupby('videoID', dropna=False).apply(is_complete)
    total_ids = int(complete_series.shape[0])
    complete_ids = int(complete_series.sum())
    missing_ids = total_ids - complete_ids
    pct_complete = (complete_ids / total_ids * 100.0) if total_ids else 0.0

    return {
        'file': csv_path.name,
        'total': total_ids,
        'complete': complete_ids,
        'missing': missing_ids,
        'pct': pct_complete,
    }


def main():
    parser = argparse.ArgumentParser(description='Summarize YouTube stats enrichment progress')
    parser.add_argument('--file', type=str, help='Specific CSV filename under All_data to summarize')
    parser.add_argument('--all', action='store_true', help='Summarize all CSVs under All_data')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    all_dir = root / 'All_data'

    sleep_s = os.environ.get('YOUTUBE_SLEEP') or os.environ.get('YOUTUBE_API_SLEEP')
    try:
        sleep_s = float(sleep_s) if sleep_s is not None else 0.2
    except ValueError:
        sleep_s = 0.2

    targets = []
    if args.all:
        targets = sorted(all_dir.glob('*.csv'))
        if not targets:
            print('No CSV files found in All_data')
            return
    else:
        csv_name = args.file or 'all_in_one.csv'
        csv_path = all_dir / csv_name
        if not csv_path.exists():
            print(f"ERROR: File not found: {csv_path}")
            return
        targets = [csv_path]

    total_sum = {'total': 0, 'complete': 0, 'missing': 0}
    results = []
    for csv_path in targets:
        res = summarize_csv(csv_path)
        results.append(res)
        total_sum['total'] += res['total']
        total_sum['complete'] += res['complete']
        total_sum['missing'] += res['missing']

    for r in results:
        print(f"{r['file']}: total_unique={r['total']}, complete={r['complete']}, missing={r['missing']} ({r['pct']:.2f}%)")

    eta_hours = (total_sum['missing'] * sleep_s) / 3600.0
    print(f"\nTOTAL: total_unique={total_sum['total']}, complete={total_sum['complete']}, missing={total_sum['missing']}")
    print(f"Approx. remaining time (@{sleep_s:.2f}s/ID): {eta_hours:.2f} hours")


if __name__ == '__main__':
    main()
