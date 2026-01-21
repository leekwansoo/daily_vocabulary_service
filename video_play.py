# ...existing code...
import os
import sys
import subprocess
import webbrowser
import json
from pathlib import Path
import streamlit as st 
# from gtts import gTTS
# import pyttsx3
import random 
random_num = random.randint(1, 100)
from utils.word_functions import DIFFICULTY_LEVELS
# ...existing code...

# Try to use user's videoplay helper if present

external_play_video = None

    
def display_photo(path):
    """Display local image file or image from URL in Streamlit."""
    try:
        # If it's a local path
        if not str(path).startswith(("http://", "https://")):
            p = Path(path)
            if not p.is_absolute():
                p = (Path(__file__).parent / p).resolve()
                print(f"Resolved image path: {p}")
            if p.exists():
                st.image(str(p))
            else:
                st.error(f"Image file not found: {p}")
        else:
            # It's a URL
            st.image(path)
    except Exception as e:
        st.error(f"Failed to display image: {e}")
        
def play_video(path_or_url):
    """Open local file in external player or open a URL in the browser.
    Prefers the external helper if provided (videoplay.play_video)."""
    try:
        # If it's a local path
        if not str(path_or_url).startswith(("http://", "https://")):
            p = Path(path_or_url)
            if not p.is_absolute():
                p = (Path(__file__).parent / p).resolve()
            if p.exists():
                if external_play_video:
                    try:
                        external_play_video(str(p))
                        return
                    except Exception:
                        pass
                # Fallback to platform open
                if sys.platform.startswith("win"):
                    os.startfile(str(p))
                elif sys.platform.startswith("darwin"):
                    subprocess.Popen(["open", str(p)])
                else:
                    subprocess.Popen(["xdg-open", str(p)])
                return
            else:
                # Not found as a file; treat as URL below
                path_or_url = str(path_or_url)
        # It's a URL or local file was not found — open in browser
        webbrowser.open_new_tab(path_or_url)
    except Exception as e:
        st.error(f"Failed to open video: {e}")

def _drive_direct_link(url: str) -> str | None:
    """Try to convert common Google Drive share URLs to a direct-download link Streamlit can play."""
    import re
    # /d/FILEID/...
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    # id=FILEID
    m = re.search(r"id=([a-zA-Z0-9_-]+)", url)
    if m:
        return f"https://drive.google.com/uc?export=download&id={m.group(1)}"
    return None

def _drive_embed_link(url: str) -> str | None:
    """Convert Google Drive share URLs to embeddable iframe link."""
    import re
    # /d/FILEID/...
    m = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if m:
        return f"https://drive.google.com/file/d/{m.group(1)}/preview"
    # id=FILEID
    m = re.search(r"id=([a-zA-Z0-9_-]+)", url)
    if m:
        return f"https://drive.google.com/file/d/{m.group(1)}/preview"
    return None

def _detect_media_type(path_or_url: str) -> str:
    """Detect if the media is an image, video, or unknown type."""
    # Common extensions
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    video_exts = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'}
    audio_exts = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}
    
    # Get extension from path/URL
    ext = Path(path_or_url).suffix.lower()
    
    # Check query parameters for URLs (e.g., ?format=mp4)
    if '?' in str(path_or_url):
        import re
        format_match = re.search(r'[?&]format=([^&]+)', str(path_or_url))
        if format_match:
            ext = f".{format_match.group(1).lower()}"
    
    if ext in image_exts:
        return 'image'
    elif ext in video_exts:
        return 'video'
    elif ext in audio_exts:
        return 'audio'
    else:
        # Default to video for unknown types with URLs
        if str(path_or_url).startswith(('http://', 'https://')):
            return 'win_browser'  # Assume online content
        return 'unknown'



# ...existing code...
# Ensure the left column uses create_word_widget(entry) (if not already)

