import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from faster_whisper import WhisperModel

# Agree to Coqui TOS for non-interactive container environments
os.environ["COQUI_TOS_AGREED"] = "1"
from TTS.api import TTS

app = FastAPI(title="Hermes Audio Microservice")

# ─────────────────────────────────────────────
# Model initialization (at startup)
# ─────────────────────────────────────────────

print(f"[hermes-audio] Loading Whisper STT model (base, CPU int8)...")
stt_model = WhisperModel("base", device="cpu", compute_type="int8")
print("[hermes-audio] Whisper model ready!")

print("[hermes-audio] Loading XTTS v2 TTS model (CPU)...")
tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
print("[hermes-audio] XTTS v2 model ready!")

# Reference speaker WAV (required by XTTS for zero-shot voice cloning)
REFERENCE_WAV = os.path.join(os.path.dirname(__file__), "reference_speaker.wav")

# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────

def remove_file(path: str):
    """Background cleanup of temporary audio files."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "stt": "faster-whisper/base", "tts": "xtts_v2"}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Receive an audio file (OGG/WAV/MP3) and return the transcribed text.
    Used to convert WhatsApp voice notes to text.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        print(f"[hermes-audio] Transcribing {file.filename}...")
        segments, info = stt_model.transcribe(tmp_path, beam_size=5)
        transcription = " ".join(s.text for s in segments).strip()
        print(f"[hermes-audio] Transcription ({info.language}): {transcription}")
        return JSONResponse({"text": transcription, "language": info.language})
    except Exception as exc:
        print(f"[hermes-audio] Transcription error: {exc}")
        return JSONResponse({"error": str(exc)}, status_code=500)
    finally:
        remove_file(tmp_path)


@app.post("/synthesize")
async def synthesize(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    language: str = Form("pt"),
):
    """
    Convert text to speech using XTTS v2 (local, offline).
    Returns a WAV audio file.
    """
    tmp_path = tempfile.mktemp(suffix=".wav")

    try:
        if not os.path.exists(REFERENCE_WAV):
            return JSONResponse(
                {"error": f"Reference speaker WAV not found at '{REFERENCE_WAV}'. Mount a real voice file."},
                status_code=500,
            )

        print(f"[hermes-audio] Synthesizing (XTTS v2, lang={language}): {text[:80]}...")
        tts_model.tts_to_file(
            text=text,
            file_path=tmp_path,
            speaker_wav=REFERENCE_WAV,
            language=language,
        )
        print(f"[hermes-audio] Synthesis complete: {tmp_path}")

        background_tasks.add_task(remove_file, tmp_path)
        return FileResponse(tmp_path, media_type="audio/wav", filename="response.wav")

    except Exception as exc:
        print(f"[hermes-audio] Synthesis error: {exc}")
        remove_file(tmp_path)
        return JSONResponse({"error": str(exc)}, status_code=500)
