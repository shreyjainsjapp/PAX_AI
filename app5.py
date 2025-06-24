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
st.set_page_config(page_title="EmpathyBot Ultimate", layout="wide")
st.title("🧠 EmpathyBot Ultimate")
st.caption("Never Forgets | Always Understands")

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
    st.session_state.eq_score += EQ_WEIGHTS.get(emotion, 0)
    st.session_state.eq_score = max(0, min(100, st.session_state.eq_score))
    st.session_state.emotion_counts[emotion] += 1

# Enhanced fact extraction - captures EVERY important detail
def extract_important_facts(user_input):
    """Extract and store ALL important facts permanently"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": """Extract ALL important factual information from this message.
                Return as bullet points. Include:
                - Personal details (names, relationships)
                - Important events (exams, meetings)
                - Emotional triggers
                - Key preferences"""
            }, {
                "role": "user",
                "content": user_input
            }],
            temperature=0.2,
            max_tokens=150
        )
        facts = response.choices[0].message.content.split("\n")
        for fact in facts:
            if fact.strip() and not any(fact.lower() in c.lower() for c in st.session_state.conversation_context):
                st.session_state.conversation_context.append(fact.strip())
    except Exception:
        pass

# Emotion detection
def detect_emotion(text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"Classify emotion from: {', '.join(EMOTIONS)}. Return ONLY the emotion name."
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

# Response generation with perfect memory recall
def generate_response(user_input, emotion):
    try:
        # Prepare context from ALL remembered facts
        context = "Remembered Facts:\n" + "\n".join(
            f"• {fact}" for fact in st.session_state.conversation_context
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""You remember EVERYTHING. Rules:
1. Always reference relevant facts
2. Current emotion: {emotion}
3. Context:
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
        return "Let me think differently about that..."

# Layout - Two columns with persistent displays
col1, col2 = st.columns([3, 1])  # Wider conversation column

with col1:
    # Chat interface
    st.subheader("Conversation")
    for msg in st.session_state.messages:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])
            if msg["role"] == "user" and "emotion" in msg:
                st.caption(f"Detected: {msg['emotion'].capitalize()}")

with col2:
    # Permanent compact analytics panel
    st.header("Emotional Health")
    
    # EQ Score
    st.metric("EQ Score", f"{st.session_state.eq_score}/100")
    st.progress(st.session_state.eq_score/100)
    
    # Mini pie chart (always visible)
    if sum(st.session_state.emotion_counts.values()) > 0:
        emotion_df = pd.DataFrame({
            "Emotion": list(st.session_state.emotion_counts.keys()),
            "Count": list(st.session_state.emotion_counts.values())
        })
        fig = px.pie(
            emotion_df,
            names="Emotion",
            values="Count",
            color="Emotion",
            color_discrete_map=EMOTION_COLORS,
            hole=0.5,
            height=250,  # Compact size
            width=300
        )
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    
    # Facts count
    st.caption(f"Remembering {len(st.session_state.conversation_context)} facts")

# Left sidebar - Complete memory
with st.sidebar:
    st.header("Perfect Memory")
    
    # All remembered facts (scrollable)
    with st.expander(f"All Facts ({len(st.session_state.conversation_context)})"):
        if st.session_state.conversation_context:
            for i, fact in enumerate(st.session_state.conversation_context, 1):
                st.markdown(f"{i}. {fact}")
        else:
            st.write("No facts yet")
    
    # Emotion frequency
    st.subheader("Emotion Counts")
    for emotion, count in sorted(st.session_state.emotion_counts.items(), key=lambda x: -x[1]):
        if count > 0:
            st.metric(emotion.capitalize(), count)

# Chat input
if prompt := st.chat_input("How are you feeling today?"):
    # Process message
    emotion = detect_emotion(prompt)
    update_eq_score(emotion)
    extract_important_facts(prompt)  # Capture ALL important facts
    
    # Store message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "emotion": emotion,
        "time": datetime.now().strftime("%H:%M")
    })
    
    # Generate response
    with st.spinner("Understanding..."):
        response = generate_response(prompt, emotion)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M")
        })
    
    st.rerun()