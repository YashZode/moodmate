# MoodMate: Your Emotion-Powered AI Buddy
# ----------------------------------------
# This is a complete beginner-friendly project for a 4-hour ML hackathon.
# Participants build an app that takes user emotion input and responds with
# a motivational quote or meme and mood-based music using a sentiment analysis model.

# 1. Install dependencies (run in terminal or requirements.txt)
# pip install streamlit textblob requests

# 2. Create main app: moodmate_app.py

import streamlit as st
from textblob import TextBlob
import requests

# Function to predict sentiment
def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "positive"
    elif polarity < -0.1:
        return "negative"
    else:
        return "neutral"

# Function to get a motivational quote
def get_quote():
    try:
        res = requests.get("https://api.quotable.io/random")
        data = res.json()
        return f"\"{data['content']}\" - {data['author']}"
    except:
        return "Stay strong. Better days are coming!"

# Function to get a meme (funny image)
def get_meme():
    try:
        res = requests.get("https://meme-api.com/gimme")
        data = res.json()
        return data["url"]
    except:
        return None

# Function to get Spotify playlist by mood
def get_playlist_embed(mood):
    playlists = {
        "positive": "https://open.spotify.com/embed/playlist/37i9dQZF1DXdPec7aLTmlC",
        "neutral": "https://open.spotify.com/embed/playlist/37i9dQZF1DWU0ScTcjJBdj",
        "negative": "https://open.spotify.com/embed/playlist/37i9dQZF1DX3rxVfibe1L0"
    }
    return playlists.get(mood, playlists["neutral"])

# Streamlit UI
st.set_page_config(page_title="MoodMate AI Buddy")
st.title("🧠 MoodMate - Your Emotion-Powered AI Buddy")
st.markdown("Enter how you're feeling and let MoodMate cheer you up or celebrate with you!")

user_input = st.text_input("How are you feeling today?", "I'm feeling great!")

if st.button("Tell me something cool"):
    sentiment = get_sentiment(user_input)
    st.write(f"**Detected Mood:** {sentiment.capitalize()}")

    if sentiment == "positive":
        st.success("That's awesome! Here's something to keep the good vibes going:")
        st.write(get_quote())
    elif sentiment == "negative":
        st.warning("It's okay to feel down sometimes. Here's a little something for you:")
        meme_url = get_meme()
        if meme_url:
            st.image(meme_url)
        st.write(get_quote())
    else:
        st.info("Feeling neutral? Here's a quote to inspire you:")
        st.write(get_quote())

    # Music player based on mood
    playlist_url = get_playlist_embed(sentiment)
    st.markdown("**Here's a playlist for your mood 🎵**", unsafe_allow_html=True)
    st.components.v1.iframe(playlist_url, height=380)
