import asyncio
import streamlit as st 
import os 
import sys
import subprocess
import webbrowser
import json
from pathlib import Path
from gtts import gTTS
import pyttsx3
from utils.word_functions import create_audio_file
# Try to use user's videoplay helper if present
external_play_video = None

def load_subscribers_from_json(filename):
    """Load subscribers data from a JSON file.
    
    Args:
        filename (str): Path to the JSON file.
    
    Returns:
        dict: Loaded subscribers data.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

import re
import json


async def generate_audio():
        audio_file = await create_audio_file(input_text, "temp_audio.mp3")
        if audio_file:
            st.success("Audio file created successfully!")
            return audio_file
        else:
            st.error("Failed to create audio file.")
            return None
st.title("Audio Handler Module")
st.write("This module handles text-to-speech audio generation for multiple languages.")
input_text = st.text_area("Enter text for TTS:", "Hello, world!")
if st.button("Generate Audio"):
    audio_file = asyncio.run(generate_audio())
    if audio_file:
        st.audio(audio_file, format="audio/mp3")
