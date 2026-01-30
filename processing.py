import os
import glob
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
import math

DOWNLOAD_DIR = "downloads"
PROCESSED_DIR = "processed"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def download_video(url: str) -> str:
    """Downloads a video from YouTube and returns the file path."""
    options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'noplaylist': True,
    }
    with YoutubeDL(options) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_id = info_dict.get('id', None)
        # Find the downloaded file
        files = glob.glob(os.path.join(DOWNLOAD_DIR, f"{video_id}.*"))
        if files:
            return files[0]
        else:
            raise Exception("Download failed: File not found")

def crop_to_vertical(clip):
    """Crops a horizontal video to 9:16 vertical format (center crop)."""
    w, h = clip.size
    target_ratio = 9 / 16
    current_ratio = w / h

    if current_ratio > target_ratio:
        # Too wide, crop width
        new_w = h * target_ratio
        x1 = (w - new_w) / 2
        crop_clip = clip.crop(x1=x1, y1=0, width=new_w, height=h)
    else:
        # Too tall (unlikely for YT), crop height or keep as is
        # If it's already vertical or square, we might just leave it or crop height
        new_h = w / target_ratio
        y1 = (h - new_h) / 2
        crop_clip = clip.crop(x1=0, y1=y1, width=w, height=new_h)
        
    return crop_clip

def process_video(file_path: str):
    """Splits video into 3 vertical shorts."""
    try:
        clip = VideoFileClip(file_path)
        duration = clip.duration
        
        # Define 3 segments
        # 1. Start (skip first 10s if possible, else 0)
        # 2. 1/3 mark
        # 3. 2/3 mark
        
        segment_length = 60 # seconds
        if duration < segment_length:
             # If video is too short, just return one processed clip of the whole thing
             starts = [0]
        elif duration < segment_length * 3:
             # Overlapping or spaced out as much as possible
             starts = [0, duration/2 - segment_length/2]
        else:
             starts = [
                 10 if duration > 70 else 0, 
                 duration * 0.33, 
                 duration * 0.66
             ]

        generated_files = []
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        for i, start_time in enumerate(starts):
            end_time = min(start_time + segment_length, duration)
            if start_time >= end_time:
                continue
                
            subclip = clip.subclip(start_time, end_time)
            vertical_clip = crop_to_vertical(subclip)
            
            # Optimization: Resize if very huge (optional, for speed)
            # vertical_clip = vertical_clip.resize(height=1280) 
            
            output_filename = f"{base_name}_part{i+1}.mp4"
            output_path = os.path.join(PROCESSED_DIR, output_filename)
            
            vertical_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                threads=4,
                preset="ultrafast" # Faster encoding
            )
            generated_files.append(output_filename)
        
        clip.close()
        return generated_files

    except Exception as e:
        print(f"Error processing video: {e}")
        if 'clip' in locals():
            clip.close()
        raise e
