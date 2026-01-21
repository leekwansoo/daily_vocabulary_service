#select_words.py...

from unicodedata import category
import streamlit as st 
import random
import os
import json
import asyncio


from utils.word_functions import (
    load_word_pools, 
    create_audio_file, 
    cleanup_audio_file,
    DEFAULT_CATEGORIES,
    DEFAULT_VOCABULARY_FILE,
    DIFFICULTY_LEVELS,
    LEVEL_DESCRIPTIONS,
    SPEED_OPTIONS,
    SPEED_LABELS
)

from utils.json_manager import (
    delete_word_from_json,
    load_vocabulary_with_expressions,
    load_vocabulary_from_file,
    load_learned_words,
    save_word_pools_to_file,
    save_learned_words_to_file,
    save_to_learned,
    save_to_mailed,
    save_mailed_words_to_file,
    load_mailed_words,
    get_category_statistics,
    filter_words_by_category,
    delete_word_from_file,
)
from word_widget import create_word_widget, get_difficulty

from database.subscriber_db import (
    add_subscriber,
    delete_subscriber,
    list_subscribers,
    update_subscriber,
    Subscriber,
)

# Functions for persistent storage of sequence number
def load_seq_no():
    """Load starting sequence number from file"""
    try:
        with open('seq_state.json', 'r') as f:
            data = json.load(f)
            return data.get('starting_seq_no', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_seq_no(seq_no):
    """Save starting sequence number to file"""
    try:
        with open('seq_state.json', 'w') as f:
            json.dump({'starting_seq_no': seq_no}, f)
    except Exception as e:
        print(f"Error saving seq_no: {e}")


word_file = DEFAULT_VOCABULARY_FILE
category_list = DEFAULT_CATEGORIES
    
def display_vocabulary(vocab_file):
    with open(vocab_file, 'r', encoding='utf-8') as f:
        vocab = json.load(f) 
        
        
def select_words_from_vocabulary(number_of_words, selection_method, current_level, seq_no=0):
    # for random selection method you can skip or set 0 the seq_no parameter
    all_words = load_vocabulary_with_expressions(current_level)
    print(f"Total words available for selection: {len(all_words)}")
    
    if selection_method == "random":
        selected_words = random.sample(all_words, min(number_of_words, len(all_words)))
    elif selection_method == "sequential":
        selected_words = all_words[seq_no:seq_no + number_of_words]
    else:
        selected_words = []
    
    return selected_words


def display_selected_words(selected_words):
    for entry in selected_words:
        with st.container():
            word = entry.get('word')
            difficulty = get_difficulty(entry['word'])
            # Render the word card with editable expressions
            create_word_widget(entry, editable_expressions=True, current_level=current_level)
    return
                
def save_selected_words(selected_words):
    for entry in selected_words:
        # Save selected words to mailed.json and learned.json
        save_to_mailed(entry)   
    
    print(f"Saved {len(selected_words)} words to mailed.json")
    return {'status': 'saved'}

if 'starting_seq_no' not in st.session_state:
    st.session_state.starting_seq_no = load_seq_no()  # Load from persistent storage               
st.title("✉️ Vocabulary Mailer")
st.header("Select words for email")
st.sidebar.title("Words Selection Settings")
current_level =st.sidebar.radio("Select Library", ["level1", "level2", "level3"], horizontal=True)
# Convert level string to integer
level_map = {"level1": 1, "level2": 2, "level3": 3}
if current_level in level_map:
    current_level = level_map[current_level]
file_path = f"{current_level}.json"
st.info(f"🎯 **Current Level: {current_level}** ")
number_of_words = st.sidebar.number_input("Number of words to mail", min_value=1, max_value=10, value=3, step=1)
selected_method = st.sidebar.radio("Selection Method", ["random", "sequential"])
if selected_method == "sequential":
    seq_no = st.session_state.starting_seq_no + number_of_words
    if seq_no >= len(load_vocabulary_with_expressions(current_level)):
        # reset to 0 if exceeds available words
        st.session_state.starting_seq_no = 0
        seq_no = st.session_state.starting_seq_no
    else:
        st.session_state.starting_seq_no = seq_no
    # Save to persistent storage
    save_seq_no(st.session_state.starting_seq_no)
    print(f"Updated seq_no: {seq_no}")
    
else:
    seq_no = 0 # not used for random selection
 
if st.sidebar.button("Select Words for Email"):
    selected_words = select_words_from_vocabulary(number_of_words, selected_method, current_level, seq_no = seq_no)
    st.success(f"✅ Selected {len(selected_words)} words for email!")
    # Store selected words in session state so they persist
    st.session_state.selected_words = selected_words
    display_selected_words(selected_words)

# Show save button if words are selected (using session state)
if hasattr(st.session_state, 'selected_words') and st.session_state.selected_words:
    if st.button("Save Selected Words to Mailed List"):
        print("Saving selected words to mailed.json...")
        selected_words = st.session_state.selected_words
        result = save_selected_words(selected_words)
        print(result)
        if result:
            st.success(f"✅ Saved {len(selected_words)} words to mailed.json")
            # Clear selected words after saving
            st.session_state.selected_words = []
        else:
            st.error("❌ Failed to save selected words.")
        
        # Load word pools from level-specific JSON file
                    

                    
        
