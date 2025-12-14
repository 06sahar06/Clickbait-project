import pandas as pd
from pathlib import Path
base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')
files = ['casualVotes.csv','casualVoteTitles.csv','thumbnails.csv','thumbnailTimestamps.csv','thumbnailVotes.csv','titles.csv','titleVotes.csv','videoInfo.csv']
summary = {}
for f in files:
    path = base / f
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f'{f}: READ ERROR: {e}')
        summary[f] = None
        continue
    total_missing = int(df.isnull().sum().sum())
    summary[f] = total_missing
    print(f'{f}: missing values = {total_missing}')

print('\nFiles with missing values:')
for f,m in summary.items():
    if m is None:
        print('-', f, '(read error)')
    elif m>0:
        print('-', f, m)
