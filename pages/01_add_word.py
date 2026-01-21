import streamlit as st 
from utils.word_functions import DEFAULT_CATEGORIES
from utils.word_functions import DIFFICULTY_LEVELS
import json
import os

def add_word_to_json(word_entry):
    """
    Add a new word entry to the vocabulary storage.
    
    Args:
        word_entry (dict): Dictionary with word details
    """
    category = word_entry.get("category", "general")
    difficulty_level = word_entry.get("difficulty", 1)
    word = word_entry.get("word", "")
    meaning = word_entry.get("meaning", "")
    expressions = word_entry.get("expressions", [])
    phrase = word_entry.get("phrase", "")
    media = word_entry.get("media", "")
    new_word_entry = {
        "word": word,
        "meaning": meaning,
        "expressions": expressions,
        "phrase": phrase,
        "media": media,
    }
    if difficulty_level == 1:
        json_file = "level1.json"
    elif difficulty_level == 2:
        json_file = "level2.json"
    elif difficulty_level == 3:
        json_file = "level3.json"
    else:
        st.error("Invalid difficulty level.")
        return

    with open(json_file, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        category = word_entry.get("category", "general")
        if category not in data:
            data[category] = []

        data[category].append(new_word_entry)
        
        # Write the updated data back to the JSON file
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()

def update_word_in_json(word_entry, original_file):
    """
    Update an existing word entry in the vocabulary storage.
    
    Args:
        word_entry (dict): Dictionary with updated word details
        original_file (str): The JSON file where the word is stored
    """
    word = word_entry.get("word", "")
    category = word_entry.get("category", "general")
    meaning = word_entry.get("meaning", "")
    expressions = word_entry.get("expressions", [])
    phrase = word_entry.get("phrase", "")
    media = word_entry.get("media", "")
    
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find and update the word in the appropriate category
        word_found = False
        for cat in data:
            if isinstance(data[cat], list):
                for i, entry in enumerate(data[cat]):
                    if entry.get('word', '').lower() == word.lower():
                        # Update the entry
                        data[cat][i] = {
                            "word": word,
                            "meaning": meaning,
                            "expressions": expressions,
                            "phrase": phrase,
                            "media": media,
                        }
                        word_found = True
                        break
            if word_found:
                break
        
        if word_found:
            # Write the updated data back to the JSON file
            with open(original_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        else:
            st.error(f"Word '{word}' not found in {original_file}")
            return False
            
    except Exception as e:
        st.error(f"Error updating word: {str(e)}")
        return False

# Check if we're in edit mode
edit_mode = st.session_state.get('edit_mode', False)
edit_data = st.session_state.get('edit_word_data', {})

if edit_mode:
    st.title("✏️ Edit Word")
    word_position = edit_data.get('word_position', 0) + 1  # Convert to 1-based index
    total_words = edit_data.get('total_words', 0)
    st.info(f"Editing word: **{edit_data.get('word', '')}** (Word {word_position} of {total_words})")
else:
    st.title("➕ Add New Word")

st.sidebar.markdown("📝 **Word Details:**")
st.sidebar.subheader("Enter the details below:")

# Pre-fill form if in edit mode
default_category = edit_data.get('category', 'general') if edit_mode else 'general'
default_difficulty = edit_data.get('difficulty', 1) if edit_mode else 1
default_media = edit_data.get('media', '') if edit_mode else ''

category = st.sidebar.radio(
    "Word Category:", 
    DEFAULT_CATEGORIES, 
    index=DEFAULT_CATEGORIES.index(default_category) if default_category in DEFAULT_CATEGORIES else 0,
    key="word_category_radio", 
    horizontal=True
    ).lower()

difficulty_level = st.sidebar.radio(
    "Difficulty Level:", 
    DIFFICULTY_LEVELS, 
    index=DIFFICULTY_LEVELS.index(default_difficulty) if default_difficulty in DIFFICULTY_LEVELS else 0,
    key="word_difficulty_select", 
    horizontal=True
)
# Upload File for media (optional)
media_file = st.sidebar.file_uploader("Upload Media File (optional):", type=["mp4", "jpg", "wav"])
if media_file:
    media_path = os.path.join("media", media_file.name)
    with open(media_path, "wb") as f:
        f.write(media_file.getbuffer())
    st.sidebar.success(f"Uploaded file saved to {media_path}")
    media = f"media/{media_file.name}"
else:
    media = default_media

print(media)

# Pre-fill fields if in edit mode
word = st.text_input("Word", value=edit_data.get('word', ''), disabled=edit_mode)
meaning = st.text_input("Meaning", value=edit_data.get('meaning', ''))
expressions_default = '\n'.join(edit_data.get('expressions', [])) if edit_mode else ''
expressions = st.text_area("Expressions (one per line)", value=expressions_default, height=100).split("\n")
phrase = st.text_input("Example Phrase (optional)", value=edit_data.get('phrase', ''))
media = st.text_input("Media Path (optional)", value=media)
# Different button labels for add vs edit mode
button_label = "💾 Update Word" if edit_mode else "➕ Add Word"
button_key = "update_word_button" if edit_mode else "add_word_button"

if st.button(button_label, key=button_key):
    word_entry = {
        "word": word,
        "meaning": meaning,
        "expressions": [expr.strip() for expr in expressions if expr.strip()],
        "phrase": phrase,
        "media": media,
        "category": category,
        "difficulty": difficulty_level
    }
    
    if edit_mode:
        # Update existing word
        original_file = edit_data.get('original_file', f"level{difficulty_level}.json")
        success = update_word_in_json(word_entry, original_file)
        if success:
            word_position = edit_data.get('word_position', 0)
            st.success(f"✅ Word '{word}' updated successfully! (Position: {word_position + 1})")
            # Clear edit mode from session state
            st.session_state.edit_mode = False
            st.session_state.edit_word_data = {}
            # Automatically go back to main app
            st.switch_page("app.py")
    else:
        # Add new word
        add_word_to_json(word_entry)
        st.success(f"✅ Word '{word}' added to category '{category}' at level{difficulty_level}.json")

# Cancel button for edit mode
if edit_mode:
    if st.button("❌ Cancel", key="cancel_edit"):
        st.session_state.edit_mode = False
        st.session_state.edit_word_data = {}
        st.switch_page("app.py")
