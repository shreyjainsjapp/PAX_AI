import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv
import boto3
import json
from botocore.exceptions import ClientError


load_dotenv()

def get_secret():
    secret_name = "openai-api-key"  # Name of your secret in AWS Secrets Manager
    region_name = "us-east-1"       # Change to your region

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret['OPENAI_API_KEY']

# Initialize OpenAI client with secret manager
try:
    api_key = get_secret()
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"Failed to retrieve API key: {str(e)}")
    st.stop()



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
    page_title="EmoGenie Pro", 
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
    "frustration": -2, "neutral": 0
}

def update_eq_score(emotion):
    """Update Emotional Quotient score"""
    st.session_state.eq_score += EQ_WEIGHTS.get(emotion, 0)
    st.session_state.eq_score = max(0, min(100, st.session_state.eq_score))

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

def remember_everything(user_input):
    """Store every user message exactly as-is"""
    st.session_state.conversation_context.append(user_input)

def generate_response(user_input, emotion):
    try:
        # Use ALL previous messages as context
        full_history = "\n".join(
            f"{m['role'].capitalize()}: {m['content']}"
            for m in st.session_state.messages
        )
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": f"""You're an empathetic pyschologist or therapist with perfect memory. Act like a personal friend or guide to help people in different mental phases of life. Rules:
1. FULL CONVERSATION HISTORY:
{full_history}

2. Remembered Details:
{st.session_state.conversation_context}

3. Current emotion: {emotion}
4. Respond in 2-3 sentences, referencing relevant history"""
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
st.title("🧠 EmoGenie Pro")
st.caption("Your AI powered Mental Health Buddy")

# Create the sidebar (left panel)
with st.sidebar:
    #st.header("Conversation Memory")
    
    with st.expander(f"🧠 Chat History ({len(st.session_state.conversation_context)})"):
        if st.session_state.conversation_context:
            for i, msg in enumerate(st.session_state.conversation_context, 1):
                st.markdown(f"{i}. {msg}")
        else:
            st.write("No messages yet")
    
    if st.session_state.emotion_history:
        st.subheader("Emotion Frequency")
        emotion_df = pd.Series(st.session_state.emotion_history).value_counts().reset_index()
        emotion_df.columns = ['Emotion', 'Count']
        st.dataframe(emotion_df, hide_index=True, use_container_width=True)

# Create the right sidebar (permanent panel)
st.sidebar_right = st.sidebar.container()
with st.sidebar_right:
    st.header("Emotional Health Panel")
    
    # Emotional Quotient
    #st.subheader("Emotional Health")
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
            height=300,width=500
        )
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=30), legend=dict(
                title="Emotions",
                orientation="h",
                yanchor="bottom",
                y=-0.9,
                xanchor="center",
                x=0.5))
        st.plotly_chart(fig, use_container_width=True,height=500, key=f"pie_chart_{len(st.session_state.emotion_history)}")

# Main chat area
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

# Chat input
if prompt := st.chat_input("How are you feeling today?"):
    # Detect emotion and update EQ
    emotion = detect_emotion(prompt)
    update_eq_score(emotion)
    remember_everything(prompt)
    
    # Store message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "emotion": emotion,
        "time": datetime.now().strftime("%H:%M")
    })
    st.session_state.emotion_history.append(emotion)
    
    # Check for quit command
    if prompt.lower().strip() == "quit":
        # Prepare chat history for CSV
        chat_history = []
        for i in range(0, len(st.session_state.messages)-1, 2):
            if (i+1) < len(st.session_state.messages):
                user_msg = st.session_state.messages[i]
                bot_msg = st.session_state.messages[i+1]
                if user_msg["role"] == "user" and bot_msg["role"] == "assistant":
                    chat_history.append({
                        "User_msg": user_msg["content"],
                        "Bot_msg": bot_msg["content"],
                        "emotion": user_msg.get("emotion", "unknown")
                    })
        
        # Create DataFrame and save to CSV
        if chat_history:
            df = pd.DataFrame(chat_history)
            csv_filename = f"emogenie_chat{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(csv_filename, index=False)
            st.toast(f"Chat history saved to {csv_filename}", icon="💾")
        
        # Clear the chat (optional)
        st.session_state.messages = []
        st.session_state.emotion_history = []
        st.session_state.conversation_context = []
        st.session_state.eq_score = 50
        st.rerun()
    else:
        # Generate response (only if not quitting)
        with st.spinner("Thinking..."):
            response = generate_response(prompt, emotion)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "time": datetime.now().strftime("%H:%M")
            })
        
        st.rerun()

### perfection with all advanced features & csv file creation & AWS SECRET MANAGER (TESTING LEFT)

