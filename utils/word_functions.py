"""
Main utility functions for vocabulary builder applications
Contains reusable functions that can be used across different apps
"""

# import pyttsx3
# from gtts import gTTS
import io
import tempfile
import os
import json
import re
import random
import asyncio
random.seed(42)


def load_word_pools(level=1):
    """
    Load word pools from a level-specific JSON file
    
    Args:
        level (int): Difficulty level (1, 2, or 3)
        
    Returns:
        dict: Dictionary containing word pools for each category
    """
    json_file = f"level{level}.json"
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            word_pools = json.load(f)
            #print(f"Loaded {len(word_pools)} categories from {json_file}")
            return word_pools
    except FileNotFoundError:
        # print(f"Error: {json_file} not found")
        # Fallback to word_pools.json if level file doesn't exist
        try:
            with open("word_pools.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            #   print("Error: No vocabulary files found")
            return {}
    except json.JSONDecodeError:
        # print(f"Error: Invalid JSON format in {json_file}")
        return {}

def detect_language(text):
    # Check for Korean characters (Hangul)
    if re.search(r'[가-힣]', text):
        return 'ko'
    # Check for Chinese characters  
    elif re.search(r'[一-龯]', text):
        return 'zh'
    # Check for Japanese characters
    elif re.search(r'[ひらがなカタカナ一-龯ぁ-ゖァ-ヺ]', text):
        return 'ja'
    # Default to English
    else:
        return 'en'

async def create_audio_file(text, filename, is_phrase=False, speed="normal"):
    """
    Create audio file for text-to-speech with American English voice (cloud-compatible)
    
    Args:
        text (str): Text to convert to speech
        filename (str): Name for the temporary audio file
        is_phrase (bool): Whether the text is a phrase (affects speech rate)
        speed (str): Speed setting - "normal", "0.9", or "0.8"
        
    Returns:
        str or None: Path to the created audio file, or None if failed
    """
    # Detect language first
    detected_language = detect_language(text)
    
    # Only use pyttsx3 for English text, use gTTS for other languages
    if detected_language == 'en':
        # Try pyttsx3 first (for local development with English)
        try:
            # Run pyttsx3 in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _create_with_pyttsx3():
                engine = pyttsx3.init()
                
                # Get available voices
                voices = engine.getProperty('voices')
                
                # Try to find an American English voice
                american_voice = None
                for voice in voices:
                    # Look for American English voices (common identifiers)
                    if voice.id and any(identifier in voice.id.lower() for identifier in ['david', 'mark', 'zira', 'hazel', 'us', 'american', 'en-us']):
                        american_voice = voice.id
                        break
                    # Fallback: look for any English voice
                    elif voice.id and 'en' in voice.id.lower():
                        american_voice = voice.id
                
                # Set the American English voice if found
                if american_voice:
                    engine.setProperty('voice', american_voice)
                
                # Base speech rates
                base_word_rate = 160
                base_phrase_rate = 140
                
                # Apply speed multiplier
                speed_multipliers = {
                    "normal": 1.0,
                    "0.9": 0.9,
                    "0.8": 0.8
                }
                
                multiplier = speed_multipliers.get(speed, 1.0)
                
                # Adjust settings for phrases vs single words with speed options
                if is_phrase:
                    final_rate = int(base_phrase_rate * multiplier)
                else:
                    final_rate = int(base_word_rate * multiplier)
                
                engine.setProperty('rate', final_rate)
                engine.setProperty('volume', 0.9)
                
                # Create temporary file path
                temp_file = os.path.join(tempfile.gettempdir(), f"{filename}.wav")
                engine.save_to_file(text, temp_file)
                engine.runAndWait()
                return temp_file
            
            return await loop.run_in_executor(None, _create_with_pyttsx3)
            
        except Exception as e:
            print(f"pyttsx3 failed ({e}), trying gTTS for cloud compatibility...")
    
    # Use gTTS for non-English languages or if pyttsx3 failed
    try:
        # Run gTTS in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _create_with_gtts():
            # Adjust speed for gTTS (it only has slow/normal)
            use_slow_speech = speed in ["1.0", "0.9"] or is_phrase
            
            # Create TTS object
            tts = gTTS(text=text, lang=detected_language, slow=use_slow_speech)
            print(f"Detected language: {detected_language} for text: '{text}'")
            # Create temporary file path (MP3 format for gTTS)
            temp_file = os.path.join(tempfile.gettempdir(), f"{filename}.mp3")
            tts.save(temp_file)
            
            print(f"Created audio file using gTTS: {temp_file}")
            return temp_file
        
        return await loop.run_in_executor(None, _create_with_gtts)
        
    except Exception as e2:
        print(f"gTTS failed: {e2}")
        return None


def cleanup_audio_file(file_path):
    """
    Clean up temporary audio file
    
    Args:
        file_path (str): Path to the audio file to delete
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not delete temporary file {file_path}: {e}")

def generate_quiz_question(words, correct_word):
    """Generate a multiple choice quiz question"""
    options = [correct_word]
    other_words = [w for w in words if w['word'] != correct_word['word']]
    
    # Add 3 random wrong options
    wrong_options = random.sample(other_words, min(3, len(other_words)))
    for word in wrong_options:
        options.append(word)
    
    random.shuffle(options)
    return options

# Constants
DEFAULT_CATEGORIES = ["General", "Science", "Business", "Literature", "Travel", "History", "Geography", "Health"]
DEFAULT_VOCABULARY_FILE = "vocabulary.txt"
DEFAULT_WORD_POOLS_FILE = "word_pools.json"
DIFFICULTY_LEVELS = [1, 2, 3]
LEVEL_DESCRIPTIONS = {
    1: "Beginner - Basic vocabulary with common everyday words",
    2: "Intermediate - More challenging words for advancing learners", 
    3: "Advanced - Sophisticated vocabulary for expert learners"
}
SPEED_OPTIONS = ["normal", "0.9", "0.8"]
SPEED_LABELS = {
    "normal": "Normal (100%)",
    "0.9": "Slower (90%)",
    "0.8": "Slowest (80%)"
}

