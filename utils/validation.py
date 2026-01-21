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