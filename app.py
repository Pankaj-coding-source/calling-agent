import os
import time
import subprocess
import database as db
import ml_engine as ml
import voice_bridge as vb
from deep_translator import GoogleTranslator
import sys

# --- CONFIGURATION ---
DEFAULT_LANG = "hi"       
DEFAULT_NAME = "Kisan Bhai" 
CHECK_INTERVAL = 1 # Fast checking for presentation

def wait_for_incoming_call():
    print("\n" + "="*60)
    print("🌾 SANJAY AI: MULTILINGUAL FARMING HELPLINE 🌾")
    print("="*60)
    print("[STATUS]: System is LIVE. Waiting for farmer's call...")

    while True:
        try:
            # Detect Ringing state (1)
            raw_dump = subprocess.check_output("adb shell dumpsys telephony.registry", shell=True).decode('utf-8')
            
            if "mCallState=1" in raw_dump or "CallState: 1" in raw_dump:
                print("\n🔔 [INCOMING CALL DETECTED!]")
                
                # 1. BRUTE FORCE WAKE & UNLOCK
                os.system("adb shell input keyevent KEYCODE_WAKEUP")
                os.system("adb shell input keyevent 82") # Unlock bypass
                time.sleep(0.5)

                # 2. BRUTE FORCE ANSWER (Try 3 methods simultaneously)
                print("--> Forcing Call Answer...")
                # Method A: Swipe UP (Common for modern Android)
                os.system("adb shell input swipe 500 1500 500 800 300")
                # Method B: Headset Hook (Simulates earphone button)
                os.system("adb shell input keyevent 79")
                # Method C: Standard Answer Key
                os.system("adb shell input keyevent 5")

                time.sleep(4) # WAIT for connection stability

                # 3. RETRIEVE CALLER NUMBER
                caller_num = "Unknown"
                for line in raw_dump.splitlines():
                    if "mCallIncomingNumber=" in line:
                        caller_num = line.split("=")[1].strip()
                        break
                
                print(f"--> Connected with: {caller_num}")

                # 4. ACTIVATE SPEAKERPHONE
                print("--> Activating Speakerphone...")
                os.system("adb shell input keyevent KEYCODE_SPEAKERPHONE")
                time.sleep(1)
                
                # 5. START AI ENGINE
                run_sanjay_logic(caller_num)
                
                print("\n[STATUS]: Call ended. Sanjay is back in monitoring mode...")

            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            # Silent fail for presentation stability
            time.sleep(1)

def run_sanjay_logic(caller_phone):
    """
    Core AI logic: Search 1.7 Lakh records and talk back.
    """
    # 1. Database Lookup
    farmer = db.get_farmer_by_phone(caller_phone)
    if not farmer:
        name, lang_code = DEFAULT_NAME, DEFAULT_LANG
    else:
        name, lang_code = farmer['name'], farmer['language_code']

    # 2. Greeting
    greet_en = f"Hello {name}, I am Sanjay AI. How can I help you today?"
    try:
        greet_local = GoogleTranslator(source='en', target=lang_code).translate(greet_en)
    except:
        greet_local = greet_en
        
    vb.speak(greet_local, lang_code=lang_code)

    # 3. Talk-back Loop
    retry_count = 0
    max_retries = 3 # Don't hang up too easily during demo
    
    while True:
        sr_lang = f"{lang_code}-IN" if lang_code != 'en' else 'en-IN'
        
        # AI listens to phone speaker through laptop mic
        farmer_speech = vb.listen(lang_code=sr_lang)
        
        if not farmer_speech:
            retry_count += 1
            if retry_count >= max_retries:
                vb.speak(GoogleTranslator(source='en', target=lang_code).translate("I cannot hear you. Goodbye."), lang_code)
                break
            continue

        retry_count = 0 # Reset

        # Exit phrases
        if any(w in farmer_speech.lower() for w in ['bye', 'thank', 'dhanyawad', 'shukriya', 'exit', 'bas']):
            closing = GoogleTranslator(source='en', target=lang_code).translate("Thank you. Happy farming!")
            vb.speak(closing, lang_code=lang_code)
            break

        # 4. AI Search (FAISS 1.7 Lakh Rows)
        try:
            # Translate input
            query_en = GoogleTranslator(source=lang_code, target='en').translate(farmer_speech)
            print(f"[TRANS]: {farmer_speech} -> {query_en}")

            # Sentiment & Solution retrieval
            sentiment = vb.analyze_sentiment(query_en)
            _, expert_solution_en = ml.get_intent_and_solution(query_en)
            
            # Formulate response
            prefix = "Don't worry. " if sentiment == "urgent" else ""
            final_en = f"{prefix} {expert_solution_en} . Do you have more questions?"
            
            # Speak back in local language
            final_local = GoogleTranslator(source='en', target=lang_code).translate(final_en)
            vb.speak(final_local, lang_code=lang_code)

        except Exception as e:
            print(f"Error in Logic: {e}")
            break

    # 5. HANG UP via ADB
    print("--> Closing Call...")
    os.system("adb shell input keyevent 6")

if __name__ == "__main__":
    db.init_db()
    wait_for_incoming_call()