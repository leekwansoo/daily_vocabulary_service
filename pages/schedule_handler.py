"""
schedule_handler.py

Scheduling:
  - Windows: create a Task Scheduler task to run this script daily at 23:59
  - Linux/macOS: add a cron job to run daily at 23:59

Notes:
  - The script expects `mailed.json` to be in the current working directory or in the project root.
  - SMTP credentials may require app-specific passwords for providers like Gmail.
"""
import streamlit as st 
import random
import os
import json
import argparse
import smtplib
import asyncio
from email.message import EmailMessage
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

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

# Try to import keyring for secure credential storage; optional
from utils.json_manager import load_mailed_words
from word_widget import create_word_widget, get_difficulty
from utils.subscriber_handler import display_subscriber, edit_subscriber
from mailer import mail_trigger

from database.subscriber_db import (
    add_subscriber,
    delete_subscriber,
    list_subscribers,
    update_subscriber,
    Subscriber,
)
def display_vocabulary(vocab_file):
    with open(vocab_file, 'r', encoding='utf-8') as f:
        vocab = json.load(f) 
        
st.title("✉️ Vocabulary Mailer")
st.header("Send selected words via email")
st.sidebar.title("Mailer Settings")
selected = st.sidebar.radio("Select an option", ["Subscriber_List", "Select Vocabulary", "Mail Words"])
if selected == "Subscriber_List":
    st.write("This section would manage the subscriber list.")
    selected = st.radio("Select Action", ["View Subscribers", "Add Subscriber"], horizontal=True)
    if selected == "View Subscribers":
        subscribers = list_subscribers()
        display_subscriber(subscribers)
    elif selected == "Add Subscriber":
        result = edit_subscriber()
        if result:
            st.success(f"Added subscriber: {result['name']} ({result['email']})")
        
elif selected == "Select Vocabulary":
    current_level =st.radio("Select Library", ["level1", "level2", "level3", "learned", "mailed"], horizontal=True)
    file_path = f"{current_level}.json"
    st.sidebar.markdown("### Audio Settings")
    selected_speed = st.sidebar.radio("Select Audio Speed", SPEED_OPTIONS, format_func=lambda x: SPEED_LABELS.get(x, x))
    st.info(f"🎯 **Current Level: {current_level}** ")
    word_file = DEFAULT_VOCABULARY_FILE
    category_list = DEFAULT_CATEGORIES
    if current_level in ["mailed", "learned"]:
        if current_level == "mailed":
            words = load_mailed_words()
            print(words)
            # word_file = "mailed.json"
        else:
            words = load_learned_words()
            print(words)
            # word_file = "learned.json"
        if words:
            # Convert learned words to the standard vocabulary format and save to the working file
            with open(word_file, "w", encoding='utf-8') as f:
                for word_entry in words:
                    f.write(f"{word_entry['word']} | {word_entry['meaning']} | {word_entry['phrase']} | {word_entry.get('category', 'General')}\n")
            st.success(f"✅ Successfully loaded {len(words)} {current_level} words!")
            # st.info("Navigate to other sections to review your learned vocabulary.")
        else:
            st.warning(f"❌ No {current_level} words found")
        
    elif current_level in ["level1", "level2", "level3"]:
        if current_level =="level1":
            current_level =1
        elif current_level =="level2":
            current_level =2
        elif current_level =="level3":
            current_level =3  
                 
    word_pools = load_word_pools(current_level)
    #   print(f"level: {level}\n  length of word_pools: {len(word_pools)}")
    if word_pools:
        success = save_word_pools_to_file(word_pools, word_file)    
        if success:
            # Convert learned words to the standard vocabulary format and save to the working file
            with open(word_file, "w", encoding='utf-8') as f:
                for category, words in word_pools.items():
                    for word_entry in words:
                        # print(word_entry)
                        f.write(f"{word_entry['word']} | {word_entry['meaning']} | {word_entry['phrase']} | {category}\n")   
        st.success(f"✅ Successfully loaded {len(word_pools)}words from level_{current_level}!")
        
        # Display the loaded words in the Streamlit app
        all_words = load_vocabulary_with_expressions(current_level)
        print(f"Number of words loaded for display: {len(all_words)}")
        
        for entry in all_words:
            with st.container():
                col1, col2 = st.columns([4, 1])
                category = entry.get('category', category)
                with col1:
                    difficulty = get_difficulty(entry['word'])
                    # Render the word card with editable expressions
                    create_word_widget(entry, editable_expressions=True, current_level=current_level)

                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Play buttons
                    random_num = random.randint(0, 300)
                    random_num = random.randint(0, random_num)
                    if st.button(f"🔊 Word", key=f"word_{entry['word']}_{random_num}"):
                        audio_file = asyncio.run(create_audio_file(entry['word'], f"word_{entry['word']}", is_phrase=False, speed=selected_speed))
                        print(f"Generated audio file for word: {audio_file}")
                        if audio_file and os.path.exists(audio_file):
                            with open(audio_file, 'rb') as audio:
                                # Detect audio format based on file extension
                                audio_format = 'audio/mp3' if audio_file.endswith('.mp3') else 'audio/wav'
                                st.audio(audio.read(), format=audio_format)
                            cleanup_audio_file(audio_file)
                        else:
                            st.error("Audio generation failed")
                    random_num = random.randint(0, 300)
                    if entry['phrase'] and st.button(f"🔊 Phrase", key=f"phrase_{entry['word']}_{random_num}"):
                        audio_file = asyncio.run(create_audio_file(entry['phrase'], f"phrase_{entry['word']}", is_phrase=True, speed=selected_speed))
                        if audio_file and os.path.exists(audio_file):
                            with open(audio_file, 'rb') as audio:
                                # Detect audio format based on file extension
                                audio_format = 'audio/mp3' if audio_file.endswith('.mp3') else 'audio/wav'
                                st.audio(audio.read(), format=audio_format)
                            cleanup_audio_file(audio_file)
                        else:
                            st.error("Audio generation failed")
                    
                    # Action buttons
                    st.markdown("<br>", unsafe_allow_html=True)
                                            
                    # Different buttons based on current level
                    if current_level in ["mailed","learned"]:
                        # Move back to vocabulary button for learned words
                        if st.button(f"↩️ Move Back", key=f"moveback_{entry['word']}", help="Move back to main vocabulary"):
                            # Add word back to main vocabulary file
                            with open(word_file, "a", encoding='utf-8') as f:
                                f.write(f"{entry['word']} | {entry['meaning']} | {entry['phrase']} | {entry['category']}\n")
                            if current_level == "mailed":
                                # Remove from mailed.json
                                mailed_words = load_mailed_words()
                                updated_mailed = [w for w in mailed_words if w['word'].lower() != entry['word'].lower()]
                                save_mailed_words_to_file(updated_mailed)
                            # Remove from learned.json
                            learned_words = load_learned_words()
                            updated_learned = [w for w in learned_words if w['word'].lower() != entry['word'].lower()]
                            save_learned_words_to_file(updated_learned)
                            
                            st.success(f"'{entry['word']}' moved back to main vocabulary!")
                            st.rerun()  # Refresh the page to update the list
                    else:
                        # Learned button for regular levels
                        print(f"current level: {current_level}")
                        if current_level in [1, 2, 3]:
                            word_file = "level" + str(current_level) + ".json"
                            random_num = random.randint(0, 300)
                            if st.button(f"✅ Learned", key=f"learned_{entry['word']}_{random_num}", help="Move to learned words"):
                                success = save_to_learned(entry)
                                if success:
                                    delete_word_from_file(entry['word'], word_file)
                                    st.success(f"'{entry['word']}' moved to learned words!")
                                    st.rerun()  # Refresh the page to update the list
                                    
                            # Show 'Mailed' disabled button only if word already copied; otherwise allow copying
                            mailed_words = load_mailed_words()
                            mailed_names = [w['word'].lower() for w in mailed_words] if mailed_words else []
                            if entry['word'].lower() in mailed_names:
                                st.button("Mailed", key=f"mailed_{entry['word']}_{random_num}", help="Already mailed", disabled=True)
                            else:
                                if st.button("Move to Mail", key=f"mailed_{entry['word']}_{random_num}", help="Move to mailed words"):
                                    success = save_to_mailed(entry)
                                    if success:
                                        st.success(f"'{entry['word']}' copied to mailed words!")
                                        st.rerun()

                    st.markdown("<br>", unsafe_allow_html=True)
                    if current_level == 1 or current_level == 2 or current_level ==3:
                            word_file = "level" + str(current_level) + ".json"
                    random_num = random.randint(0, 300)
                    if st.button("Edit Word", key=f"edit_{entry['word']}_{random_num}", help="Edit this word"):
                        # Store the word data in session state for editing
                        st.session_state.edit_mode = True
                        st.session_state.edit_word_data = {
                            "word": entry['word'],
                            "meaning": entry.get('meaning', ''),
                            "expressions": entry.get('expressions', []),
                            "phrase": entry.get('phrase', ''),
                            "media": entry.get('media', ''),
                            "category": entry.get('category', category),
                            "difficulty": current_level,
                            "original_file": word_file
                        }
                        # Navigate to add_word page
                        st.switch_page("pages/01_add_word.py")
                        
                    st.markdown("<br>", unsafe_allow_html=True)
                    if current_level == 1 or current_level == 2 or current_level ==3:
                            word_file = "level" + str(current_level) + ".json"
                    random_num = random.randint(0, 300)
                    if st.button("Delete Word", key=f"delete_{entry['word']}_{random_num}", help="Delete this word from vocabulary"):
                        delete_word_from_json(entry['word'], word_file)
                        st.success(f"'{entry['word']}' has been deleted from the vocabulary.")
                        st.rerun()  # Refresh the page to update the list
        
        # st.info("Navigate to other sections to review your learned vocabulary.")
    else:
        st.warning(f"❌ No {current_level} words found")
                    
        
elif selected == "Mail Words":
    st.write("This section would display the mailed words list.")
    button = st.button("Send Today's Words")
    if button:
        result = asyncio.run(mail_trigger())
        print(result)
        
        if result:
            status = result.get('status', '')
            if status == 'no_mailed_words':
                st.info("No words scheduled to be mailed today.")
            elif status == 'emailed_and_marked_sent':
                mailed_words = result.get('mailed_words', [])
                st.success(f"Email sent successfully with {len(mailed_words)} words!")
                st.markdown("### Mailed Words:")
                for w in mailed_words:
                    st.write(f"- **{w.get('word', '')}**: {w.get('meaning', '')} | _{w.get('phrase', '')}_ | _{w.get('media', '')}_")
        else:
            st.error("Failed to send email.")