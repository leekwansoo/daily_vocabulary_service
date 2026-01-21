# Json file manager utility

import os
import json

def load_json(file_path):
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    with open(file_path, "r") as file:
        return json.load(file)

def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
        
def add_words_to_json(word_entry, json_file="level1.json", category="general"):
    """
    Add a new word entry to the specified JSON file under the given category.
    
    Args:
        word_entry (dict): Dictionary with word details
        json_file (str): Path to the JSON file
        category (str): Category under which to add the word
    """
    # Load existing data
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}
    
    # Ensure category exists
    if category not in data:
        data[category] = []
    
    # Append new word entry
    data[category].append(word_entry)
    
    # Save back to JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
def delete_word_from_file(word_to_delete, word_file):
    print(f"Deleting word: {word_to_delete} from file: {word_file}")
    """Delete a word from the vocabulary file (supports both JSON and text formats)"""
    
    # Check if it's a JSON file
    if word_file.endswith('.json'):
        return delete_word_from_json(word_to_delete, word_file)
    else:
        # Handle text files (original logic)
        with open(word_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filter out the word to delete
        updated_lines = []
        for line in lines:
            if line.strip():
                parts = line.strip().split(' | ')
                if len(parts) >= 1 and parts[0].lower() != word_to_delete.lower():
                    updated_lines.append(line)
        
        # Write back to file
        with open(word_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        return True

def update_word_audio(word_name, audio_path, json_file):
    """Update the audio field for a word in a JSON vocabulary file"""
    try:
        # Load the JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Search through all categories and update the word's audio field
        word_found = False
        for category, words in data.items():
            for word in words:
                if word.get('word', '').lower() == word_name.lower():
                    word['audio'] = audio_path
                    word_found = True
                    print(f"Updated audio for '{word_name}' in category '{category}' to '{audio_path}'")
                    break
            if word_found:
                break
        
        if word_found:
            # Save the updated data back to the file
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        else:
            print(f"Word '{word_name}' not found in {json_file}")
            return False
            
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error processing JSON file {json_file}: {e}")
        return False

def delete_word_from_json(word_to_delete, json_file):
    """Delete a word from a JSON vocabulary file"""
    try:
        # Load the JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Search through all categories and remove the word
        word_found = False
        for category, words in data.items():
            # Filter out the word to delete (case-insensitive)
            original_count = len(words)
            data[category] = [word for word in words if word.get('word', '').lower() != word_to_delete.lower()]
            if len(data[category]) < original_count:
                word_found = True
                print(f"Word '{word_to_delete}' found and removed from category '{category}'")
        
        if word_found:
            # Save the updated data back to the file
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Successfully deleted '{word_to_delete}' from {json_file}")
            return True
        else:
            print(f"Word '{word_to_delete}' not found in {json_file}")
            return False
            
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error processing JSON file {json_file}: {e}")
        return False

def load_vocabulary_with_expressions(level):
    """Load vocabulary from JSON files with expressions included"""
    import json
    
    if level in ["learned", "mailed"]:
        if level == "mailed":
            return load_mailed_words()
        return load_learned_words()
    
    # Map level to filename
    level_files = {
        1: "level1.json",
        2: "level2.json", 
        3: "level3.json"
    }
    
    filename = level_files.get(level)
    if not filename or not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten all categories into a single list
        all_words = []
        for category, words in data.items():
            for word_entry in words:
                # Add category to each word entry
                word_entry['category'] = category
                all_words.append(word_entry)
        
        return all_words
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def load_vocabulary_from_file(file_path):
    #print(file_path)
    """
    Load vocabulary words from a text file
    
    Args:
        file_path (str): Path to the vocabulary file
        
    Returns:
        list: List of dictionaries containing word data
    """
    word_list = []
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip():  # Skip empty lines
                    parts = line.strip().split(" | ")
                    if len(parts) >= 5:
                        word_details = {
                            "word": parts[0],
                            "meaning": parts[1],
                            "phrase": parts[2],
                            "media": parts[3],
                            "category": parts[4]
                        }
                        word_list.append(word_details)
            #print(word_list)
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
    except Exception as e:
        print(f"Error loading vocabulary: {e}")

    return word_list

def save_word_pools_to_file(word_pools, file_path):
    """
    Save word pools to vocabulary file
    
    Args:
        word_pools (dict): Dictionary containing word pools
        file_path (str): Path to save the vocabulary file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, "w", encoding='utf-8') as f:
            for category, words in word_pools.items():
                for word_data in words:
                    f.write(f"{word_data['word']} | {word_data['meaning']} | {word_data['phrase']} | {category}\n")
        return True
    except Exception as e:
        print(f"Error saving word pools: {e}")
        return False

def load_learned_words(learned_file="learned.json"):
    """Load learned words from learned.json and convert to vocabulary format"""
    import json
    
    if not os.path.exists(learned_file):
        return []
    
    try:
        with open(learned_file, 'r', encoding='utf-8') as f:
            learned_words = json.load(f)
        
        # Convert to the same format as regular vocabulary
        formatted_words = []
        for word_entry in learned_words:
            formatted_word = {
                'word': word_entry.get('word', ''),
                'meaning': word_entry.get('meaning', ''),
                'phrase': word_entry.get('phrase', ''),
                'category': word_entry.get('category', 'general'),
                'learned_date': word_entry.get('learned_date', '')
            }
            formatted_words.append(formatted_word)
        
        return formatted_words
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    
def load_mailed_words(mailed_file="mailed.json"):
    """Load mailed words from mailed.json and convert to vocabulary format"""
    import json
    
    if not os.path.exists(mailed_file):
        return []
    
    try:
        with open(mailed_file, 'r', encoding='utf-8') as f:
            mailed_words = json.load(f)
        
        # Convert to the same format as regular vocabulary
        formatted_words = []
        for word_entry in mailed_words:
            formatted_word = {
                'word': word_entry.get('word', ''),
                'meaning': word_entry.get('meaning', ''),
                'phrase': word_entry.get('phrase', ''),
                'media': word_entry.get('media', ''),
                'mailed_date': word_entry.get('mailed_date', '')
            }
            formatted_words.append(formatted_word)
        
        return formatted_words
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_learned_words_to_file(learned_words, learned_file="learned.json"):
    """Save learned words back to JSON file"""
    import json
    
    with open(learned_file, 'w', encoding='utf-8') as f:
        json.dump(learned_words, f, ensure_ascii=False, indent=2)
    
    return True

def save_mailed_words_to_file(mailed_words, mailed_file="mailed.json"):
    """Save mailed words back to JSON file"""
    import json
    # if mailed_word does not include 'mailed_date', add it with current timestamp
    import datetime
    for entry in mailed_words:
        if 'mailed_date' not in entry:
            entry['mailed_date'] = datetime.datetime.now().isoformat()
    with open(mailed_file, 'w', encoding='utf-8') as f:
        json.dump(mailed_words, f, ensure_ascii=False, indent=2)
    
    return True

def save_to_learned(word_entry, learned_file="learned.json"):
    """Save a word entry to learned.json file"""
    import json
    
    # Load existing learned words
    learned_words = []
    if os.path.exists(learned_file):
        try:
            with open(learned_file, 'r', encoding='utf-8') as f:
                learned_words = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            learned_words = []
    
    # Add timestamp to the entry
    import datetime
    word_entry_with_timestamp = word_entry.copy()
    word_entry_with_timestamp['learned_date'] = datetime.datetime.now().isoformat()
    
    # Check if word already exists in learned list
    existing_word = next((w for w in learned_words if w['word'].lower() == word_entry['word'].lower()), None)
    if not existing_word:
        learned_words.append(word_entry_with_timestamp)
        
        # Save back to file
        with open(learned_file, 'w', encoding='utf-8') as f:
            json.dump(learned_words, f, ensure_ascii=False, indent=2)
        return True
    return False

def save_to_mailed(word_entry, mailed_file="mailed.json"):
    """Save a word entry to mailed.json file"""
    import json
    
    # Load existing learned words
    mailed_words = []
    if os.path.exists(mailed_file):
        try:
            with open(mailed_file, 'r', encoding='utf-8') as f:
                mailed_words = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            mailed_words = []
    
    # Add timestamp to the entry
    import datetime
    word_entry_with_timestamp = word_entry.copy()
    word_entry_with_timestamp['mailed_date'] = datetime.datetime.now().isoformat()
    
    # Check if word already exists in mailed list
    existing_word = next((w for w in mailed_words if w['word'].lower() == word_entry['word'].lower()), None)
    if not existing_word:
        mailed_words.append(word_entry_with_timestamp)
        
        # Save back to file
        with open(mailed_file, 'w', encoding='utf-8') as f:
            json.dump(mailed_words, f, ensure_ascii=False, indent=2)
        return True
    return False

def filter_words_by_category(word_list, category):
    """
    Filter words by category
    
    Args:
        word_list (list): List of word dictionaries
        category (str): Category to filter by

    Returns:
        list: Filtered list of words matching the category
    """
    return [word for word in word_list if word.get('category', '').lower() == category.lower()]
        


def get_category_statistics(word_list):
    """
    Get statistics about words in each category

    Args:
        word_list (list): List of word dictionaries

    Returns:
        dict: Dictionary with category names as keys and word counts as values
    
    Args:
        word_list (list): List of word dictionaries
        
    Returns:
        dict: Dictionary with category names as keys and word counts as values
    """
    category_stats = {}
    for word in word_list:
        category = word.get('category', 'Unknown').lower()
        category_stats[category] = category_stats.get(category, 0) + 1
    return category_stats


def validate_word_entry(word, meaning, phrase="", category="general"):
    """
    Validate word entry data
    
    Args:
        word (str): The vocabulary word
        meaning (str): The word's meaning
        phrase (str): Example phrase (optional)
        category (str): Word category
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not word or not word.strip():
        return False, "Word cannot be empty"
    
    if not meaning or not meaning.strip():
        return False, "Meaning cannot be empty"
    
    if len(word.strip()) > 100:
        return False, "Word is too long (max 100 characters)"
    
    
    if len(meaning.strip()) > 500:
        return False, "Meaning is too long (max 500 characters)"
    
    if phrase and len(phrase.strip()) > 500:
        return False, "Phrase is too long (max 500 characters)"
    
    return True, ""
