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
st.set_page_config(
    page_title="EmpathyBot Pro+", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.emotion_history = []
    st.session_state.conversation_context = []
    st.session_state.eq_score = 50  # Emotional Quotient (50 = neutral)

# Emotional Quotient weights
EQ_WEIGHTS = {
    "happiness": 2, "joy": 2, "love": 3, "surprise": 1,
    "sadness": -1, "fear": -2, "anger": -3, "disgust": -2,
    "guilt": -1, "shame": -2, "anxiety": -2, "envy": -1,
    "frustration": -1, "neutral": 0
}

def update_eq_score(emotion):
    """Update Emotional Quotient score"""
    st.session_state.eq_score += EQ_WEIGHTS.get(emotion, 0)
    st.session_state.eq_score = max(0, min(100, st.session_state.eq_score))

def detect_emotion(text):
    """Detects emotion from text using OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"Classify the dominant emotion from: {', '.join(EMOTIONS)}. Return ONLY the emotion name."
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

def log_all_conversation(user_input):
    """Logs every user message verbatim with timestamp"""
    st.session_state.conversation_context.append(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - USER: {user_input}"
    )

def generate_response(user_input, emotion):
    """Generates response with full conversation context"""
    try:
        # Create full conversation history
        full_history = "\n".join(
            f"{m['time']} - {m['role'].upper()}: {m['content']}"
            for m in st.session_state.messages
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""You're an empathetic therapist with perfect memory. Rules:
1. FULL CONVERSATION HISTORY (chronological order):
{full_history}

2. Current emotion: {emotion}
3. Always reference relevant past exchanges"""
            }, {
                "role": "user",
                "content": user_input
            }],
            temperature=0.7,
            max_tokens=250
        )
        return response.choices[0].message.content
    except Exception:
        return "I appreciate you sharing. Could you tell me more?"

# Main layout
st.title("🧠 EmpathyBot Pro+ (Complete Memory Version)")
st.caption("Your AI Companion That Remembers Everything")

# Left sidebar - Full conversation log
with st.sidebar:
    st.header("Complete Memory Log")
    
    with st.expander(f"📜 Entire Conversation ({len(st.session_state.messages)} messages)"):
        if st.session_state.messages:
            for msg in st.session_state.messages:
                st.write(f"**{msg['time']} - {msg['role'].upper()}**")
                st.write(msg['content'])
                if msg["role"] == "user":
                    emoji = {
                        "happiness": "😊", "sadness": "😢", "fear": "😨",
                        "anger": "😠", "disgust": "🤢", "surprise": "😲",
                        "love": "❤️", "joy": "😂", "guilt": "😳",
                        "shame": "😞", "anxiety": "😰", "envy": "😒",
                        "frustration": "😤", "neutral": "😐"
                    }.get(msg.get("emotion", "neutral"), "❓")
                    st.caption(f"{emoji} {msg.get('emotion', 'neutral').capitalize()}")
        else:
            st.write("No messages yet")

# Right sidebar - Emotional analytics
with st.sidebar:
    st.header("Emotional Analytics")
    
    # Emotional Quotient
    st.subheader("EQ Tracker")
    eq_color = "#4CAF50" if st.session_state.eq_score >= 50 else "#F44336"
    st.metric("Current Score", f"{st.session_state.eq_score}/100", 
             delta=f"{st.session_state.eq_score-50:+d} from neutral")
    st.progress(st.session_state.eq_score/100)
    
    # Emotion pie chart
    if st.session_state.emotion_history:
        emotion_counts = pd.Series(st.session_state.emotion_history).value_counts()
        fig = px.pie(
            names=emotion_counts.index,
            values=emotion_counts.values,
            color=emotion_counts.index,
            color_discrete_map=EMOTION_COLORS,
            hole=0.4,
            height=250
        )
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, key=f"pie_chart_{len(st.session_state.emotion_history)}")

# Main chat interface
st.subheader("Therapy Session")
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

# Chat input handler
if prompt := st.chat_input("How are you feeling today?"):
    # Detect emotion and update systems
    emotion = detect_emotion(prompt)
    update_eq_score(emotion)
    log_all_conversation(prompt)
    
    # Store message with timestamp
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "emotion": emotion,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.session_state.emotion_history.append(emotion)
    
    # Generate and store response
    with st.spinner("Processing..."):
        response = generate_response(prompt, emotion)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    st.rerun()