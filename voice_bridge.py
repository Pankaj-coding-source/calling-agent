import os
import asyncio
import edge_tts
import pygame
import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time
import io

# Initialize AI Components
analyzer = SentimentIntensityAnalyzer()
if not pygame.mixer.get_init():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

def speak(text, lang_code='hi'):
    """
    Sanjay's Narration: Downloads the high-quality voice and plays it 
    through laptop speakers so the phone can hear it.
    """
    if not text or not text.strip():
        return

    print(f"[SANJAY]: {text}")
    
    voice_map = {
        'hi': 'hi-IN-SwaraNeural',
        'or': 'or-IN-SubhasiniNeural', 
        'en': 'en-IN-NeerjaNeural'
    }
    
    selected_voice = voice_map.get(lang_code, 'hi-IN-SwaraNeural')
    temp_file = f"sanjay_voice_{int(time.time())}.mp3"

    async def save_audio():
        try:
            communicate = edge_tts.Communicate(text, selected_voice)
            await communicate.save(temp_file)
            return True
        except Exception as e:
            print(f"❌ Voice Download Error: {e}")
            return False

    try:
        # Step 1: Download the audio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(save_audio())
        loop.close()

        # Step 2: Play through laptop speakers
        if success and os.path.exists(temp_file):
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
            
            # Step 3: Cleanup
            try: os.remove(temp_file)
            except: pass
    except Exception as e:
        print(f"❌ Playback Error: {e}")

def listen(lang_code='hi-IN'):
    """
    Sanjay's Ear: Listens through the laptop microphone (Index 1).
    Adjusts for exhibition room noise.
    """
    r = sr.Recognizer()
    
    # Based on your find_mic.py: Index 1 is the AMD Microphone Array
    TARGET_MIC_INDEX = 1 

    try:
        with sr.Microphone(device_index=TARGET_MIC_INDEX) as source:
            print(f"🎤 Sanjay is listening through the air ({lang_code})...")
            
            # 1. NOISE CANCELLATION: Listen to room noise for 1 sec and filter it
            r.adjust_for_ambient_noise(source, duration=1)
            
            # 2. SENSITIVITY: Ignore low background noise
            r.energy_threshold = 800  
            r.dynamic_energy_threshold = True

            audio = r.listen(source, timeout=6, phrase_time_limit=10)
            
            print("⏳ Interpreting...")
            text = r.recognize_google(audio, language=lang_code)
            print(f"[FARMER]: {text}")
            return text
    except Exception as e:
        return ""

def analyze_sentiment(text):
    score = analyzer.polarity_scores(text)
    return "urgent" if score['compound'] < -0.1 else "normal"
