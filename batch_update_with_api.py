"""
Batch update all_in_one.csv with YouTube video statistics using YouTube Data API.
Fetches channelID, Views, Published, likes, and comments for each videoID.
Uses YouTube Data API v3 with proper rate limiting and checkpointing.
"""

import os
import sys
import pandas as pd
import time
from pathlib import Path
from typing import Dict, Optional
import requests

# Ensure UTF-8 output handling
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SLEEP_PER_REQUEST = 0.1  # 100ms between requests (well under quota limits)
SAVE_EVERY = 5000  # Save checkpoint every 5000 videos (reduce memory reloads)
BATCH_SIZE = 50  # Fetch this many videos per API call (API supports up to 50)


def get_videos_stats_batch(video_ids: list, api_key: str) -> Dict[str, Dict]:
    """
    Fetch statistics for multiple YouTube videos in one API call.
    
    Args:
        video_ids: List of YouTube video IDs (max 50)
        api_key: YouTube Data API v3 key
    
    Returns:
        Dictionary mapping video_id to stats dict
    """
    if not api_key:
        raise ValueError("YouTube API key not provided. Set YOUTUBE_API_KEY environment variable.")
    
    base_url = "https://www.googleapis.com/youtube/v3/videos"
    
    # Join video IDs with commas (API accepts up to 50)
    video_ids_str = ','.join(video_ids[:BATCH_SIZE])
    
    params = {
        'part': 'snippet,statistics',
        'id': video_ids_str,
        'key': api_key
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = {}
        for item in data.get('items', []):
            video_id = item['id']
            snippet = item.get('snippet', {})
            stats = item.get('statistics', {})
            
            # Parse published date
            published = snippet.get('publishedAt', '')
            if published:
                # Convert from ISO format to YYYY-MM-DD
                published = published.split('T')[0]
            
            results[video_id] = {
                'channelID': snippet.get('channelId', ''),
                'Views': int(stats.get('viewCount', 0)),
                'Published': published,
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0))
            }
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"  [API Error] {e}")
        return {}
    except Exception as e:
        print(f"  [Error] {e}")
        return {}


def update_all_in_one_with_api():
    """
    Update all_in_one.csv with YouTube statistics using the official API.
    Processes in chunks to avoid memory issues with large files.
    Resumes from last checkpoint automatically.
    """
    csv_path = Path(r"c:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\All_data\all_in_one.csv")
    
    if not YOUTUBE_API_KEY:
        print("="*70)
        print("ERROR: YouTube API key not found!")
        print("="*70)
        print("\nTo use this script, you need a YouTube Data API v3 key.")
        print("\nSteps to get an API key:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project (or select existing)")
        print("3. Enable 'YouTube Data API v3'")
        print("4. Create credentials (API key)")
        print("5. Set it as environment variable:")
        print("   $env:YOUTUBE_API_KEY = 'your-api-key-here'")
        print("\nQuota limits: 10,000 units/day (each batch request = 1 unit)")
        print("With batch size 50, you can fetch ~500,000 videos per day")
        print("="*70)
        return
    
    print("="*70)
    print("Updating all_in_one.csv with YouTube Data API v3 (Chunked Mode)")
    print("="*70)
    
    try:
        # First pass: identify all videos needing stats
        print("\nScanning file for videos needing stats...")
        all_missing = set()
        
        chunk_size = 50000  # Process 50k rows at a time to avoid memory issues
        for chunk_num, chunk in enumerate(pd.read_csv(csv_path, chunksize=chunk_size, dtype={'category': str, 'original_title': str})):
            # Find videos in this chunk that need fetching
            missing_mask = (
                chunk['videoID'].notna() & 
                (chunk['Views'] != -1) &  # Skip previously failed videos
                (
                    chunk['channelID'].isna() |
                    chunk['Views'].isna() |
                    chunk['Published'].isna() |
                    chunk['likes'].isna() |
                    chunk['comments'].isna()
                )
            )
            chunk_missing = chunk.loc[missing_mask, 'videoID'].dropna().unique().tolist()
            all_missing.update(chunk_missing)
            
            if (chunk_num + 1) % 2 == 0:
                print(f"  Scanned chunk {chunk_num + 1}... Found {len(all_missing)} unique videos so far")
        
        unique_videos = list(all_missing)
        total_videos = len(unique_videos)
        
        if total_videos == 0:
            print("\n✓ All videos already have statistics!")
            return
        
        print(f"\nFound {total_videos:,} unique videoIDs needing stats")
        print(f"Fetching in batches of {BATCH_SIZE}...")
        print(f"Estimated API calls: {(total_videos + BATCH_SIZE - 1) // BATCH_SIZE:,}")
        print(f"Saving checkpoint every {SAVE_EVERY} videos\n")
        
        # Process in chunks and update
        successful = 0
        failed = 0
        start_time = time.time()
        
        for i in range(0, total_videos, BATCH_SIZE):
            batch = unique_videos[i:i+BATCH_SIZE]
            current_idx = i + len(batch)
            
            # Fetch batch
            batch_results = get_videos_stats_batch(batch, YOUTUBE_API_KEY)
            
            successful += len(batch_results)
            failed += len(batch) - len(batch_results)
            
            # Progress update
            if current_idx % 500 == 0 or current_idx >= total_videos:
                elapsed = time.time() - start_time
                rate = successful / elapsed if elapsed > 0 else 0
                eta_seconds = (total_videos - current_idx) / rate if rate > 0 else 0
                eta_minutes = eta_seconds / 60
                
                print(f"Progress: {current_idx:,}/{total_videos:,} ({current_idx/total_videos*100:.1f}%) | "
                      f"Success: {successful:,} | Failed: {failed} | "
                      f"Rate: {rate:.1f} vid/s | ETA: {eta_minutes:.1f}min")
            
            # Save checkpoint: only update relevant rows for this batch
            if current_idx % SAVE_EVERY == 0 or current_idx >= total_videos:
                print(f"  ✓ Saving checkpoint at {current_idx:,}/{total_videos:,}...")
                _update_csv_chunk(csv_path, batch, batch_results)
                print(f"    Checkpoint saved")
            
            # Rate limiting
            time.sleep(SLEEP_PER_REQUEST)
        
        elapsed = time.time() - start_time
        print("\n" + "="*70)
        print(f"✓ Update complete!")
        print(f"  Successfully fetched: {successful:,}/{total_videos:,}")
        print(f"  Failed: {failed}")
        print(f"  Time elapsed: {elapsed/60:.1f} minutes")
        print(f"  Average rate: {successful/elapsed:.1f} videos/second")
        print("="*70)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


def _update_csv_chunk(csv_path: Path, batch: list, batch_results: Dict):
    """Update only the rows for this batch to save memory."""
    # Read with error handling for corrupted lines
    try:
        df = pd.read_csv(csv_path, on_bad_lines='skip', engine='python')
    except:
        # Fallback: try with different options
        df = pd.read_csv(csv_path, error_bad_lines=False, warn_bad_lines=True, engine='python')
    
    # Update successful fetches
    for video_id, stats in batch_results.items():
        mask = df['videoID'] == video_id
        df.loc[mask, 'channelID'] = stats['channelID']
        df.loc[mask, 'Views'] = stats['Views']
        df.loc[mask, 'Published'] = stats['Published']
        df.loc[mask, 'likes'] = stats['likes']
        df.loc[mask, 'comments'] = stats['comments']
    
    # Mark failed videos
    failed_videos = set(batch) - set(batch_results.keys())
    for video_id in failed_videos:
        mask = df['videoID'] == video_id
        df.loc[mask, 'Views'] = -1  # Mark as failed
        df.loc[mask, 'channelID'] = ''
        df.loc[mask, 'Published'] = ''
        df.loc[mask, 'likes'] = -1
        df.loc[mask, 'comments'] = -1
    
    # Write safely with quoting to prevent corruption
    df.to_csv(csv_path, index=False, quoting=1)  # QUOTE_ALL to protect data


if __name__ == "__main__":
    update_all_in_one_with_api()
