import os
import asyncio
import edge_tts
import pygame
import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time

# Initialize
analyzer = SentimentIntensityAnalyzer()
if not pygame.mixer.get_init():
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

def speak(text, lang_code='hi'):
    """
    Stable Microsoft Neural TTS. Downloads fully before playing 
    to prevent 'No audio received' errors.
    """
    if not text or not text.strip():
        return

    print(f"[AI]: {text}")
    
    # Map to professional Neural voices
    voice_map = {
        'hi': 'hi-IN-SwaraNeural',
        'or': 'or-IN-SubhasiniNeural', 
        'en': 'en-IN-NeerjaNeural'
    }
    
    selected_voice = voice_map.get(lang_code, 'hi-IN-SwaraNeural')
    # Unique filename to avoid permission conflicts
    temp_file = f"voice_temp_{int(time.time())}.mp3"

    async def download_audio():
        try:
            communicate = edge_tts.Communicate(text, selected_voice)
            await communicate.save(temp_file)
            return True
        except Exception as e:
            print(f"❌ Voice Download Error: {e}")
            return False

    try:
        # Step 1: Download
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(download_audio())
        loop.close()

        # Step 2: Play
        if success and os.path.exists(temp_file):
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
            
            # Step 3: Delete temp file
            try:
                os.remove(temp_file)
            except:
                pass
    except Exception as e:
        print(f"❌ Playback Error: {e}")

def listen(lang_code='hi-IN'):
    """Listens with high noise threshold for phone calls"""
    r = sr.Recognizer()
    r.energy_threshold = 600 # Filter background noise
    r.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        print(f"🎤 Listening ({lang_code})...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            text = r.recognize_google(audio, language=lang_code)
            print(f"[Farmer]: {text}")
            return text
        except:
            return ""

def analyze_sentiment(text):
    score = analyzer.polarity_scores(text)
    return "urgent" if score['compound'] < -0.1 else "normal"