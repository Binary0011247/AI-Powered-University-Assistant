import os
from groq import Groq
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AudioEngine:
    def __init__(self):
        print("🎙️ Loading Audio Engine...")
        if GROQ_API_KEY:
            self.client = Groq(api_key=GROQ_API_KEY)
        else:
            self.client = None
            print("⚠️ WARNING: GROQ_API_KEY not found!")

    def transcribe_audio(self, audio_file_path: str) -> str:
        """Converts an audio file (mp3/wav) into text using Whisper."""
        if not self.client:
            return "Error: Groq API not connected."
        
        try:
            with open(audio_file_path, "rb") as file:
                # Use OpenAI's Whisper model hosted on Groq's lightning-fast servers
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(audio_file_path), file.read()),
                    model="whisper-large-v3",
                    response_format="json",
                )
            return transcription.text
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"

    def text_to_speech(self, text: str, output_file_path: str):
        """Converts text into a spoken MP3 file."""
        try:
            # Create a human-sounding voice using Google TTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_file_path)
            return output_file_path
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

audio_engine = AudioEngine()