# test program for subscriber_db.py
from datetime import datetime
import streamlit as st 


from database.subscriber_db import (
    add_subscriber,
    delete_subscriber,
    list_subscribers,
    update_subscriber,
    Subscriber,
)

def edit_subscriber():
    with st.form(key="add_subscriber_form"):
        email = st.text_input("Email Address")
        name = st.text_input("Name")
        level_option = st.radio("Level", options=["Level 1", "Level 2", "Level 3"], horizontal=True)
        # Convert level option to integer
        level_map = {"Level 1": 1, "Level 2": 2, "Level 3": 3}
        level = level_map[level_option]
        media = st.text_input("Media (optional)")
        subscribed_at = datetime.now().isoformat()
        if st.form_submit_button("Add Subscriber"):
            add_subscriber(subscribed_at, email, name, level, media)
            return {"email": email, "name": name, "level": level_option, "media": media, "subscribed_at": subscribed_at}
    
def display_subscriber(subscribers):
    if subscribers is not None:
        # Display header row
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 4, 7, 2, 3, 3, 2, 2])
        
        with col1:
            st.write("**ID**")
        with col2:
            st.write("**Name**")
        with col3:
            st.write("**Email**")
        with col4:
            st.write("**Level**")
        with col5:
            st.write("**Subscribe_date**")
        with col6:
            st.write("**Media**")
        with col7:
            st.write("**Edit**")
        with col8:
            st.write("**Delete**")
        
        st.markdown("---")
        
        # Display subscriber rows
        for sub in subscribers:
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 4, 7, 2, 3, 3, 2, 2])
            
            with col1:
                st.write(f"**{sub.id}**")
            with col2:
                st.write(sub.name)
            with col3:
                st.write(sub.email)
            with col4:
                st.write(sub.level_display)
            with col5:
                st.write(sub.subscribed_at.strftime("%Y-%m-%d"))
            with col6:
                st.write(sub.media or "N/A")
            with col7:
                if st.button("✏️", key=f"edit_{sub.id}"):
                    st.session_state.edit_subscriber = sub
                    st.session_state.show_edit_form = True
            with col8:
                if st.button("🗑️", key=f"del_{sub.id}"):
                    delete_subscriber(sub.email)
                    st.success(f"Deleted subscriber: {sub.email}")
                    st.rerun()
            
            st.markdown("---")
        
        # Show edit form if edit button was clicked
        if st.session_state.get("show_edit_form", False) and st.session_state.get("edit_subscriber"):
            sub = st.session_state.edit_subscriber
            st.subheader(f"✏️ Edit Subscriber: {sub.name}")
            
            with st.form(key="edit_form"):
                new_name = st.text_input("Name", value=sub.name)
                new_email = st.text_input("Email", value=sub.email)
                new_media = st.text_input("Media", value=sub.media or "")
                
                # Add level selection to edit form
                level_options = ["Beginner", "Intermediate", "Advanced"]
                level_map = {1: "Beginner", 2: "Intermediate", 3: "Advanced"}
                reverse_level_map = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
                current_level_display = level_map.get(sub.level, "Beginner")
                new_level_option = st.radio("Level", options=level_options, index=level_options.index(current_level_display))
                new_level = reverse_level_map[new_level_option]
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    submit = st.form_submit_button("Save Changes")
                with col_cancel:
                    cancel = st.form_submit_button("Cancel")
                
                if submit:
                    # Update subscriber with all fields
                    update_subscriber(
                        old_email=sub.email,
                        new_email=new_email if new_email != sub.email else None,
                        new_name=new_name if new_name != sub.name else None,
                        new_level=new_level if new_level != sub.level else None,
                        new_media=new_media if new_media != (sub.media or "") else None
                    )
                    st.session_state.show_edit_form = False
                    st.session_state.edit_subscriber = None
                    st.success(f"Updated subscriber: {new_name}")
                    st.rerun()
                
                if cancel:
                    st.session_state.show_edit_form = False
                    st.session_state.edit_subscriber = None
                    st.rerun()
    else:
        st.info("No subscribers found.")
  

    
    