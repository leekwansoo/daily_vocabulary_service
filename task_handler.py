"""
schedule_handler.py

Scheduling:
  - Windows: create a Task Scheduler task to run this script daily at 23:59
  - Linux/macOS: add a cron job to run daily at 23:59

Notes:
  - The script expects `mailed.json` to be in the current working directory or in the project root.
  - SMTP credentials may require app-specific passwords for providers like Gmail.
"""
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
    save_mailed_words_to_file,
    load_mailed_words,
)
from word_widget import create_word_widget, get_difficulty

# Try to import keyring for secure credential storage; optional
from utils.json_manager import load_mailed_words

from mailer import mail_trigger
# Remove Streamlit-dependent import to avoid context errors
# from pages.select_words import select_words_from_vocabulary

# Create standalone version of select_words_from_vocabulary to avoid Streamlit dependencies
def select_words_from_vocabulary_standalone(number_of_words, selection_method, current_level, seq_no=0):
    """
    Standalone version of select_words_from_vocabulary that doesn't depend on Streamlit
    """
    from utils.json_manager import load_vocabulary_with_expressions
    
    all_words = load_vocabulary_with_expressions(current_level)
    print(f"Total words available for selection: {len(all_words)}")
    
    if selection_method == "random":
        selected_words = random.sample(all_words, min(number_of_words, len(all_words)))
    elif selection_method == "sequential":
        selected_words = all_words[seq_no:seq_no + number_of_words]
    else:
        selected_words = []
    
    return selected_words

from database.subscriber_db import (
    add_subscriber,
    list_subscribers,
    Subscriber,
)
def display_vocabulary(vocab_file):
    with open(vocab_file, 'r', encoding='utf-8') as f:
        vocab = json.load(f) 
        
# classify subscribers by level
subscribers = list_subscribers()
levels = [1,2,3]
subscribers_by_level = {}
for sub in subscribers:
    subscribers_by_level.setdefault(sub.level, []).append(sub)

# Save subscribers data to JSON for later access
def save_subscribers_to_json(subscribers_by_level, filename="subscribers_by_level.json"):
    """Convert subscribers to JSON-serializable format and save to file"""
    json_data = {}
    for level, subs in subscribers_by_level.items():
        json_data[str(level)] = []
        for sub in subs:
            subscriber_dict = {
                "id": sub.id,
                "email": sub.email,
                "name": sub.name,
                "level": sub.level,
                "media": sub.media,
                "subscribed_at": sub.subscribed_at.isoformat() if hasattr(sub, 'subscribed_at') else None
            }
            json_data[str(level)].append(subscriber_dict)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    return filename

# Check if we have any subscribers
total_subscribers = sum(len(subs) for subs in subscribers_by_level.values())

if total_subscribers == 0:
    print("⚠️  No subscribers found in database!")
    print("💡 Add subscribers using the Streamlit interface or add sample data below")
    
    # Option to add sample subscribers for testing
    def add_sample_subscribers():
        """Add sample subscribers for testing"""
        sample_subs = [
            {"email": "test1@example.com", "name": "Test User 1", "level": 1, "media": "email"},
            {"email": "test2@example.com", "name": "Test User 2", "level": 2, "media": "email"},
            {"email": "test3@example.com", "name": "Test User 3", "level": 3, "media": "email"}
        ]
        
        for sub_data in sample_subs:
            try:
                add_subscriber(
                    email=sub_data["email"],
                    name=sub_data["name"], 
                    level=sub_data["level"],
                    media=sub_data["media"]
                )
                print(f"✅ Added sample subscriber: {sub_data['name']} ({sub_data['email']})")
            except Exception as e:
                print(f"❌ Failed to add {sub_data['email']}: {e}")
    
    # Uncomment the line below to add sample subscribers
    # add_sample_subscribers()
    
else:
    print(f"📊 Found {total_subscribers} total subscribers")

# Save the subscribers data
subscribers_file = save_subscribers_to_json(subscribers_by_level)
print(f"💾 Subscribers saved to: {subscribers_file}")

def load_subscribers_from_json(filename="subscribers_by_level.json"):
    """Load subscribers data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded subscribers from: {filename}")
        return data
    except FileNotFoundError:
        print(f"File {filename} not found")
        return {}
    except json.JSONDecodeError:
        print(f"Error reading JSON from {filename}")
        return {}

# Example: Load subscribers data later
# loaded_subscribers = load_subscribers_from_json("subscribers_by_level.json")
# list subscriber with levels
level1_subscribers = subscribers_by_level.get(1, [])
level2_subscribers = subscribers_by_level.get(2, [])
level3_subscribers = subscribers_by_level.get(3, [])

print(f"📧 Level 1 Subscribers ({len(level1_subscribers)}): {[sub.email for sub in level1_subscribers] if level1_subscribers else 'None'}")
print(f"📧 Level 2 Subscribers ({len(level2_subscribers)}): {[sub.email for sub in level2_subscribers] if level2_subscribers else 'None'}")
print(f"📧 Level 3 Subscribers ({len(level3_subscribers)}): {[sub.email for sub in level3_subscribers] if level3_subscribers else 'None'}")

# Show JSON file contents for verification
if os.path.exists("subscribers_by_level.json"):
    with open("subscribers_by_level.json", 'r', encoding='utf-8') as f:
        json_content = json.load(f)
    print(f"📄 JSON file contains: {json_content}")
else:
    print("📄 JSON file not found")



    
def mailer_task_handler():   
    # Load subscribers from JSON file (this will have the actual data)
    subscribers_from_json = load_subscribers_from_json("subscribers_by_level.json")
    print(f"🔍 DEBUG: JSON data loaded: {subscribers_from_json}")
    
    # If JSON file is empty, refresh from database
    if not any(subscribers_from_json.get(str(level), []) for level in [1, 2, 3]):
        print("⚠️ JSON file appears empty, refreshing from database...")
        fresh_subscribers = list_subscribers()
        fresh_subscribers_by_level = {}
        for sub in fresh_subscribers:
            fresh_subscribers_by_level.setdefault(sub.level, []).append(sub)
        
        # Save fresh data to JSON
        if fresh_subscribers:
            subscribers_file = save_subscribers_to_json(fresh_subscribers_by_level)
            subscribers_from_json = load_subscribers_from_json("subscribers_by_level.json")
            print(f"🔄 Refreshed data from database: {subscribers_from_json}")
        else:
            print("❌ No subscribers found in database either!")
    
    current_level = [1,2,3]            
    for level in current_level:
        # Get emails from JSON data instead of database query
        level_data = subscribers_from_json.get(str(level), [])
        to_addr = [sub['email'] for sub in level_data] if level_data else []
        
        print(f"🔍 DEBUG: Level {level} data from JSON: {level_data}")
        print(f"Level {level} subscribers' emails: {to_addr}")
        if to_addr and len(to_addr) > 0:
            print(f"Preparing to send emails to Level {level} subscribers: {to_addr}")
            # st.subheader(f"words for Level {level} - {LEVEL_DESCRIPTIONS.get(level, '')}")
            selected_words_for_level = select_words_from_vocabulary_standalone(number_of_words=2, selection_method="random", current_level=level)
            # words = load_mailed_words(selected_words_for_level)    
            file_name = f"selected_level{level}.json"        
            result = save_mailed_words_to_file(selected_words_for_level, mailed_file=file_name)
            if result:
                words = load_mailed_words(file_name)
                result = asyncio.run(mail_trigger(words=words, to_addr=to_addr))
                print(f"✅ Successfully processed {len(selected_words_for_level)} words for Level {level}")
                # Display selected words in console format
                for i, word_entry in enumerate(selected_words_for_level, 1):
                    print(f"  {i}. {word_entry.get('word', 'N/A')} - {word_entry.get('definition', 'No definition available')}")
                
                
        else:
            print(f"No subscribers found for Level {level}. Skipping email sending.")
            
mailer_task_handler()
                        
        

          