from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import pydantic
import python_multipart
import requests

import streamlit as st 
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gemini-chat-414606-505058a474c0.json"
import random
import asyncio
random.seed(42)
from utils.word_functions import (
    load_word_pools, 
    create_audio_file,  
    cleanup_audio_file,
    DEFAULT_CATEGORIES,
    DEFAULT_VOCABULARY_FILE
)

from utils.json_manager import (
    delete_word_from_json,
    load_vocabulary_with_expressions,
    load_vocabulary_from_file,
    load_learned_words,
    save_word_pools_to_file,
    save_learned_words_to_file,
    save_to_learned,
    filter_words_by_category,
    delete_word_from_file,
)
from word_widget import create_word_widget, get_difficulty

# Function to create media directory
def initialize_media_directory():
    """Create media directory in the root directory if it doesn't exist"""
    media_dir = os.path.join(os.path.dirname(__file__), "media")
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
        print(f"Created media directory at: {media_dir}")
    return media_dir

# Initialize media directory
initialize_media_directory()

# Custom CSS to increase base font size by 80% for senior users (30% + 50% additional)
def local_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("css/styles.css")


# Configuration
word_file = DEFAULT_VOCABULARY_FILE
category_list = DEFAULT_CATEGORIES


app = FastAPI()
# Enable CORS so the API can be called from other origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"greetings": "This is a vocabulary learning API"}
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)