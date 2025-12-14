"""
Data Processing and Feature Engineering for Clickbait Detection/Neutralization
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import re
from datetime import datetime

class ClickbaitDataProcessor:
    """Process deArrow data for clickbait detection/neutralization"""
    
    def __init__(self, data_dir='deArrow_data'):
        self.data_dir = Path(data_dir)
        self.titles_df = None
        self.casual_titles_df = None
        self.title_votes_df = None
        self.video_info_df = None
        
    def load_data(self, verbose=True):
        """Load all relevant CSV files"""
        files_to_load = {
            'titles': 'titles.csv',
            'casual_titles': 'casualVoteTitles.csv',
            'title_votes': 'titleVotes.csv',
            'video_info': 'videoInfo.csv'
        }
        
        for key, filename in files_to_load.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                setattr(self, f'{key}_df', pd.read_csv(filepath))
                if verbose:
                    print(f"✓ Loaded {filename}: {len(getattr(self, f'{key}_df'))} rows")
            else:
                print(f"✗ File not found: {filename}")
    
    def extract_text_features(self, text):
        """Extract linguistic features from a title"""
        if pd.isna(text):
            return {}
        
        text_str = str(text).strip()
        
        features = {
            'length': len(text_str),
            'word_count': len(text_str.split()),
            'char_per_word': len(text_str) / max(1, len(text_str.split())),
            'uppercase_ratio': sum(1 for c in text_str if c.isupper()) / max(1, len(text_str)),
            'digit_count': sum(1 for c in text_str if c.isdigit()),
            'exclamation_count': text_str.count('!'),
            'question_count': text_str.count('?'),
            'ellipsis_count': text_str.count('...'),
            'caps_words': sum(1 for w in text_str.split() if w.isupper() and len(w) > 1),
            'has_emoji': bool(re.search(r'[\U0001F300-\U0001F9FF]', text_str)),
            'has_number': bool(re.search(r'\d', text_str)),
            'has_caps_sequence': bool(re.search(r'[A-Z]{3,}', text_str)),
        }
        
        return features
    
    def add_text_features(self, df, text_col='title', prefix=''):
        """Add text feature columns to dataframe"""
        feature_cols = {}
        
        for idx, text in enumerate(df[text_col]):
            features = self.extract_text_features(text)
            for feat_name, feat_val in features.items():
                col_name = f'{prefix}{feat_name}' if prefix else feat_name
                if col_name not in feature_cols:
                    feature_cols[col_name] = []
                feature_cols[col_name].append(feat_val)
        
        for col_name, values in feature_cols.items():
            df[col_name] = values
        
        return df
    
    def create_training_pairs(self, min_video_info_coverage=True):
        """
        Create clickbait → neutral training pairs
        Returns: DataFrame with (clickbait_title, neutral_title, videoID)
        """
        
        if self.titles_df is None or self.casual_titles_df is None:
            print("Error: Load data first")
            return None
        
        # Merge titles with title votes to get clickbait score
        titles_with_votes = self.titles_df.merge(
            self.title_votes_df[['UUID', 'votes']],
            left_on='UUID',
            right_on='UUID',
            how='left'
        )
        
        # Create pairs: original titles with casual alternatives
        pairs = []
        
        for vid in self.casual_titles_df['videoID'].unique():
            # Get the neutral/casual title(s)
            casual = self.casual_titles_df[self.casual_titles_df['videoID'] == vid]
            
            # Get the clickbaity title(s) from titles.csv
            clickbaity = titles_with_votes[titles_with_votes['videoID'] == vid]
            
            if len(casual) > 0 and len(clickbaity) > 0:
                # Get the most upvoted casual title
                neutral_title = casual.iloc[0]['title']
                
                # Get the most voted (highest clicks) clickbaity title
                clickbaity_sorted = clickbaity.sort_values('votes', ascending=False, na_position='last')
                clickbaity_title = clickbaity_sorted.iloc[0]['title']
                
                pairs.append({
                    'videoID': vid,
                    'clickbait_title': clickbaity_title,
                    'neutral_title': neutral_title,
                    'clickbait_votes': clickbaity_sorted.iloc[0].get('votes', 0),
                    'pair_source': 'titles_casual'
                })
        
        pairs_df = pd.DataFrame(pairs)
        
        if min_video_info_coverage and self.video_info_df is not None:
            # Filter to only pairs where we have video info
            video_info_ids = set(self.video_info_df['videoID'].dropna().unique())
            pairs_df = pairs_df[pairs_df['videoID'].isin(video_info_ids)]
        
        return pairs_df
    
    def detect_language(self, text):
        """Simple language detection based on character sets"""
        if pd.isna(text):
            return 'unknown'
        
        text_str = str(text)
        
        # Cyrillic (Russian, etc.)
        if re.search(r'[а-яА-ЯёЁ]', text_str):
            return 'ru'
        # Accented chars (likely romance languages)
        elif re.search(r'[àáâãäåèéêëìíîïòóôõöùúûüñç]', text_str):
            # Check for Spanish patterns
            if re.search(r'¿|¡', text_str):
                return 'es'
            # Check for Italian patterns (common endings)
            elif re.search(r'(ione|ità|ezza)$', text_str):
                return 'it'
            else:
                return 'other_romance'
        # Default to English for ASCII-heavy text
        else:
            return 'en'
    
    def add_language_detection(self, df, text_col='title'):
        """Add language detection to dataframe"""
        df['language'] = df[text_col].apply(self.detect_language)
        return df
    
    def get_summary_stats(self):
        """Print summary statistics about loaded data"""
        print("\n" + "="*80)
        print("DATA SUMMARY STATISTICS")
        print("="*80)
        
        if self.titles_df is not None:
            print(f"\ntitles.csv: {len(self.titles_df)} rows")
            print(f"  - Unique videoIDs: {self.titles_df['videoID'].nunique()}")
            print(f"  - Original (YouTube) titles: {self.titles_df['original'].sum()}")
        
        if self.casual_titles_df is not None:
            print(f"\ncasualVoteTitles.csv: {len(self.casual_titles_df)} rows")
            print(f"  - Unique videoIDs: {self.casual_titles_df['videoID'].nunique()}")
        
        if self.title_votes_df is not None:
            print(f"\ntitleVotes.csv: {len(self.title_votes_df)} rows")
            print(f"  - Avg votes: {self.title_votes_df['votes'].mean():.2f}")
            print(f"  - Positive votes: {(self.title_votes_df['votes'] > 0).sum()}")
            print(f"  - Negative votes: {(self.title_votes_df['votes'] < 0).sum()}")
        
        if self.video_info_df is not None:
            print(f"\nvideoInfo.csv: {len(self.video_info_df)} rows")
            print(f"  - Unique videoIDs: {self.video_info_df['videoID'].nunique()}")


# Example usage
if __name__ == "__main__":
    processor = ClickbaitDataProcessor()
    processor.load_data()
    processor.get_summary_stats()
    
    # Create training pairs
    print("\n" + "="*80)
    print("CREATING TRAINING PAIRS")
    print("="*80)
    pairs = processor.create_training_pairs(min_video_info_coverage=True)
    
    if pairs is not None:
        print(f"\nCreated {len(pairs)} clickbait → neutral training pairs")
        print(f"Sample pairs:")
        for idx, row in pairs.head(3).iterrows():
            print(f"\n  {idx+1}. VideoID: {row['videoID']}")
            print(f"     Clickbait: {row['clickbait_title'][:70]}...")
            print(f"     Neutral:   {row['neutral_title'][:70]}...")
        
        # Add text features
        print(f"\n\nAdding text features to pairs...")
        pairs_with_features = processor.add_text_features(
            pairs.copy(), 
            text_col='clickbait_title',
            prefix='clickbait_'
        )
        pairs_with_features = processor.add_text_features(
            pairs_with_features,
            text_col='neutral_title',
            prefix='neutral_'
        )
        
        print(f"Feature columns added: {[c for c in pairs_with_features.columns if 'clickbait_' in c or 'neutral_' in c]}")
        
        # Add language detection
        pairs_with_features = processor.add_language_detection(
            pairs_with_features,
            text_col='clickbait_title'
        )
        
        print(f"\nLanguage distribution:")
        print(pairs_with_features['language'].value_counts())
        
        # Save processed data
        output_file = 'processed_clickbait_pairs.csv'
        pairs_with_features.to_csv(output_file, index=False)
        print(f"\n✓ Saved {len(pairs_with_features)} pairs to {output_file}")
