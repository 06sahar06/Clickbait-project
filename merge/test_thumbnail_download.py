import re
import requests

def get_thumbnail(video_id, quality='maxresdefault.jpg'):
    return f'https://img.youtube.com/vi/{video_id}/{quality}'

url = 'https://www.youtube.com/watch?v=B5Y7z8PoXkM'  # From casualVoteTitles.csv
video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url).group(1)
thumb_url = get_thumbnail(video_id)
print(f"Video ID: {video_id}")
print(f"Thumbnail URL: {thumb_url}")

img_data = requests.get(thumb_url).content
print(f"Downloaded {len(img_data)} bytes")

output_file = f'{video_id}_thumb.jpg'
with open(output_file, 'wb') as f:
    f.write(img_data)

print(f"✓ Saved thumbnail to {output_file}")

# Check if the file was created
import os
if os.path.exists(output_file):
    file_size = os.path.getsize(output_file)
    print(f"✓ File exists: {file_size} bytes")
    
    # Try to verify it's a valid image
    try:
        from PIL import Image
        img = Image.open(output_file)
        print(f"✓ Valid image: {img.size[0]}x{img.size[1]} pixels, format: {img.format}")
    except ImportError:
        print("  (PIL not installed, cannot verify image)")
    except Exception as e:
        print(f"✗ Error opening image: {e}")
else:
    print("✗ File was not created")
