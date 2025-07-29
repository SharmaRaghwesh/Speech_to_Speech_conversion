A real-time speech-to-speech translation application built with Google Gemini AI that allows users to speak in one language and receive both translated text and audio output in their selected target language.

🚀 Features
Real-time Speech Recognition: Capture and process spoken input using advanced speech recognition
Multi-language Translation: Translate speech between multiple supported languages using Google Gemini AI
Text-to-Speech Output: Generate natural-sounding audio in the target language
User-friendly Interface: Simple and intuitive interface for seamless user experience
Language Selection: Choose from a wide range of supported languages for translation
High Accuracy: Powered by Google Gemini AI for accurate translation results

🛠️ Technologies Used
Google Gemini AI: Core translation and AI processing
Speech Recognition API: For converting speech to text
Text-to-Speech API: For generating audio output

📋 Prerequisites
Before running this application, make sure you have:

Google Gemini API key
Modern web browser with microphone access
Internet connection for API calls🔧 Installation

Clone the repository
bashgit clone https://github.com/SharmaRaghwesh/speech-to-speech-conversion.git
cd speech-to-speech-conversion

Install dependencies

pip install -r requirements.txt

Set up environment variables
Create a .env file in the root directory:
envGEMINI_API_KEY=your_gemini_api_key_here


Run the  streamlit application

streamlit run app.py
