"""
Batch update all_in_one.csv with YouTube video statistics using yt-dlp.
Uses stealth techniques to avoid bot detection:
- Slow, randomized rate limiting
- Browser cookies for authentication
- User agent rotation
- Proper checkpointing and resume capability
"""

import os
import sys
import pandas as pd
import time
import random
from pathlib import Path
from typing import Dict, Optional
import yt_dlp

# Ensure UTF-8 output handling
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Stealth Configuration
MIN_SLEEP = 2.0  # Minimum delay between requests (seconds)
MAX_SLEEP = 5.0  # Maximum delay between requests (seconds)
SAVE_EVERY = 100  # Save checkpoint every N successful fetches
MAX_RETRIES = 2  # Retries per video on transient errors

# Browser cookie options (uncomment one if you want to use browser cookies)
# BROWSER = 'chrome'  # or 'firefox', 'edge', 'safari', 'opera'
BROWSER = None  # Disabled due to DPAPI decryption errors


def get_random_user_agent():
    """Return a random user agent to avoid detection."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    return random.choice(user_agents)


def get_video_stats(video_id: str, retry_count: int = 0) -> Optional[Dict]:
    """
    Fetch statistics for a YouTube video using yt-dlp with stealth mode.
    
    Args:
        video_id: YouTube video ID
        retry_count: Current retry attempt
    
    Returns:
        Dictionary with video statistics or None if fails
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'socket_timeout': 15,
            'extract_flat': False,
            'user_agent': get_random_user_agent(),
            # Add more realistic headers
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        
        # Use browser cookies if specified
        if BROWSER:
            ydl_opts['cookiesfrombrowser'] = (BROWSER,)
        
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
        
    except Exception as e:
        error_msg = str(e)
        
        # Check if it's a bot detection error
        if 'bot' in error_msg.lower() or 'captcha' in error_msg.lower():
            print(f"  [Bot Detected] {video_id} - Increase delays or use browser cookies")
            return None
        
        # Retry on transient errors
        if retry_count < MAX_RETRIES and any(keyword in error_msg.lower() for keyword in ['timeout', 'connection', 'network']):
            wait = random.uniform(3, 8)
            print(f"  [Retry {retry_count+1}/{MAX_RETRIES}] {video_id}: waiting {wait:.1f}s...")
            time.sleep(wait)
            return get_video_stats(video_id, retry_count=retry_count + 1)
        
        # Skip on all other errors
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        try:
            print(f"  [Skip] {video_id}: {error_msg}")
        except:
            print(f"  [Skip] {video_id}: <encoding error>")
        return None


def update_all_in_one_stealth():
    """
    Update all_in_one.csv with YouTube statistics using stealth mode.
    Resumes from last checkpoint automatically.
    """
    csv_path = Path(r"c:\Users\Sahar\Desktop\Clickbait_git\Clickbait-project\All_data\all_in_one.csv")
    
    print("="*70)
    print("Updating all_in_one.csv with yt-dlp (Stealth Mode)")
    print("="*70)
    print(f"Rate limiting: {MIN_SLEEP}-{MAX_SLEEP} seconds between requests")
    print(f"Browser cookies: {'Yes (' + BROWSER + ')' if BROWSER else 'No'}")
    print(f"Save frequency: Every {SAVE_EVERY} successful fetches")
    print("="*70)
    
    if not BROWSER:
        print("\n⚠️  TIP: If you get bot detection, set BROWSER='chrome' in the script")
        print("   This will use your browser's cookies for authentication\n")
    
    try:
        # Read CSV
        print("\nReading CSV file...")
        df = pd.read_csv(csv_path, dtype={'category': str, 'original_title': str}, low_memory=False)
        print(f"Total rows: {len(df):,}")
        
        # Add new columns if they don't exist
        new_cols = ['channelID', 'Views', 'Published', 'likes', 'comments']
        for col in new_cols:
            if col not in df.columns:
                df[col] = pd.NA
        
        # Determine which videoIDs still need fetching
        missing_mask = (
            df['videoID'].notna() & (
                df['channelID'].isna() |
                df['Views'].isna() |
                df['Published'].isna() |
                df['likes'].isna() |
                df['comments'].isna()
            )
        )
        unique_videos = df.loc[missing_mask, 'videoID'].dropna().unique().tolist()
        total_videos = len(unique_videos)
        
        if total_videos == 0:
            print("\n✓ All videos already have statistics!")
            return
        
        print(f"\nFound {total_videos:,} unique videoIDs needing stats")
        
        # Estimate time
        avg_delay = (MIN_SLEEP + MAX_SLEEP) / 2
        estimated_hours = (total_videos * avg_delay) / 3600
        print(f"Estimated time: {estimated_hours:.1f} hours ({estimated_hours/24:.1f} days)")
        print(f"\nStarting in 3 seconds...\n")
        time.sleep(3)
        
        # Process videos one by one
        successful = 0
        failed = 0
        start_time = time.time()
        last_save_count = 0
        
        for idx, video_id in enumerate(unique_videos, 1):
            if pd.isna(video_id) or str(video_id).strip() == '':
                continue
            
            video_id = str(video_id).strip()
            
            # Fetch stats
            stats = get_video_stats(video_id)
            
            if stats:
                # Update all rows with this videoID
                mask = df['videoID'] == video_id
                df.loc[mask, 'channelID'] = stats['channelID']
                df.loc[mask, 'Views'] = stats['Views']
                df.loc[mask, 'Published'] = stats['Published']
                df.loc[mask, 'likes'] = stats['likes']
                df.loc[mask, 'comments'] = stats['comments']
                successful += 1
            else:
                failed += 1
            
            # Progress update every 10 videos
            if idx % 10 == 0 or idx == total_videos:
                elapsed = time.time() - start_time
                rate = successful / elapsed if elapsed > 0 else 0
                remaining = total_videos - idx
                eta_seconds = remaining / rate if rate > 0 else 0
                eta_hours = eta_seconds / 3600
                
                print(f"[{idx:,}/{total_videos:,}] Success: {successful:,} | Failed: {failed} | "
                      f"Rate: {rate*3600:.0f}/hr | ETA: {eta_hours:.1f}h")
            
            # Save checkpoint periodically based on successful fetches
            if successful - last_save_count >= SAVE_EVERY or idx == total_videos:
                df.to_csv(csv_path, index=False)
                print(f"  ✓ Checkpoint saved ({successful:,} successful fetches)")
                last_save_count = successful
            
            # Randomized delay to avoid detection (skip on last iteration)
            if idx < total_videos:
                delay = random.uniform(MIN_SLEEP, MAX_SLEEP)
                time.sleep(delay)
        
        # Final save
        df.to_csv(csv_path, index=False)
        
        elapsed = time.time() - start_time
        print("\n" + "="*70)
        print(f"✓ Update complete!")
        print(f"  Successfully fetched: {successful:,}/{total_videos:,}")
        print(f"  Failed: {failed}")
        print(f"  Time elapsed: {elapsed/3600:.2f} hours")
        print(f"  Average rate: {successful/elapsed*3600:.0f} videos/hour")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user - saving checkpoint...")
        df.to_csv(csv_path, index=False)
        print(f"✓ Progress saved: {successful:,} videos fetched")
        print("You can resume by running this script again")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    update_all_in_one_stealth()
