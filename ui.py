import streamlit as st
import requests
import json
# FastAPI backend URLs
START_TRANSCRIPTION_URL = "http://127.0.0.1:8000/start-speech"

st.set_page_config(page_title="AI Voice Assistant", layout="centered")

st.markdown(
    "<h1 style='text-align: center; color: #4A90E2;'>🎙️ AI Voice Assistant</h1>",
    unsafe_allow_html=True
)

# Centered microphone button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🎤 Start Listening", use_container_width=True):
        response = requests.get(START_TRANSCRIPTION_URL)
        # res= "" if (response.json()['transcription']==None) else response.json()['transcription']
        res='succes'
        st.success(res)
