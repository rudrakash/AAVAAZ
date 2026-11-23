from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import whisper
import librosa
import numpy as np

app = FastAPI(title="SAHAY API")

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper once when backend starts
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper ready!")


@app.get("/")
def home():
    return {
        "message": "SAHAY Backend is running"
    }


@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):

    # Save uploaded audio temporarily
    temp_file = "temp_audio.wav"

    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ==========================================
    # 1. LIBROSA AUDIO ANALYSIS
    # ==========================================

    y, sr = librosa.load(temp_file, sr=None)

    duration = len(y) / sr

    # Energy
    rms = librosa.feature.rms(y=y)[0]
    average_energy = float(np.mean(rms))

    # Pitch
    f0, voiced_flag, voiced_prob = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7")
    )

    valid_pitch = f0[~np.isnan(f0)]

    if len(valid_pitch) > 0:
        average_pitch = float(np.mean(valid_pitch))
        pitch_variation = float(np.std(valid_pitch))
    else:
        average_pitch = 0
        pitch_variation = 0

    # MFCC
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=13
    )

    # Silence / pauses
    rms_db = librosa.amplitude_to_db(
        rms,
        ref=np.max
    )

    silence_frames = rms_db < -35

    pause_percentage = float(
        np.mean(silence_frames) * 100
    )

    # ==========================================
    # 2. WHISPER TRANSCRIPTION
    # ==========================================

    result = model.transcribe(temp_file)

    transcript = result["text"].strip()

    text = transcript.lower()

    # ==========================================
    # 3. NLP INDICATORS
    # ==========================================

    fear_words = [
        "scared",
        "afraid",
        "fear",
        "frightened",
        "terrified",
        "panic",
        "worried"
    ]

    threat_words = [
        "kill",
        "hurt",
        "attack",
        "threat",
        "threatening",
        "danger",
        "harm"
    ]

    distress_words = [
        "help",
        "cry",
        "crying",
        "alone",
        "desperate",
        "please",
        "can't"
    ]

    def find_indicators(words):
        return [
            word for word in words
            if word in text
        ]

    fear_indicators = find_indicators(fear_words)
    threat_indicators = find_indicators(threat_words)
    distress_indicators = find_indicators(distress_words)

    # ==========================================
    # 4. PROOF-OF-CONCEPT RISK SCORE
    # ==========================================

    risk_score = 0

    risk_score += len(fear_indicators) * 10
    risk_score += len(distress_indicators) * 10
    risk_score += len(threat_indicators) * 20

    risk_score = min(risk_score, 100)

    # ==========================================
    # 5. RISK CLASSIFICATION
    # ==========================================

    if risk_score >= 75:
        risk_level = "CRITICAL"
    elif risk_score >= 50:
        risk_level = "HIGH"
    elif risk_score >= 25:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    # Remove temporary audio
    if os.path.exists(temp_file):
        os.remove(temp_file)

    # ==========================================
    # 6. SEND RESULTS TO REACT
    # ==========================================

    return {
        "transcript": transcript,

        "audio_features": {
            "duration": round(duration, 2),
            "sample_rate": sr,
            "average_energy": round(average_energy, 4),
            "average_pitch": round(average_pitch, 2),
            "pitch_variation": round(pitch_variation, 2),
            "mfcc_shape": list(mfcc.shape),
            "pause_percentage": round(pause_percentage, 1)
        },

        "risk_indicators": {
            "fear": fear_indicators,
            "threat": threat_indicators,
            "distress": distress_indicators
        },

        "risk_score": risk_score,
        "risk_level": risk_level
    }