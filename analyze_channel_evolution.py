import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Read the data
print("Loading data...")
df = pd.read_csv('All_data/all_in_one.csv')

# Convert timeSubmitted from milliseconds to datetime
df['timeSubmitted'] = pd.to_datetime(df['timeSubmitted'], unit='ms')

# Extract date (without time) for daily aggregation
df['date'] = df['timeSubmitted'].dt.date

# Count submissions per channel per day
print("Analyzing channel submissions over time...")
channel_daily = df.groupby(['date', 'channelID']).size().reset_index(name='submissions')

# Convert date back to datetime for plotting
channel_daily['date'] = pd.to_datetime(channel_daily['date'])

# Get top channels by total submissions for better visualization
top_channels = df['channelID'].value_counts().head(10).index.tolist()

# Create the main visualization
fig, axes = plt.subplots(2, 1, figsize=(16, 12))

# Plot 1: Total submissions over time (all channels combined)
daily_total = df.groupby('date').size().reset_index(name='total_submissions')
daily_total['date'] = pd.to_datetime(daily_total['date'])
daily_total = daily_total.sort_values('date')

axes[0].plot(daily_total['date'], daily_total['total_submissions'], linewidth=2, color='#2E86AB')
axes[0].fill_between(daily_total['date'], daily_total['total_submissions'], alpha=0.3, color='#2E86AB')
axes[0].set_title('Total Submissions Over Time (All Channels)', fontsize=16, fontweight='bold')
axes[0].set_xlabel('Date', fontsize=12)
axes[0].set_ylabel('Number of Submissions', fontsize=12)
axes[0].grid(True, alpha=0.3)
axes[0].tick_params(axis='x', rotation=45)

# Plot 2: Top 10 channels evolution
top_channel_data = channel_daily[channel_daily['channelID'].isin(top_channels)]

# Plot each top channel
for channel in top_channels:
    channel_data = top_channel_data[top_channel_data['channelID'] == channel].sort_values('date')
    axes[1].plot(channel_data['date'], channel_data['submissions'], 
                 label=channel[:16] + '...' if len(str(channel)) > 16 else channel,
                 marker='o', markersize=3, linewidth=1.5, alpha=0.8)

axes[1].set_title('Top 10 Channels: Submissions Evolution Over Time', fontsize=16, fontweight='bold')
axes[1].set_xlabel('Date', fontsize=12)
axes[1].set_ylabel('Number of Submissions', fontsize=12)
axes[1].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
axes[1].grid(True, alpha=0.3)
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('channel_evolution_over_time.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: channel_evolution_over_time.png")

# Create a cumulative view
fig2, ax2 = plt.subplots(figsize=(16, 8))

for channel in top_channels:
    channel_data = top_channel_data[top_channel_data['channelID'] == channel].sort_values('date')
    channel_data['cumulative'] = channel_data['submissions'].cumsum()
    ax2.plot(channel_data['date'], channel_data['cumulative'], 
             label=channel[:16] + '...' if len(str(channel)) > 16 else channel,
             linewidth=2, alpha=0.8)

ax2.set_title('Top 10 Channels: Cumulative Submissions Over Time', fontsize=16, fontweight='bold')
ax2.set_xlabel('Date', fontsize=12)
ax2.set_ylabel('Cumulative Submissions', fontsize=12)
ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('channel_cumulative_submissions.png', dpi=300, bbox_inches='tight')
print("✓ Saved: channel_cumulative_submissions.png")

# Create a heatmap showing channel activity intensity
fig3, ax3 = plt.subplots(figsize=(16, 10))

# Prepare data for heatmap - weekly aggregation for better visualization
channel_daily_copy = channel_daily.copy()
channel_daily_copy['week'] = pd.to_datetime(channel_daily_copy['date']).dt.to_period('W')

top_20_channels = df['channelID'].value_counts().head(20).index.tolist()
weekly_pivot = channel_daily_copy[channel_daily_copy['channelID'].isin(top_20_channels)].groupby(['week', 'channelID'])['submissions'].sum().reset_index()
weekly_pivot['week'] = weekly_pivot['week'].astype(str)

pivot_table = weekly_pivot.pivot(index='channelID', columns='week', values='submissions').fillna(0)

sns.heatmap(pivot_table, cmap='YlOrRd', ax=ax3, cbar_kws={'label': 'Submissions'}, 
            linewidths=0.5, linecolor='white')
ax3.set_title('Top 20 Channels: Weekly Activity Heatmap', fontsize=16, fontweight='bold')
ax3.set_xlabel('Week', fontsize=12)
ax3.set_ylabel('Channel ID', fontsize=12)
ax3.tick_params(axis='x', rotation=90, labelsize=8)
ax3.tick_params(axis='y', labelsize=8)

plt.tight_layout()
plt.savefig('channel_activity_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ Saved: channel_activity_heatmap.png")

# Print summary statistics
print("\n" + "="*60)
print("CHANNEL EVOLUTION SUMMARY")
print("="*60)
print(f"\nTotal unique channels: {df['channelID'].nunique():,}")
print(f"Total submissions: {len(df):,}")
print(f"Date range: {df['timeSubmitted'].min().date()} to {df['timeSubmitted'].max().date()}")
print(f"Duration: {(df['timeSubmitted'].max() - df['timeSubmitted'].min()).days} days")

print("\n\nTop 10 Most Active Channels:")
print("-" * 60)
top_channel_stats = df['channelID'].value_counts().head(10)
for idx, (channel, count) in enumerate(top_channel_stats.items(), 1):
    print(f"{idx:2d}. {channel}: {count:,} submissions")

print("\n\nDaily Statistics:")
print("-" * 60)
print(f"Average submissions per day: {daily_total['total_submissions'].mean():.1f}")
print(f"Max submissions in a day: {daily_total['total_submissions'].max():,}")
print(f"Peak day: {daily_total.loc[daily_total['total_submissions'].idxmax(), 'date']}")

print("\n" + "="*60)
print("Analysis complete! Check the generated PNG files.")
print("="*60)

plt.show()
