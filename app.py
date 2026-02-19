import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
import database as db
import os

# 1. Initialize
db.create_db()
recognizer = sr.Recognizer()

# 2. Page Config & Theme
st.set_page_config(page_title="Sofia: AI Translator", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #2d3436; }
    .stTextArea textarea { background-color: white !important; color: #2d3436 !important; border-radius: 15px !important; border: 2px solid #667eea !important; }
    .stButton>button { background: linear-gradient(to right, #00c6ff, #0072ff); color: white !important; border-radius: 25px !important; font-weight: bold !important; border: none; }
    h1, h2, h3, p, label { color: white !important; }
    .history-card { background: rgba(255, 255, 255, 0.2); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid white; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# --- SCREEN 1: LOGIN ---
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem;'>👩‍💼 Sofia</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Your Personal Spanish-English Bridge</p>", unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 1.5, 1])
    with col_m:
        st.markdown("<div style='background: white; padding: 30px; border-radius: 20px;'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        with tab1:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Log In"):
                if db.verify_user(email, password):
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email
                    st.rerun()
                else: st.error("Wrong email or password!")
        with tab2:
            n_email = st.text_input("New Email", key="n_e")
            n_pass = st.text_input("New Password", type="password", key="n_p")
            if st.button("Sign Up"):
                if db.add_user(n_email, n_pass): st.success("Created! Now Sign In.")
                else: st.error("Email already taken.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- SCREEN 2: SOFIA TRANSLATOR ---
else:
    st.sidebar.markdown(f"### 👩‍💼 Sofia is ready\nLogged in: {st.session_state['user_email']}")
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.markdown("<h1 style='text-align: center;'>🎙️ Sofia: Voice-to-Voice Translator</h1>", unsafe_allow_html=True)
    
    mode = st.radio("Translate:", ["English ➔ Spanish", "Spanish ➔ English"], horizontal=True)
    src_l, dest_l = ('en', 'es') if mode == "English ➔ Spanish" else ('es', 'en')

    col_in, col_out = st.columns(2)
    with col_in:
        st.markdown("### 📥 Input")
        user_text = st.text_area("Type or Record...", height=150)
        if st.button("🎤 Start Listening"):
            with sr.Microphone() as source:
                st.toast("Listening...")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    user_text = recognizer.recognize_google(audio, language=src_l)
                    st.success(f"Heard: {user_text}")
                except: st.error("Try again!")

    with col_out:
        st.markdown("### 📤 Result")
        if user_text:
            translated = GoogleTranslator(source=src_l, target=dest_l).translate(user_text)
            st.text_area("Translation:", value=translated, height=150, disabled=True)
            
            # Save to history!
            db.save_history(st.session_state['user_email'], user_text, translated, mode)
            
            tts = gTTS(text=translated, lang=dest_l)
            tts.save("speech.mp3")
            st.audio("speech.mp3")

    # --- HISTORY SECTION ---
    st.markdown("---")
    st.markdown("### 📜 Your Translation History")
    history_data = db.get_history(st.session_state['user_email'])
    
    if history_data:
        for original, trans, direction, time in history_data:
            with st.container():
                st.markdown(f"""
                <div class="history-card">
                    <small style='color: #eee;'>📅 {time} | 🔄 {direction}</small><br>
                    <b>Input:</b> {original}<br>
                    <b>Sofia:</b> {trans}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.write("No history yet. Start talking to Sofia!")