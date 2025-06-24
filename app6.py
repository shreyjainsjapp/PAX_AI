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
st.set_page_config(page_title="EmpathyBot Pro+", layout="wide")
st.title("🧠 EmpathyBot Pro+")
st.caption("Your Complete AI Mental Health Companion")

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
    st.session_state.eq_score = max(0, min(100, st.session_state.eq_score))  # Clamp between 0-100

# Emotion detection (unchanged)
def detect_emotion(text):
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

# Fact extraction (unchanged)
def extract_important_facts(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "Extract key factual information to remember. Return as bullet point or None."
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

# Response generation (unchanged)
# In the response generation function - change this part:
def generate_response(user_input, emotion):
    try:
        history = "\n".join(
            f"{m['role'].capitalize()}: {m['content']}"
            for m in st.session_state.messages[-10:]
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""You're an empathetic therapist. Rules:
1. Remember ALL these facts: {st.session_state.conversation_context}  # Changed from [-5:] to full list
2. Conversation history: {history}
3. Current emotion: {emotion}
4. Respond in 2-3 sentences"""
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

# Replace the entire layout section with this:
st.set_page_config(page_title="EmpathyBot Pro+", layout="wide", initial_sidebar_state="expanded")

# Main layout columns
col_chat, col_right = st.columns([4, 1])  # Wider chat area

with col_chat:
    # Chat interface (unchanged)
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

with col_right:
    # Emotional Quotient - Top Right
    st.subheader("Emotional Health")
    eq_color = "#4CAF50" if st.session_state.eq_score >= 50 else "#F44336"
    st.metric("EQ Score", f"{st.session_state.eq_score}/100", 
             delta=f"{st.session_state.eq_score-50:+d} from neutral")
    st.progress(st.session_state.eq_score/100)
    
    # Mini pie chart
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
        st.plotly_chart(fig, use_container_width=True)

# Left sidebar for memory
with st.sidebar:
    st.header("Conversation Memory")
    
    # All remembered facts
    with st.expander(f"🧠 Facts Remembered ({len(st.session_state.conversation_context)})"):
        if st.session_state.conversation_context:
            for i, fact in enumerate(st.session_state.conversation_context, 1):
                st.markdown(f"{i}. {fact}")
        else:
            st.write("No facts yet")
    
    # Emotion counts
    if st.session_state.emotion_history:
        st.subheader("Emotion Frequency")
        emotion_df = pd.Series(st.session_state.emotion_history).value_counts().reset_index()
        emotion_df.columns = ['Emotion', 'Count']
        st.dataframe(emotion_df, hide_index=True, use_container_width=True)
    

with st.sidebar:  # Moved to sidebar
    st.header("Memory & Analytics")
    with st.expander(f"💡 Remembered Facts ({len(st.session_state.conversation_context)})"):
        if st.session_state.conversation_context:
            for fact in st.session_state.conversation_context:  # Show all facts, not just last 5
                st.markdown(f"- {fact}")
        else:
            st.write("No facts remembered yet")
    

# Chat input
if prompt := st.chat_input("How are you feeling today?"):
    # Detect emotion and update EQ
    emotion = detect_emotion(prompt)
    update_eq_score(emotion)
    extract_important_facts(prompt)
    
    # Store message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "emotion": emotion,
        "time": datetime.now().strftime("%H:%M")
    })
    st.session_state.emotion_history.append(emotion)
    
    # Generate response
    with st.spinner("Thinking..."):
        response = generate_response(prompt, emotion)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "time": datetime.now().strftime("%H:%M")
        })
    
    st.rerun()