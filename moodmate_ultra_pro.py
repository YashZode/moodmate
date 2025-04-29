# moodmate_ultra_pro_final_side_by_side.py

import streamlit as st
import cv2
import time
import tempfile
import numpy as np
import threading
import speech_recognition as sr
import openai
from deepface import DeepFace
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

# Set OpenAI API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Globals
recorded_text = ""
live_emotions = []

emoji_map = {
    'happy': '😄',
    'sad': '😢',
    'neutral': '😐',
    'angry': '😡',
    'fear': '😨',
    'surprise': '😲',
    'disgust': '🤢'
}

mood_levels = {
    'sad': 1,
    'neutral': 2,
    'happy': 3
}

def record_voice_background(duration=10):
    global recorded_text
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        st.info("🎤 Listening... Please speak during 10 seconds...")
        audio = recognizer.listen(source, phrase_time_limit=duration)

    try:
        recorded_text = recognizer.recognize_google(audio)
    except Exception as e:
        recorded_text = ""
        st.error(f"Voice recognition error: {e}")

def detect_face_emotion(frame):
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        cv2.imwrite(temp_file.name, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        temp_file.close()

        result = DeepFace.analyze(img_path=temp_file.name, actions=['emotion'], enforce_detection=False)
        os.remove(temp_file.name)
        dominant_emotion = result[0]['dominant_emotion'].lower()
        return dominant_emotion
    except Exception as e:
        st.error(f"Face detection error: {e}")
        return "neutral"

def detect_voice_emotion(text):
    if not text.strip():
        return "neutral"

    try:
        response = openai.ChatCompletion.create(
            model="o4-mini",
            messages=[
                {"role": "system", "content": "Classify the user's mood as positive, negative, or neutral."},
                {"role": "user", "content": text}
            ]
        )
        mood = response['choices'][0]['message']['content'].strip().lower()

        if "positive" in mood:
            return "happy"
        elif "negative" in mood:
            return "sad"
        else:
            return "neutral"
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return "neutral"

def save_mood_diary(mood):
    now = datetime.now()
    data = {'Date': [now.strftime("%Y-%m-%d")], 'Time': [now.strftime("%H:%M:%S")], 'Mood': [mood]}
    df = pd.DataFrame(data)
    if os.path.exists('mood_diary.csv'):
        df.to_csv('mood_diary.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('mood_diary.csv', index=False)

def generate_compliment():
    compliments = [
        "You're shining bright! 🌟",
        "You inspire those around you! ✨",
        "You have unstoppable energy! 🚀",
        "You are a ray of sunshine! 🌞",
        "You are stronger than any storm! 💪"
    ]
    return np.random.choice(compliments)

# ========================
# Streamlit App Starts
# ========================

st.set_page_config(page_title="🧠 MoodMate Ultra Pro (Side-by-Side)", layout="wide")
st.title("🧠 MoodMate Ultra Pro - Live Video + Live Mood Graph")

st.info("📸 Look into the camera and speak freely for 10 seconds...")

# Start background voice thread
mic_thread = threading.Thread(target=record_voice_background, args=(10,))
mic_thread.start()

# Create two columns
col1, col2 = st.columns(2)

with col1:
    FRAME_WINDOW = st.image([])

with col2:
    MOOD_GRAPH = st.empty()

# Start webcam live
cap = cv2.VideoCapture(0)

start_time = time.time()

while time.time() - start_time < 10:
    ret, frame = cap.read()
    if not ret:
        continue
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mood_now = detect_face_emotion(frame_rgb)
    live_emotions.append(mood_now)

    # Left side: Live video + emoji
    mood_emoji = emoji_map.get(mood_now, "😐")
    FRAME_WINDOW.image(frame_rgb, caption=f"Detected Mood: {mood_now.capitalize()} {mood_emoji}")

    # Right side: Live updating mood graph
    mood_numeric = [mood_levels.get(m, 2) for m in live_emotions]
    fig, ax = plt.subplots()
    ax.plot(mood_numeric, marker='o', linestyle='-')
    ax.set_ylim(0.5, 3.5)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(['Sad', 'Neutral', 'Happy'])
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Mood Level')
    ax.set_title('Live Mood Trend')
    MOOD_GRAPH.pyplot(fig)

cap.release()
mic_thread.join()

# ========================
# Final Analysis
# ========================

# Decide final mood
if live_emotions:
    final_face_mood = max(set(live_emotions), key=live_emotions.count)
else:
    final_face_mood = "neutral"

voice_mood = detect_voice_emotion(recorded_text)

final_mood = final_face_mood if final_face_mood != "neutral" else voice_mood

save_mood_diary(final_mood)

st.success(f"**Final Detected Mood:** {final_mood.capitalize()} {emoji_map.get(final_mood, '')}")

# 💬 Motivational Quote
prompt = f"Give me a short motivational quote for someone feeling {final_mood}."
try:
    response = openai.ChatCompletion.create(
        model="o4-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    quote = response['choices'][0]['message']['content'].strip()
except Exception:
    quote = "Stay strong. Better days are coming."

st.markdown(f"**💬 Motivational Quote:** _{quote}_")

# ✨ Surprise Compliment
st.markdown(f"**✨ Compliment:** {generate_compliment()}")

# 🎵 Playlist
playlists = {
    "happy": "https://open.spotify.com/embed/playlist/37i9dQZF1DXdPec7aLTmlC",
    "neutral": "https://open.spotify.com/embed/playlist/37i9dQZF1DWU0ScTcjJBdj",
    "sad": "https://open.spotify.com/embed/playlist/37i9dQZF1DX3rxVfibe1L0"
}
playlist_url = playlists.get(final_mood, playlists["neutral"])

st.markdown("## 🎵 Music for your Mood")
st.components.v1.iframe(playlist_url, height=380)
