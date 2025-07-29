import streamlit as st
import speech_recognition as sr
from google.generativeai import GenerativeModel
from audiorecorder import audiorecorder
from gtts import gTTS
import os
import io
import tempfile
import soundfile as sf # For handling audio data


try:
    # Attempt to get API key from environment, then secrets.toml
    API_KEY = os.environ.get("GOOGLE_API_KEY")
    if not API_KEY:
        # If not in environment, try Streamlit secrets
        API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Gemini API key not found. Please set it as an environment variable (GOOGLE_API_KEY) or in your Streamlit secrets.toml file.")
    st.stop()

# Initialize Gemini Pro model
try:
    genai_model = GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Failed to initialize Gemini Pro model. Make sure your GOOGLE_API_KEY is set correctly. Error: {e}")
    st.stop()

# Supported languages for translation (key: code, value: display name)
# These are the target languages for translation and TTS output.
# Input languages are English ('en') and Hindi ('hi')
SUPPORTED_LANGUAGES = {
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'hi': 'Hindi', # Can be target too
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh-CN': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'it': 'Italian',
    'en': 'English' # Can be target too
}

# --- Streamlit UI ---
st.set_page_config(page_title="Speech-to-Speech Translator", layout="centered")

st.title("🗣️ Speech-to-Speech Translator")
st.markdown("""
Speak in **English** or **Hindi**, and get instant translation and spoken output in your selected language!
""")

# Language selection for output
target_lang_display = st.selectbox(
    "Select Target Language for Translation:",
    options=list(SUPPORTED_LANGUAGES.values()),
    index=list(SUPPORTED_LANGUAGES.keys()).index('es') # Default to Spanish
)
target_lang_code = [k for k, v in SUPPORTED_LANGUAGES.items() if v == target_lang_display][0]

st.subheader("1. Speak into the Microphone")

# Audio Recorder Widget from audiorecorder library
# Note: This uses the `audiorecorder` function from the `audiorecorder` library,
# which has different arguments than Streamlit's built-in st.audio_recorder.
# It typically uses 'start_prompt' and 'stop_prompt' for button labels.
# IMPORTANT: This library, or SpeechRecognition, might require FFmpeg to be installed on your system.
# If you get a "FileNotFoundError: [Errno 2] No such file or directory: 'ffprobe'",
# please install FFmpeg (e.g., `brew install ffmpeg` on macOS, `sudo apt install ffmpeg` on Linux,
# or download and add to PATH on Windows).
audio_bytes = audiorecorder(
    start_prompt="Click to start recording",
    stop_prompt="Click to stop recording",
    key="audio_recorder",
    show_visualizer=True,
)

if audio_bytes:
    st.subheader("2. Processing Your Speech...")
    st.info("Transcribing and translating your audio. This may take a moment...")

    try:
        # Save the recorded audio to a temporary WAV file for SpeechRecognition
        # audiorecorder returns a pydub.AudioSegment object, which needs to be exported
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
            # Export the AudioSegment object to the temporary file
            audio_bytes.export(tmp_audio_file.name, format="wav")
            audio_file_path = tmp_audio_file.name

        recognizer = sr.Recognizer()
        original_text = ""
        detected_input_lang = "en" # Default to English if detection fails

        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source) # Read the entire audio file

            # Try to recognize English
            try:
                original_text = recognizer.recognize_google(audio_data, language="en-US")
                detected_input_lang = "en"
                st.success(f"Detected input language: English")
            except sr.UnknownValueError:
                # If English recognition fails, try Hindi
                try:
                    original_text = recognizer.recognize_google(audio_data, language="hi-IN")
                    detected_input_lang = "hi"
                    st.success(f"Detected input language: Hindi")
                except sr.UnknownValueError:
                    st.warning("Could not understand audio in English or Hindi. Please try again.")
                    original_text = "[Could not transcribe]"
                except sr.RequestError as e:
                    st.error(f"Could not request results from Google Speech Recognition service; {e}")
                    original_text = "[Transcription Error]"
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Speech Recognition service; {e}")
                original_text = "[Transcription Error]"

        os.remove(audio_file_path) # Clean up temporary file

        st.write(f"**Original Text ({detected_input_lang.upper()}):**")
        st.write(original_text)

        if original_text and original_text != "[Could not transcribe]":
            st.subheader("3. Translating and Speaking...")

            # --- Text Translation using Gemini Pro ---
            translation_prompt = f"Translate the following text from {detected_input_lang} to {SUPPORTED_LANGUAGES[target_lang_code]} ({target_lang_code}):\n\n{original_text}"
            
            # Use gemini-pro for text translation
            response = genai_model.generate_content(translation_prompt)
            translated_text = response.text

            st.write(f"**Translated Text ({SUPPORTED_LANGUAGES[target_lang_code]}):**")
            st.write(translated_text)

            # --- Text-to-Speech using gTTS ---
            try:
                tts = gTTS(text=translated_text, lang=target_lang_code, slow=False)
                
                # Save TTS audio to a bytes buffer
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0) # Rewind to the beginning of the buffer

                st.audio(audio_fp.read(), format="audio/mp3")
                st.success("Translation spoken!")

            except Exception as e:
                st.error(f"Error generating or playing translated speech: {e}")
                st.info("Ensure the selected target language is supported by Google Text-to-Speech for audio output.")

    except Exception as e:
        st.error(f"An unexpected error occurred during processing: {e}")

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit, SpeechRecognition, Gemini Pro, and gTTS.")
