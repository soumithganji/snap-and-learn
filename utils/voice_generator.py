from gtts import gTTS
import os
import hashlib

def text_to_speech(text, object_name):
    """
    Convert text to speech using gTTS (Google Text-to-Speech)
    
    Args:
        text: string text to convert
        object_name: string name of object (for filename)
    
    Returns:
        string: path to generated audio file
    """
    try:
        # Create audio directory if it doesn't exist
        os.makedirs("audio", exist_ok=True)
        
        # Create unique filename based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        filename = f"audio/{object_name}_{text_hash}.mp3"
        
        # Check if file already exists (cache)
        if os.path.exists(filename):
            return filename
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        
        return filename
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def cleanup_old_audio_files(max_files=50):
    """
    Clean up old audio files to save space
    Keeps only the most recent max_files
    """
    try:
        audio_dir = "audio"
        if not os.path.exists(audio_dir):
            return
        
        # Get all audio files
        files = [
            os.path.join(audio_dir, f) 
            for f in os.listdir(audio_dir) 
            if f.endswith('.mp3')
        ]
        
        # Sort by modification time
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Delete old files
        for f in files[max_files:]:
            try:
                os.remove(f)
            except:
                pass
                
    except Exception as e:
        print(f"Cleanup error: {e}")