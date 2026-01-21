import streamlit as st 
import os
import random
random.seed(42)
import asyncio
from utils.word_functions import (
    load_word_pools, 
    create_audio_file, 
    cleanup_audio_file,
    DEFAULT_CATEGORIES,
    DEFAULT_VOCABULARY_FILE,
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
    delete_word_from_file,
)
from word_widget import create_word_widget, get_difficulty

# Function to create media directory
def initialize_media_directory():
    """Create media directory in the root directory if it doesn't exist"""
    media_dir = os.path.join(os.path.dirname(__file__), "media")
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
        # print(f"Created media directory at: {media_dir}")
    return media_dir

# Initialize media directory
initialize_media_directory()

# Configure the app
st.set_page_config(
    page_title="Vocabulary Builder - Advanced 1",
    page_icon="📚",
    layout="wide"
)

# Custom CSS to increase base font size by 80% for senior users (30% + 50% additional)
def local_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("css/styles.css")

st.title("📚 Vocabulary Builder - Advanced")

# Main Menu Navigation
st.sidebar.title("🎯 Advanced Navigation")

# Level Selection
st.sidebar.markdown("### 🎯 Select Your Learning Level")
level_col1, level_col2, level_col3, level_col4, level_col5 = st.sidebar.columns(5)

with level_col1:
    if st.sidebar.button("📚 **Level 1: Basic vocabulary", key="adv1_level1"):
        st.session_state.selected_level = 1
        
with level_col2:
    if st.sidebar.button("📚 **Level 2: Intermediate vocabulary", key="adv1_level2"):
        st.session_state.selected_level = 2
        
with level_col3:
    if st.sidebar.button("📚 **Level 3: Advanced vocabulary", key="adv1_level3"):
        st.session_state.selected_level = 3

with level_col4:
    if st.sidebar.button("✅ **Learned Words**\n\nReview learned vocabulary", key="adv1_learned"):
        st.session_state.selected_level = "learned"
        
with level_col5:
    if st.sidebar.button("📬 **Mailed Words**\n\nReview mailed vocabulary", key="adv1_mailed"):
        st.session_state.selected_level = "mailed"

# Initialize session state
if 'selected_level' not in st.session_state:
    st.session_state.selected_level = 1  # Default to beginner for Advanced 1 app

# Display current level
current_level = st.session_state.selected_level
if current_level in ["mailed","learned"]:
    # print(f"Current level is: {current_level}")
    st.info(f"✅ **Current Level: {current_level.capitalize()} Words** - Review your mastered vocabulary")
else:
    st.info(f"🎯 **Current Level: {current_level}** - {LEVEL_DESCRIPTIONS[current_level]}")

# Configuration
word_file = DEFAULT_VOCABULARY_FILE
category_list = DEFAULT_CATEGORIES

# Load sample vocabulary button
col1, col2 = st.columns(2)
with col1:
    if current_level in  ["learned", "mailed"]:
        #if st.button(f"📚 Load Learned Words", help="Load your learned vocabulary from learned.json"):
        if current_level == "learned":
            words = load_learned_words()
        else:
            words = load_mailed_words()
            # print(f"Words are loaded for level: {current_level}")
        if words:
            # Convert learned words to the standard vocabulary format and save to the working file
            with open(word_file, "w", encoding='utf-8') as f:
                for word_entry in words:
                    f.write(f"{word_entry['word']} | {word_entry['meaning']} | {word_entry['phrase']} | {word_entry.get('category', 'General')}\n")
            st.success(f"✅ Successfully loaded {len(words)} {current_level} words!")
            # st.info("Navigate to other sections to review your learned vocabulary.")
        else:
            st.warning(f"❌ No {current_level} words found")
    else:
        #   if st.button(f"📚 Load Level {current_level} Vocabulary (160 words)"):
        word_pools = load_word_pools(current_level)
        # print(f"Loaded word pools: {current_level}\n {word_pools}")
        if word_pools:
            success = save_word_pools_to_file(word_pools, word_file)
            if success:
                # st.success(f"✅ Successfully loaded Level {current_level} vocabulary")
                pass
            else:
                st.error(f"❌ Error loading {current_level} vocabulary.")
        else:
            st.error(f"❌ Could not load Level {current_level} word pools from JSON file.")

with col2:
    # Statistics display
    all_words = load_vocabulary_from_file(word_file)
    if all_words:
        st.metric("📊 Total Words", len(all_words))

# Main navigation
select = st.sidebar.radio("Select Learning Mode", [
    "📖 Study Mode", 
    "📊 Progress"
])

# Category and speed selection for both Study Mode and Quiz Mode

# selected_category = st.sidebar.radio("Select a Category", category_list, key="category_radio", horizontal=True)

# Speed selection as radio buttons
st.sidebar.markdown("🔊 **Voice Speed:**")
selected_speed = st.sidebar.radio(
    "Voice Speed Selection",
    options=SPEED_OPTIONS,
    format_func=lambda x: SPEED_LABELS[x],
    key="speed_radio",
    label_visibility="hidden"
)  


if select == "📖 Study Mode":
    selected_category = "general"
    st.subheader("📖 Enhanced Study Mode")
    # print(f"Selected category: {selected_category}")
    # if selected_category:
    # Load vocabulary with expressions from JSON files
    all_words = load_vocabulary_with_expressions(current_level)
    # print(f"All words loaded:\n {all_words}")
    # filtered_words = filter_words_by_category(all_words, selected_category)
    filtered_words = all_words
    # print(f"Filtered words:\n {filtered_words}")
    if filtered_words:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.info(f"📚 Showing {len(filtered_words)} words from {selected_category}")
        with col2:
            search_word = st.text_input("🔍 Search Word", key="search_word_input")
            if search_word:
                # display word with container
                filtered_words = [entry for entry in filtered_words if search_word.lower() in entry['word'].lower()]
                if not filtered_words:
                    st.warning(f"No words found matching '{search_word}' in {selected_category}")
                else:
                    st.info(f"📚 Showing {len(filtered_words)} words matching '{search_word}' in {selected_category}")            
                
        
        for entry in filtered_words:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    difficulty = get_difficulty(entry['word'])
                    # Render the word card with editable expressions
                    create_word_widget(entry, editable_expressions=True, current_level=current_level)

                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Play buttons
                    random_num = random.randint(0, 300)
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
                                f.write(f"{entry['word']} | {entry['meaning']} | {entry['phrase']} | General\n")
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
                        if current_level == 1 or current_level == 2 or current_level ==3:
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
                            "category": entry.get('category', selected_category),
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
