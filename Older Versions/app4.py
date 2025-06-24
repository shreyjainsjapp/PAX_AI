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
st.set_page_config(page_title="EmpathyBot Pro", layout="wide", initial_sidebar_state="expanded")
st.title("🧠 EmpathyBot Pro")
st.caption("Your AI Companion With Perfect Memory")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.emotion_history = []
    st.session_state.conversation_context = []
    st.session_state.eq_score = 50
    st.session_state.emotion_counts = {e: 0 for e in EMOTIONS}

# Emotional Quotient weights
EQ_WEIGHTS = {
    "happiness": 2, "joy": 2, "love": 3, "surprise": 1,
    "sadness": -1, "fear": -2, "anger": -3, "disgust": -2,
    "guilt": -1, "shame": -2, "anxiety": -2, "envy": -1,
    "frustration": -1, "neutral": 0
}

def update_eq_score(emotion):
    """Update EQ score and emotion counts"""
    st.session_state.eq_score += EQ_WEIGHTS.get(emotion, 0)
    st.session_state.eq_score = max(0, min(100, st.session_state.eq_score))
    st.session_state.emotion_counts[emotion] += 1

# Enhanced emotion detection
def detect_emotion(text):
    """More accurate emotion classification with context"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""Classify the dominant emotion from: {', '.join(EMOTIONS)}. 
                Consider this context: {st.session_state.conversation_context[-3:] if st.session_state.conversation_context else 'No context yet'}
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

# Permanent fact extraction
def extract_important_facts(user_input):
    """Store facts permanently with duplicate prevention"""
    try:
        existing_context = "\n".join(st.session_state.conversation_context)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""Extract NEW important information not already in:
                {existing_context}
                Return ONLY the fact or None"""
            }, {
                "role": "user",
                "content": user_input
            }],
            temperature=0.3,
            max_tokens=100
        )
        fact = response.choices[0].message.content
        if fact and fact.lower() != "none":
            # Check for similar existing facts
            if not any(fact.lower() in c.lower() for c in st.session_state.conversation_context):
                st.session_state.conversation_context.append(fact)
    except Exception:
        pass

# Response generation with perfect memory
def generate_response(user_input, emotion):
    """Uses entire conversation history"""
    try:
        # Prepare context - all facts + recent messages
        context = "KNOWS THESE FACTS:\n- " + "\n- ".join(
            st.session_state.conversation_context[-10:] + 
            [f"...plus {len(st.session_state.conversation_context)-10} more facts"]
            if len(st.session_state.conversation_context) > 10 
            else st.session_state.conversation_context
        )
        
        history = "\n".join(
            f"{m['time']} - {m['role'].capitalize()}: {m['content']}"
            for m in st.session_state.messages[-5:]
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""You're an empathetic therapist with perfect memory. Rules:
1. Always reference relevant facts when appropriate
2. Current emotion: {emotion}
3. Conversation history:
{history}
4. Important context:
{context}"""
            }, {
                "role": "user",
                "content": user_input
            }],
            temperature=0.7,
            max_tokens=250
        )
        return response.choices[0].message.content
    except Exception:
        return "I appreciate you sharing. Could you elaborate?"

# Layout - Two columns
col1, col2 = st.columns([3, 2])

with col1:
    # Chat interface
    st.subheader("Conversation")
    for msg in st.session_state.messages:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
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

    # Left sidebar - Memory and emotion counts
    with st.sidebar:
        st.header("Memory Panel")
        
        # Remembered facts (scrollable)
        with st.expander(f"🧠 Facts Remembered ({len(st.session_state.conversation_context)})"):
            if st.session_state.conversation_context:
                for i, fact in enumerate(st.session_state.conversation_context, 1):
                    st.markdown(f"{i}. {fact}")
            else:
                st.write("No facts yet")
        
        # Emotion counts table
        st.subheader("Emotion Frequency")
        emotion_df = pd.DataFrame.from_dict(
            st.session_state.emotion_counts, 
            orient="index", 
            columns=["Count"]
        ).sort_values("Count", ascending=False)
        st.dataframe(emotion_df, use_container_width=True)

with col2:
    # Right panel - Emotional analytics
    st.header("Emotional Analytics")
    
    # EQ Score
    eq_color = "green" if st.session_state.eq_score >= 50 else "red"
    st.metric("Emotional Quotient", 
             f"{st.session_state.eq_score}/100",
             delta=f"{st.session_state.eq_score-50:+d} from neutral")
    st.progress(st.session_state.eq_score/100)
    
    # Emotion distribution pie chart
    if sum(st.session_state.emotion_counts.values()) > 0:
        st.subheader("Emotion Distribution")
        fig = px.pie(
            names=list(st.session_state.emotion_counts.keys()),
            values=list(st.session_state.emotion_counts.values()),
            color=list(st.session_state.emotion_counts.keys()),
            color_discrete_map=EMOTION_COLORS,
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No emotion data yet")

# Chat input
if prompt := st.chat_input("How are you feeling today?"):
    # Detect emotion and update tracking
    emotion = detect_emotion(prompt)
    update_eq_score(emotion)
    extract_important_facts(prompt)
    
    # Store message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "emotion": emotion,
        "time": datetime.now().strftime("%H:%M:%S")
    })
    
    # Generate response
    with st.spinner("Responding..."):
        response = generate_response(prompt, emotion)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M:%S")
        })
    
    st.rerun()