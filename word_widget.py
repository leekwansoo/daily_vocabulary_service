# from turtle import width # Dont use TKinter environment
import streamlit as st 
import random
import os
import json
from pathlib import Path
from video_play import play_video, display_photo,  _drive_embed_link, _drive_direct_link, _detect_media_type

def get_difficulty(difficulty_level):
    """Get difficulty level for a word (robust to unexpected DIFFICULTY_LEVELS types)."""
    if difficulty_level == 1:
        return "⭐"
    # If DIFFICULTY_LEVELS is a dict-like object
    if difficulty_level == 2:
        return "⭐⭐"
    if difficulty_level == 3:
        return "⭐⭐⭐"
    else:
        return "⭐"


def create_word_widget(entry: dict, editable_expressions=True, editable_phrase=True, current_level=None):
    """Render the word card (meaning, expressions, phrase) and show video if provided.
    Handles local files, direct URLs, and attempts to convert Google Drive links.
    Also supplies an 'Open in external player' button that calls play_video()."""
    st.markdown("---")
    
    difficulty_level = entry.get('difficulty', 1)
    difficulty = get_difficulty(difficulty_level)
    # print(f"Difficulty for '{entry['word']}': {difficulty}")
    st.markdown(f"### 📚 {entry['word']} {difficulty}")
    
    # Larger font for Meaning with balanced styling
    st.markdown(f"<div class='balanced-meaning'><strong>Meaning:</strong> {entry.get('meaning','')}</div>", unsafe_allow_html=True)
    
    # Larger font for Phrase with balanced styling
    st.markdown(f"<div class='balanced-phrase'><strong>Phrase:</strong> {entry.get('phrase','')}</div>", unsafe_allow_html=True)
    
    # Handle expressions display - either editable or read-only
    if editable_expressions and current_level != "learned":
        # Get current expressions as default text - limit to 5 and format properly
        current_expressions = entry.get('expressions', [])[:5]  # Limit to 5 expressions
        # Smaller font for expressions label with compact styling and count
        current_count = len(current_expressions) if current_expressions else 0
        st.markdown(f"<div class='balanced-expressions'><strong>✏️ Expressions ({current_count}/5):</strong></div>", unsafe_allow_html=True)
        # Format with proper comma separation and line breaks for better readability
        if current_expressions:
            default_text = ",\n".join(current_expressions)
        else:
            default_text = ""
        
        # Calculate height based on number of expressions (auto-adjust)
        num_expressions = len(current_expressions) if current_expressions else 1
        # Base height + additional height per expression (minimum 2 lines, maximum 6 lines for 5 expressions)
        calculated_height = max(140, min(140, 40 + (num_expressions * 20)))
        
        # Custom CSS for auto-adjusting text area
        st.markdown(f"""
        <style>
        div[data-testid="stTextArea"] textarea {{
            font-size: 1.4em !important;
            line-height: 1.4 !important;
            padding: 8px 12px !important;
            min-height: 60px !important;
            height: {calculated_height}px !important;
            resize: vertical !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Text area for expressions input with auto-calculated height
        random_num = random.randint(1, 100)
        expressions_input = st.text_area(
            "Enter expressions separated by commas (max 5):", 
            value=default_text,
            key=f"expr_widget_{entry['word']}_{random_num}",
            height=calculated_height,
            label_visibility="collapsed",
            help="Enter up to 5 expressions, separated by commas. Use line breaks for better readability."
        )
        
        # Auto-save functionality with session state
        if f"prev_expr_{entry['word']}" not in st.session_state:
            st.session_state[f"prev_expr_{entry['word']}"] = default_text
        
        # Parse expressions for processing (but don't auto-save yet)
        if expressions_input.strip():
            # Handle both comma and line break separation
            # First split by line breaks, then by commas
            all_expressions = []
            for line in expressions_input.split('\n'):
                line_expressions = [expr.strip() for expr in line.split(',') if expr.strip()]
                all_expressions.extend(line_expressions)
            
            # Limit to 5 expressions and clean up
            new_expressions = [expr for expr in all_expressions if expr][:5]
            
            # Show warning if more than 5 expressions were entered
            if len(all_expressions) > 5:
                st.warning(f"⚠️ Only first 5 expressions will be saved (entered {len(all_expressions)})", icon="📝")
        else:
            new_expressions = []
        
              
        # Save Expressions Button - always visible for manual saving
        st.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
        
        # Check if expressions are different from saved ones (for styling)
        current_expressions_text = ",\n".join(entry.get('expressions', []))
        expressions_changed = expressions_input.strip() != current_expressions_text
        
        # Button styling based on whether there are changes
        button_type = "primary" if expressions_changed else "secondary"
        button_text = f"💾 Save Expressions ({len(new_expressions)}/5)" + (" *" if expressions_changed else "")
        random_num = random.randint(1, 100)
        if st.button(button_text, key=f"save_expr_{entry['word']}_{random_num}", type=button_type):
                # Update the entry
                entry['expressions'] = new_expressions
                
                # Save to JSON file
             
                level_files = {
                    1: "level1.json",
                    2: "level2.json", 
                    3: "level3.json"
                }
                
                if current_level and current_level in level_files:
                    filename = level_files[current_level]
                    if os.path.exists(filename):
                        try:
                            with open(filename, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            # Find and update the word in the appropriate category
                            category = entry.get('category', '').lower()
                            if category in data:
                                for i, word_entry in enumerate(data[category]):
                                    if word_entry['word'] == entry['word']:
                                        data[category][i]['expressions'] = new_expressions
                                        break
                            
                            # Save back to file
                            with open(filename, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            
                            # Show success message
                            st.success(f"✅ {len(new_expressions)} expressions saved successfully!", icon="💾")
                            st.rerun()  # Refresh to show updated data
                        except Exception as e:
                            st.error(f"❌ Error saving expressions: {e}")
    else:
        # Read-only expressions display with balanced styling (max 5)
        expressions = entry.get('expressions', [])[:5]  # Limit to 5 expressions for display
        if expressions:
            st.markdown("<div class='balanced-expressions'><strong>Expressions:</strong></div>", unsafe_allow_html=True)
            for expr in expressions:
                st.markdown(f"<div class='balanced-expressions'>• {expr}</div>", unsafe_allow_html=True)
    
    # Add small spacing between expressions and phrase
    st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)
       
    # Media handling (image or video)    
    media_path = entry.get('media') or entry.get('video')
    if media_path:
        # Detect media type automatically
        media_type = _detect_media_type(media_path)
        
        st.markdown("**Media:**")
        proj_root = Path(__file__).parent
        is_url = str(media_path).startswith(("http://", "https://"))
        if is_url:
            st.markdown(f"🔗 URL: {media_path}")
            
        else:
            # Handle based on media type
            if media_type == 'image':
                # Image handling
                if not is_url:
                    # Local image
                    img_path = Path(media_path)
                    if not img_path.is_absolute():
                        img_path = (proj_root / img_path).resolve()
                    if img_path.exists():
                        st.image(str(img_path), use_container_width=True)
                    else:
                        st.warning(f"Image file not found: {img_path}")
                else:
                    # URL image
                    try:
                        st.image(media_path, use_container_width=True)
                    except Exception as e:
                        st.error(f"Cannot load image: {e}")
                        st.markdown(f"[🖼️ Open image link]({media_path})")
            
            elif media_type == 'video':
                # Video handling
                if not is_url:
                    # Local video file
                    vp = Path(media_path)
                    if not vp.is_absolute():
                        vp = (proj_root / vp).resolve()
                    if vp.exists():
                        try:
                            st.video(str(vp))
                        except Exception:
                            try:
                                with open(vp, "rb") as vf:
                                    st.video(vf.read())
                            except Exception as e:
                                st.error(f"Cannot play local video: {e}")
                        # Provide external open button
                        random_num = random.randint(1, 100)
                        if st.button("Open in external player", key=f"open_ext_{entry['word']}_{random_num}"):
                            play_video(str(vp))
                    else:
                        st.warning(f"Video file not found: {vp}")
                        st.write(str(vp))
                elif "drive.google.com" in str(media_path):
                    # URL video handling
                    if "drive.google.com" in str(media_path):
                        # Google Drive video
                        embed_link = _drive_embed_link(media_path)
                        direct = _drive_direct_link(media_path)
                        
                        if embed_link:
                            st.info("🎥 Google Drive Video")
                            try:
                                st.markdown(
                                    f'<iframe src="{embed_link}" width="100%" height="400" frameborder="0" allowfullscreen></iframe>',
                                    unsafe_allow_html=True
                                )
                            except Exception as e:
                                st.warning(f"⚠️ Cannot embed video: {str(e)[:50]}")
                            
                            st.markdown(f"[📺 Open in browser]({media_path})")
                            random_num = random.randint(1, 100)
                            if st.button("🎬 Open in external player", key=f"open_ext_{entry['word']}_{random_num}"):
                                if direct:
                                    play_video(direct)
                                else:
                                    play_video(media_path)
                            else:
                                # Not a single-file share (maybe folder) — provide link + external open
                                st.markdown(f"[Open Google Drive link]({media_path})")
                                random_num = random.randint(1, 100)
                                if st.button("Open in external player", key=f"open_ext_{entry['word']}_{random_num}"):
                                    play_video(media_path)
                        else:
                            # Generic URL video: try to let Streamlit play it
                            random_num = random.randint(1, 100)
                            try:
                                st.video(media_path)
                            except Exception as e:
                                st.warning(f"⚠️ Cannot embed video from URL")
                                st.markdown(f"[📺 Open video link]({media_path})")
                                if st.button("🎬 Open in external player", key=f"open_ext_{entry['word']}_{random_num}"):
                                    play_video(media_path)
                else:
                    # Generic URL video
                    random_num = random.randint(1, 100)
                    try:
                        st.video(media_path)
                    except Exception as e:
                        st.warning(f"⚠️ Cannot embed video from URL")
                        st.markdown(f"[📺 Open video link]({media_path})")
                        if st.button("🎬 Open in external player", key=f"open_ext_{entry['word']}_{random_num}"):
                            play_video(media_path)
                        
            elif media_type == 'audio':
                # Audio handling
                if not is_url:
                    # Local audio file
                    audio_path = Path(media_path)
                    if not audio_path.is_absolute():
                        audio_path = (proj_root / audio_path).resolve()
                    if audio_path.exists():
                        st.audio(str(audio_path))
                    else:
                        st.warning(f"Audio file not found: {audio_path}")
                else:
                    # URL audio
                    try:
                        st.audio(media_path)
                    except Exception as e:
                        st.error(f"Cannot load audio: {e}")
                        st.markdown(f"[� Open audio link]({media_path})")
            
            else:
                # Unknown media type - try to determine by content
                st.info(f"📎 Media file detected (type: {media_type})")
                if not is_url:
                    # Local file with unknown type
                    unknown_path = Path(media_path)
                    if not unknown_path.is_absolute():
                        unknown_path = (proj_root / unknown_path).resolve()
                    if unknown_path.exists():
                        st.markdown(f"**File:** `{unknown_path.name}`")
                        # Try as image first, then video
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📷 Try as Image", key=f"img_{entry['word']}"):
                                try:
                                    st.image(str(unknown_path), use_container_width=True)
                                except Exception as e:
                                    st.error(f"Cannot display as image: {e}")
                        with col2:
                            if st.button("🎬 Try as Video", key=f"vid_{entry['word']}"):
                                try:
                                    st.video(str(unknown_path), use_container_width=True)
                                except Exception as e:
                                    st.error(f"Cannot play as video: {e}")
                    else:
                        st.warning(f"File not found: {unknown_path}")
                else:
                    # URL with unknown type
                    st.markdown(f"[🔗 Open media link]({media_path})")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📷 Try as Image", key=f"img_{entry['word']}"):
                            try:
                                st.image(media_path, use_container_width=True)
                            except Exception as e:
                                st.error(f"Cannot display as image: {e}")
                    with col2:
                        if st.button("🎬 Try as Video", key=f"vid_{entry['word']}"):
                            try:
                                st.video(media_path, use_container_width=True)
                            except Exception as e:
                                st.error(f"Cannot play as video: {e}")
            
            st.markdown("---")
            
    return
