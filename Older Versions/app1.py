import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv

# Initialize
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Emotion configuration
EMOTIONS = [
    "happiness", "sadness", "fear", "anger", "disgust",
    "surprise", "love", "joy", "guilt", "shame",
    "anxiety", "envy", "frustration", "neutral"
]
EMOTION_COLORS = {
    "happiness": "#FFD700", "sadness": "#1E90FF", "fear": "#9370DB",
    "anger": "#FF4500", "disgust": "#32CD32", "surprise": "#FFA500",
    "love": "#FF69B4", "joy": "#FFD700", "guilt": "#A9A9A9",
    "shame": "#8B0000", "anxiety": "#FF8C00", "envy": "#2E8B57",
    "frustration": "#CD5C5C", "neutral": "#D3D3D3"
}

# Setup UI
st.set_page_config(page_title="EmpathyBot Pro", layout="wide")
st.title("🧠 EmpathyBot Pro")
st.caption("Your AI Mental Health Companion")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.emotion_history = []
    st.session_state.eq_score = 50  # Starting Emotional Quotient

# Emotion scoring weights (positive emotions increase EQ, negative decrease)
EQ_WEIGHTS = {
    "happiness": 2, "joy": 2, "love": 3, "surprise": 1,
    "sadness": -1, "fear": -2, "anger": -3, "disgust": -2,
    "guilt": -1, "shame": -2, "anxiety": -2, "envy": -1,
    "frustration": -1, "neutral": 0
}

# Faster emotion detection
def detect_emotion(text):
    """Quick emotion classification with fallback"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""Classify the dominant emotion in this text as ONLY ONE from: {', '.join(EMOTIONS)}. 
                Return ONLY the lowercase emotion name."""
            }, {
                "role": "user",
                "content": text
            }],
            temperature=0.1,
            max_tokens=15
        )
        emotion = response.choices[0].message.content.lower().strip()
        return emotion if emotion in EMOTIONS else "neutral"
    except Exception:
        return "neutral"

# Therapist response with full context
def generate_response(user_input, emotion):
    """Context-aware empathetic responses"""
    try:
        # Build conversation history
        history = "\n".join(
            f"{m['time']} - {m['role'].capitalize()}: {m['content']}"
            for m in st.session_state.messages[-10:]  # Last 10 messages for context
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""You're an empathetic mental health guide. Rules:
1. First acknowledge the detected emotion ({emotion})
2. Maintain conversation context: {history}
3. Respond in 2-3 sentences max
4. Show unconditional positive regard
5. Ask thoughtful questions when appropriate"""
            }, {
                "role": "user",
                "content": user_input
            }],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception:
        return "I appreciate you sharing. Could you tell me more about how you're feeling?"

# Update Emotional Quotient
def update_eq_score(emotion):
    """Calculate rolling emotional quotient"""
    st.session_state.eq_score += EQ_WEIGHTS.get(emotion, 0)
    st.session_state.eq_score = max(0, min(100, st.session_state.eq_score))  # Clamp 0-100

# Sidebar - Emotion Tracking
with st.sidebar:
    st.header("Emotional Analysis")
    
    # Current EQ Score
    eq_color = "#4CAF50" if st.session_state.eq_score >= 50 else "#F44336"
    st.metric("Emotional Quotient", 
              f"{st.session_state.eq_score}/100",
              delta_color="off")
    st.progress(st.session_state.eq_score/100, text=None)
    
    # Emotion Distribution
    if st.session_state.emotion_history:
        emotion_counts = pd.Series(st.session_state.emotion_history).value_counts()
        st.subheader("Emotion Frequency")
        fig = px.pie(
            names=emotion_counts.index,
            values=emotion_counts.values,
            color=emotion_counts.index,
            color_discrete_map=EMOTION_COLORS
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Emotion Timeline
        st.subheader("Emotion Timeline")
        timeline_df = pd.DataFrame({
            "Time": [m["time"] for m in st.session_state.messages if m["role"] == "user"],
            "Emotion": st.session_state.emotion_history,
            "Intensity": [EQ_WEIGHTS[e] for e in st.session_state.emotion_history]
        })
        if not timeline_df.empty:
            st.line_chart(
                timeline_df.set_index("Time")["Intensity"],
                color="#FF4B4B"
            )

# Main Chat Interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        st.write(msg["content"])
        if msg["role"] == "user" and "emotion" in msg:
            emoji = {
                "happiness": "😊", "sadness": "😢", "fear": "😨",
                "anger": "😠", "disgust": "🤢", "surprise": "😲",
                "love": "❤️", "joy": "😂", "guilt": "😳",
                "shame": "😞", "anxiety": "😰", "envy": "😒",
                "frustration": "😤", "neutral": "😐"
            }.get(msg["emotion"], "❓")
            st.caption(f"{emoji} {msg['emotion'].capitalize()}")

# Chat input
if prompt := st.chat_input("How are you feeling today?"):
    # Detect emotion and update EQ
    emotion = detect_emotion(prompt)
    update_eq_score(emotion)
    
    # Store user message with timestamp
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "emotion": emotion,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    st.session_state.emotion_history.append(emotion)
    
    # Generate and display response
    with st.spinner("Thinking..."):
        response = generate_response(prompt, emotion)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M:%S")
        })
    
    # Rerun to update all visualizations
    st.rerun()