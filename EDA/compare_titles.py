import pandas as pd
from pathlib import Path

base = Path(r'C:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\deArrow_data')

print("Loading data...")
titles = pd.read_csv(base / 'titles.csv')
casual_vote_titles = pd.read_csv(base / 'casualVoteTitles.csv')

# Find videoIDs that appear in both
titles_videos = set(titles['videoID'].dropna().unique())
casual_videos = set(casual_vote_titles['videoID'].dropna().unique())
overlap_videos = list(titles_videos.intersection(casual_videos))

print(f"\nFound {len(overlap_videos)} videos with titles in BOTH files")
print("\n" + "="*100)
print("EXAMPLES: Same VideoID, Different Titles")
print("="*100)

# Show 10 examples
for i, vid in enumerate(overlap_videos[:10], 1):
    print(f"\n{'='*100}")
    print(f"EXAMPLE {i} - VideoID: {vid}")
    print('='*100)
    
    # Get titles from titles.csv
    titles_data = titles[titles['videoID'] == vid][['title', 'UUID']].copy()
    print(f"\n📄 TITLES.CSV ({len(titles_data)} alternative titles):")
    for idx, row in titles_data.head(5).iterrows():
        print(f"   • \"{row['title']}\"")
    
    if len(titles_data) > 5:
        print(f"   ... and {len(titles_data) - 5} more")
    
    # Get titles from casualVoteTitles
    casual_data = casual_vote_titles[casual_vote_titles['videoID'] == vid][['title', 'id']].copy()
    print(f"\n🎯 CASUALVOTETITLES.CSV ({len(casual_data)} casual vote titles):")
    for idx, row in casual_data.iterrows():
        print(f"   • [id={row['id']}] \"{row['title']}\"")
    
    print(f"\n💡 OBSERVATION:")
    # Check if any casualVoteTitles appear in titles.csv
    casual_title_set = set(casual_data['title'].str.lower().str.strip())
    titles_title_set = set(titles_data['title'].str.lower().str.strip())
    
    if casual_title_set.intersection(titles_title_set):
        print("   ⚠️  Some casualVoteTitles ALSO appear in titles.csv (exact match)")
    else:
        print("   ✓ casualVoteTitles are DIFFERENT from all titles in titles.csv")

print("\n" + "="*100)
print("SUMMARY")
print("="*100)
print("""
Key observations:
- titles.csv contains multiple user-submitted title alternatives for the same video
- casualVoteTitles.csv contains titles that received "casual votes" (community flagging)
- They are often DIFFERENT titles for the same video
- casualVoteTitles appear to be less clickbaity alternatives
""")
