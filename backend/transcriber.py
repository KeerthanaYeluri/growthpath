import os
import json
import wave
import io
import tempfile

# Lazy-loaded models (load on first use)
_whisper_model = None
_vosk_model = None
_vosk_recognizer = None

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
VOSK_MODEL_PATH = os.path.join(MODELS_DIR, "vosk-model-en-in")


def get_whisper_model():
    """Load Whisper model lazily (downloads ~150MB on first run)."""
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        print("[Whisper] Loading model (first time may download ~150MB)...")
        _whisper_model = WhisperModel(
            "base",             # base model - good balance of speed/accuracy
            device="cpu",       # use CPU (change to "cuda" if you have GPU)
            compute_type="int8" # fastest on CPU
        )
        print("[Whisper] Model loaded!")
    return _whisper_model


def get_vosk_model():
    """Load Vosk model lazily."""
    global _vosk_model
    if _vosk_model is None:
        from vosk import Model, SetLogLevel
        SetLogLevel(-1)  # suppress logs
        if not os.path.exists(VOSK_MODEL_PATH):
            raise FileNotFoundError(
                f"Vosk model not found at {VOSK_MODEL_PATH}. "
                f"Download from https://alphacephei.com/vosk/models"
            )
        print("[Vosk] Loading model...")
        _vosk_model = Model(VOSK_MODEL_PATH)
        print("[Vosk] Model loaded!")
    return _vosk_model


def transcribe_whisper(audio_bytes):
    """Transcribe audio bytes using Whisper. Returns transcript text."""
    model = get_whisper_model()

    # Save audio to temp file (Whisper needs a file path)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        temp_path = f.name

    try:
        segments, info = model.transcribe(
            temp_path,
            language="en",
            beam_size=5,
            best_of=5,
            temperature=0.0,
            condition_on_previous_text=True,
            vad_filter=True,          # skip silence
            vad_parameters=dict(
                min_silence_duration_ms=300,  # detect pauses faster
            )
        )

        transcript = " ".join(seg.text.strip() for seg in segments)
        return transcript.strip()
    finally:
        os.unlink(temp_path)


def transcribe_vosk(audio_bytes):
    """Transcribe audio bytes using Vosk. Returns transcript text."""
    from vosk import KaldiRecognizer

    model = get_vosk_model()

    # Read WAV to get sample rate
    wav_io = io.BytesIO(audio_bytes)
    try:
        with wave.open(wav_io, "rb") as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())
    except Exception:
        # If not valid WAV, try raw PCM at 16kHz
        sample_rate = 16000
        frames = audio_bytes

    recognizer = KaldiRecognizer(model, sample_rate)
    recognizer.SetWords(True)  # get word-level detail

    # Feed audio in chunks for better processing
    chunk_size = 4000
    transcript_parts = []

    for i in range(0, len(frames), chunk_size):
        chunk = frames[i:i + chunk_size]
        if recognizer.AcceptWaveform(chunk):
            result = json.loads(recognizer.Result())
            if result.get("text"):
                transcript_parts.append(result["text"])

    # Get final remaining audio
    final = json.loads(recognizer.FinalResult())
    if final.get("text"):
        transcript_parts.append(final["text"])

    return " ".join(transcript_parts).strip()