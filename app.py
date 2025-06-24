import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Initialize
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Emotion list (13 emotions as requested)
EMOTIONS = [
    "happiness", "sadness", "fear", "anger", "disgust", 
    "surprise", "love", "joy", "guilt", "shame", 
    "anxiety", "envy", "frustration"
]

# Simple UI
st.title("🤝 EmpathyBot")
st.caption("Your compassionate mental guide")

# Initialize session
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.emotion_history = []

# Display chat
for msg in st.session_state.messages:
    avatar = "😊" if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])
        if msg["role"] == "user" and "emotion" in msg:
            st.caption(f"Detected: {msg['emotion']}")

# Faster emotion detection (single API call)
def detect_emotion(text):
    """Quick emotion classification"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Faster than GPT-4
            messages=[{
                "role": "system",
                "content": f"""Classify the emotion in this text as ONLY ONE from: {', '.join(EMOTIONS)}. 
                Return ONLY the emotion name."""
            }, {
                "role": "user",
                "content": text
            }],
            temperature=0.1,
            max_tokens=10
        )
        return response.choices[0].message.content.lower()
    except Exception:
        return "neutral"

# Therapist response generator
def generate_response(user_input, emotion, history):
    """Fast empathetic responses"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""You're an empathetic mental health guide. Follow these rules:
                1. Respond to the emotion ({emotion}) first
                2. Be concise (1-2 sentences)
                3. Show unconditional positive regard
                4. Ask open-ended questions when appropriate
                
                Conversation history: {history[-3:] if history else 'None'}"""
            }, {
                "role": "user",
                "content": user_input
            }],
            temperature=0.7,
            max_tokens=150  # Shorter = faster
        )
        return response.choices[0].message.content
    except Exception:
        return "I appreciate you sharing. Could you tell me more?"

# Chat input
if prompt := st.chat_input("How are you feeling today?"):
    # User message with emotion
    emotion = detect_emotion(prompt)
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "emotion": emotion,
        "time": datetime.now().strftime("%H:%M")
    })
    st.session_state.emotion_history.append(emotion)
    
    # Generate and display response
    with st.spinner("Thinking..."):
        history = [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
        response = generate_response(prompt, emotion, history)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M")
        })
    
    # Rerun to update UI
    st.rerun()

# Simple emotion tracking (shown only when expanded)
with st.expander("📈 Emotion Tracker (Click to See)"):
    if st.session_state.emotion_history:
        st.write("Recent Emotions:")
        cols = st.columns(4)
        for i, emo in enumerate(st.session_state.emotion_history[-8:]):
            cols[i%4].metric(f"Msg {i+1}", emo.capitalize())