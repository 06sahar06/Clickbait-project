"""
Batch update All_data CSV files with YouTube video statistics.
Fetches channelID, Views, Published, likes, and comments for each videoID.
Uses yt-dlp with exponential backoff and resilient error handling.
"""

import os
import sys
import pandas as pd
import time
from pathlib import Path
from typing import Dict, Optional
import json
import yt_dlp
from socket import timeout as socket_timeout
from urllib.error import URLError

# Ensure UTF-8 output handling for emojis and special characters
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# Tuning knobs
BASE_SLEEP = float(os.getenv("YOUTUBE_SLEEP", "0.2"))  # base delay between requests
SAVE_EVERY = int(os.getenv("YOUTUBE_SAVE_EVERY", "500"))  # flush to CSV every N fetches
MAX_RETRIES = 3  # retries per video on timeout/connection error
BACKOFF_FACTOR = 1.5  # exponential backoff multiplier


def get_video_stats(video_id: str, retry_count: int = 0) -> Optional[Dict]:
    """
    Fetch statistics for a YouTube video using yt-dlp with exponential backoff.
    
    Args:
        video_id: YouTube video ID
        retry_count: Current retry attempt
    
    Returns:
        Dictionary with video statistics or None if all retries fail
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'socket_timeout': 10,  # 10 second timeout
            'http_chunk_size': 1024 * 1024,  # 1MB chunks for slow connections
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
        
        if not info:
            return None
        
        # Convert upload_date YYYYMMDD to ISO format
        upload_date = info.get('upload_date', '')
        if upload_date and len(upload_date) == 8:
            published = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
        else:
            published = ''
        
        return {
            'channelID': info.get('channel_id', ''),
            'Views': int(info.get('view_count', 0)) if info.get('view_count') else 0,
            'Published': published,
            'likes': int(info.get('like_count', 0)) if info.get('like_count') else 0,
            'comments': int(info.get('comment_count', 0)) if info.get('comment_count') else 0
        }
        
    except (socket_timeout, URLError, ConnectionError, TimeoutError) as e:
        # Transient network errors: retry with exponential backoff
        if retry_count < MAX_RETRIES:
            wait = BASE_SLEEP * (BACKOFF_FACTOR ** retry_count)
            print(f"  [Retry {retry_count+1}/{MAX_RETRIES}] {video_id}: {type(e).__name__}, waiting {wait:.1f}s...")
            time.sleep(wait)
            return get_video_stats(video_id, retry_count=retry_count + 1)
        else:
            print(f"  [Max retries exhausted] {video_id}: {type(e).__name__}")
            # After max retries, mark as -1 (assume unreachable)
            return {
                'channelID': '-1',
                'Views': -1,
                'Published': '-1',
                'likes': -1,
                'comments': -1
            }
    
    except Exception as e:
        # All other errors (video unavailable, private, etc.): mark as -1
        error_msg = str(e)
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        try:
            print(f"  [Unavailable] {video_id}: {error_msg}")
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Handle emoji or special character encoding issues in error messages
            print(f"  [Unavailable] {video_id}: <encoding issue in error message>")
        
        # Return -1 values for unavailable videos
        return {
            'channelID': '-1',
            'Views': -1,
            'Published': '-1',
            'likes': -1,
            'comments': -1
        }


def update_csv_with_youtube_stats(csv_path: Path):
    """
    Update a CSV file with YouTube statistics for all videoIDs.
    """
    print(f"\nProcessing: {csv_path.name}")
    
    try:
        # Read CSV
        df = pd.read_csv(csv_path, dtype={'category': str, 'original_title': str})
        
        # Check if videoID column exists
        if 'videoID' not in df.columns:
            print(f"  Skipping (no videoID column)")
            return
        
        # Add new columns if they don't exist
        new_cols = ['channelID', 'Views', 'Published', 'likes', 'comments']
        for col in new_cols:
            if col not in df.columns:
                df[col] = pd.NA
        
        # Determine which videoIDs still need fetching (any stat missing)
        missing_mask = (
            df['videoID'].notna() & (
                df['channelID'].isna() |
                df['Views'].isna() |
                df['Published'].isna() |
                df['likes'].isna() |
                df['comments'].isna()
            )
        )
        unique_videos = df.loc[missing_mask, 'videoID'].dropna().unique()
        total_videos = len(unique_videos)
        
        if total_videos == 0:
            print(f"  No videoIDs to process")
            return
        
        print(f"  Found {total_videos} unique videoIDs")
        print(f"  Fetching stats using yt-dlp with exponential backoff...")
        
        # Fetch stats for each unique videoID
        stats_cache = {}
        successful = 0
        for idx, video_id in enumerate(unique_videos, 1):
            if pd.isna(video_id) or str(video_id).strip() == '':
                continue
            
            video_id = str(video_id).strip()
            
            # Progress indicator
            if idx % 50 == 0 or idx == total_videos:
                print(f"    Progress: {idx}/{total_videos} ({idx/total_videos*100:.1f}%) - Successful: {successful}")
            
            # Fetch stats (with built-in retry logic)
            stats = get_video_stats(video_id)
            if stats:
                stats_cache[video_id] = stats
                successful += 1
            
            # Flush periodically to avoid losing progress
            if idx % SAVE_EVERY == 0 or idx == total_videos:
                if stats_cache:
                    for vid, s in stats_cache.items():
                        mask = df['videoID'] == vid
                        df.loc[mask, 'channelID'] = s['channelID']
                        df.loc[mask, 'Views'] = s['Views']
                        df.loc[mask, 'Published'] = s['Published']
                        df.loc[mask, 'likes'] = s['likes']
                        df.loc[mask, 'comments'] = s['comments']
                    df.to_csv(csv_path, index=False)
                    print(f"    ✓ Saved checkpoint at {idx}/{total_videos} (batch: {len(stats_cache)} videos)")
                    stats_cache.clear()
            
            # Rate limiting (base sleep per request)
            time.sleep(BASE_SLEEP)
        
        print(f"\n  Successfully fetched: {successful}/{total_videos}")
        
        # Final save if anything pending (should be empty)
        if stats_cache:
            for vid, s in stats_cache.items():
                mask = df['videoID'] == vid
                df.loc[mask, 'channelID'] = s['channelID']
                df.loc[mask, 'Views'] = s['Views']
                df.loc[mask, 'Published'] = s['Published']
                df.loc[mask, 'likes'] = s['likes']
                df.loc[mask, 'comments'] = s['comments']
            df.to_csv(csv_path, index=False)
            print(f"  ✓ Saved final checkpoint")
        
        print(f"  ✓ File saved: {csv_path.name}")
        
    except Exception as e:
        print(f"  Error processing file: {e}")


def main():
    """
    Process all CSV files in All_data folder.
    """
    all_data_folder = Path(r"c:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\All_data")
    
    if not all_data_folder.exists():
        print(f"Error: Folder not found: {all_data_folder}")
        return
    
    csv_files = list(all_data_folder.glob("*.csv"))
    
    if not csv_files:
        print("No CSV files found in All_data folder")
        return
    
    print("="*70)
    print(f"Starting batch update for {len(csv_files)} CSV files using yt-dlp")
    print("="*70)
    
    start_time = time.time()
    
    for csv_file in csv_files:
        update_csv_with_youtube_stats(csv_file)
    
    elapsed = time.time() - start_time
    print("\n" + "="*70)
    print(f"Batch update complete! Time elapsed: {elapsed:.1f} seconds")
    print("="*70)


if __name__ == "__main__":
    main()
