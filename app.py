import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import base64
from pathlib import Path

# Import utility functions
from utils.image_processor import classify_image
from utils.story_generator import generate_story
from utils.voice_generator import text_to_speech

# Page config
st.set_page_config(
    page_title="Snap & Learn",
    page_icon="📸",
    layout="wide"
)

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)
os.makedirs("audio", exist_ok=True)

# Initialize parent log
PARENT_LOG_FILE = "data/parent_log.json"

def load_parent_log():
    """Load parent log from JSON file"""
    if os.path.exists(PARENT_LOG_FILE):
        with open(PARENT_LOG_FILE, 'r') as f:
            return json.load(f)
    return {"sessions": []}

def save_to_parent_log(object_detected, story):
    """Save interaction to parent log"""
    log = load_parent_log()
    
    session = {
        "timestamp": datetime.now().isoformat(),
        "object_detected": object_detected,
        "story_generated": story
    }
    
    log["sessions"].append(session)
    
    with open(PARENT_LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2)

def get_audio_html(audio_path):
    """Create HTML audio player"""
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    audio_html = f"""
    <audio controls autoplay style="width: 100%;">
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    """
    return audio_html

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["📸 Snap & Learn", "👨‍👩‍👧 Parent Dashboard"])

if page == "📸 Snap & Learn":
    # Main page
    st.title("📸 Snap & Learn")
    st.markdown("### Take a picture of anything around you and discover something amazing!")
    
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload a photo or drawing",
        type=['png', 'jpg', 'jpeg'],
        help="Take a picture of a butterfly, leaf, toy, or your drawing!"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption="Your picture!")
        
        with col2:
            if st.button("🔍 Discover!", type="primary"):
                with st.spinner("🔎 Looking closely at your picture..."):
                    # Process image
                    image = Image.open(uploaded_file)
                    
                    # Step 1: Classify image
                    object_name = classify_image(image)
                    
                    with st.spinner("✨ Creating a fun story for you..."):
                        story = generate_story(object_name)
                        
                    # Step 3: Generate voice
                    with st.spinner("🎵 Making it talk..."):
                        audio_file = text_to_speech(story, object_name)
                        
                    # Display results
                    st.success(f"### I found a {object_name}! 🎉")
                        
                    st.markdown("---")
                    st.markdown("### 📖 Here's something cool:")
                    st.markdown(f"*{story}*")
                        
                    st.markdown("---")
                    st.markdown("### 🔊 Listen to the story:")
                        
                    if audio_file and os.path.exists(audio_file):
                        st.markdown(get_audio_html(audio_file), unsafe_allow_html=True)
                        
                    # Save to parent log
                    save_to_parent_log(object_name, story)
                        
                    st.balloons()

    # Instructions
    with st.expander("ℹ️ How to use Snap & Learn"):
        st.markdown("""
        1. **Type your name** in the box above
        2. **Upload a picture** of anything around you - a toy, a pet, a plant, or your drawing!
        3. **Click "Discover!"** to learn something fun
        4. **Listen** to the story about what you found
        
        Try these ideas:
        - 🦋 A butterfly or insect
        - 🍎 Fruits or vegetables
        - 🌳 Leaves or flowers
        - 🎨 Your own drawings
        - 🧸 Your favorite toy
        """)

else:
    # Parent Dashboard
    st.title("👨‍👩‍👧 Parent Dashboard")
    st.markdown("### Track what your child is exploring and learning")
    
    # Load log
    log = load_parent_log()
    sessions = log.get("sessions", [])
    
    if len(sessions) == 0:
        st.info("No learning sessions yet! Your child's discoveries will appear here.")
    else:
        # Stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Discoveries", len(sessions))
        
        with col2:
            unique_objects = len(set([s["object_detected"] for s in sessions]))
            st.metric("Unique Objects", unique_objects)
    
        
        st.markdown("---")
        
        # Recent sessions table
        st.markdown("### Recent Learning Sessions")
        
        # Display sessions in reverse chronological order
        for i, session in enumerate(reversed(sessions[-10:])):  # Show last 10
            with st.expander(
                f"🔍 {session['object_detected'].title()} - "
                f"{datetime.fromisoformat(session['timestamp']).strftime('%b %d, %I:%M %p')}"
            ):
                st.markdown(f"**Object:** {session['object_detected']}")
                st.markdown(f"**Time:** {session['timestamp']}")
                st.markdown(f"**Story Generated:**")
                st.info(session['story_generated'])
        
        # Download log
        st.markdown("---")
        if st.button("📥 Download Full Log"):
            st.download_button(
                label="Download JSON",
                data=json.dumps(log, indent=2),
                file_name=f"snap_learn_log_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )