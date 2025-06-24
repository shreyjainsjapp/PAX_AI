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

# Setup UI
st.set_page_config(page_title="EmpathyBot Pro+", layout="wide")
st.title("🧠 EmpathyBot Pro+")
st.caption("Your AI Mental Health Companion With Perfect Memory")

# Initialize session state with conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.emotion_history = []
    st.session_state.eq_score = 50
    st.session_state.conversation_context = []  # New: Stores key facts

# Enhanced emotion detection with context awareness
def detect_emotion(text):
    """More accurate emotion classification"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""Analyze this message considering the full conversation context:
                {st.session_state.conversation_context[-3:] if st.session_state.conversation_context else 'No context yet'}
                
                Classify the dominant emotion as ONLY ONE from: {', '.join(EMOTIONS)}. 
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

# New: Fact extraction function
def extract_important_facts(user_input):
    """Identify and store key information from user messages"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": """Extract key factual information from this message that might be important to remember later. 
                Return as a concise bullet point. If nothing important, return None."""
            }, {
                "role": "user",
                "content": user_input
            }],
            temperature=0.3,
            max_tokens=50
        )
        fact = response.choices[0].message.content
        if fact and fact.lower() != "none":
            st.session_state.conversation_context.append(fact)
    except Exception:
        pass

# Enhanced therapist response with perfect memory
def generate_response(user_input, emotion):
    """Response using complete conversation history"""
    try:
        # Build detailed conversation history
        history = "\n".join(
            f"Message {i+1}: {m['role'].capitalize()} at {m['time']}: {m['content']}"
            for i, m in enumerate(st.session_state.messages)
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""You're an empathetic therapist with perfect memory. Rules:
1. Remember ALL these key facts: {st.session_state.conversation_context}
2. Full conversation history: {history}
3. Current emotion: {emotion}
4. Always acknowledge important past details
5. Respond in 2-3 sentences"""
            }, {
                "role": "user",
                "content": user_input
            }],
            temperature=0.7,
            max_tokens=250  # Slightly more for detailed responses
        )
        return response.choices[0].message.content
    except Exception:
        return "I appreciate you sharing. Could you tell me more about how you're feeling?"

# Sidebar - Enhanced Memory Display
with st.sidebar:
    st.header("Conversation Memory")
    
    # Show remembered facts
    if st.session_state.conversation_context:
        st.subheader("Key Facts Remembered")
        for i, fact in enumerate(st.session_state.conversation_context[-5:]):  # Show last 5 facts
            st.markdown(f"• {fact}")
    else:
        st.write("No key facts remembered yet")
    
    # Emotion tracking (kept from previous version)
    if st.session_state.emotion_history:
        st.subheader("Recent Emotions")
        emotion_counts = pd.Series(st.session_state.emotion_history[-10:]).value_counts()
        st.dataframe(emotion_counts, use_container_width=True)

# Main Chat Interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        st.write(msg["content"])
        if msg["role"] == "user" and "emotion" in msg:
            st.caption(f"Detected emotion: {msg['emotion'].capitalize()}")

# Chat input with perfect memory
if prompt := st.chat_input("How are you feeling today?"):
    # Detect emotion and extract facts
    emotion = detect_emotion(prompt)
    extract_important_facts(prompt)  # New: Extract and store key facts
    
    # Store message with timestamp
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "emotion": emotion,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    st.session_state.emotion_history.append(emotion)
    
    # Generate and display response
    with st.spinner("Thinking with full context..."):
        response = generate_response(prompt, emotion)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M:%S")
        })
    
    st.rerun()