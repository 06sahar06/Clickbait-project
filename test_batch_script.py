"""
Quick test of hardened batch_update_youtube_stats.py on a small sample (20 videoIDs).
"""

import os
import pandas as pd
import time
from pathlib import Path
import sys

# Set environment variables for testing
os.environ['YOUTUBE_SLEEP'] = '0.15'
os.environ['YOUTUBE_SAVE_EVERY'] = '500'

# Import the module we're testing
sys.path.insert(0, str(Path(__file__).parent))
from batch_update_youtube_stats import get_video_stats

def test_single_videos():
    """Test 10 sample videoIDs to verify exponential backoff works."""
    
    # Read all_in_one to get sample videoIDs
    all_in_one = Path("All_data/all_in_one.csv")
    if not all_in_one.exists():
        print(f"Error: {all_in_one} not found")
        return
    
    df = pd.read_csv(all_in_one)
    sample_ids = df['videoID'].dropna().unique()[:20]
    
    print("="*70)
    print(f"Testing {len(sample_ids)} sample videoIDs with exponential backoff")
    print("="*70)
    
    successful = 0
    for idx, vid in enumerate(sample_ids, 1):
        print(f"\n[{idx}/{len(sample_ids)}] Testing videoID: {vid}")
        stats = get_video_stats(str(vid).strip())
        
        if stats:
            print(f"  ✓ Success! Stats: Views={stats['Views']}, Channel={stats['channelID']}")
            successful += 1
        else:
            print(f"  ✗ Skipped or max retries reached")
        
        time.sleep(0.15)  # Base sleep between tests
    
    print("\n" + "="*70)
    print(f"Test complete: {successful}/{len(sample_ids)} successful")
    print("="*70)

if __name__ == "__main__":
    test_single_videos()
