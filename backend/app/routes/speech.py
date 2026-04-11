import os
import shutil
import base64
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.speech.audio_engine import audio_engine
from app.services.search.semantic_search import search_engine
from app.services.llm.generator import llm_engine

router = APIRouter(prefix="/api/speech", tags=["Voice & Accessibility"])

TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/voice-query")
async def process_voice_query(audio_file: UploadFile = File(...)):
    try:
        # 1. Save uploaded audio
        input_path = os.path.join(TEMP_DIR, f"input_{audio_file.filename}")
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # 2. EARS (ASR): Voice to Text
        user_text = audio_engine.transcribe_audio(input_path)
        if "Error" in user_text:
            raise HTTPException(status_code=500, detail=user_text)

        # 3. BRAIN: Search and Generate
        search_results = search_engine.search(user_text, top_k=2)
        ai_text_response = llm_engine.generate_response(user_text, search_results)

        # 4. MOUTH (TTS): Text to Voice MP3
        output_path = os.path.join(TEMP_DIR, "output_response.mp3")
        audio_engine.text_to_speech(ai_text_response, output_path)

        # 5. NEW: Convert MP3 to Base64 string so React can read it easily inside JSON!
        with open(output_path, "rb") as audio_f:
            audio_base64 = base64.b64encode(audio_f.read()).decode('utf-8')

        # Return Text AND Audio together
        return {
            "user_text": user_text,
            "bot_text": ai_text_response,
            "audio_base64": audio_base64
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))