import whisper
import librosa
import numpy as np

# ============================================================
# SAHAY — AUDIO + SPEECH + NLP PROOF OF CONCEPT
# ============================================================

audio_file = "03-01-01-01-01-01-01.wav"

print("\n========== SAHAY AUDIO ANALYSIS ==========\n")


# ============================================================
# 1. AUDIO ANALYSIS — LIBROSA
# ============================================================

print("[1] Analysing voice with Librosa...")

y, sr = librosa.load(audio_file, sr=None)

duration = len(y) / sr

# Energy
rms = librosa.feature.rms(y=y)[0]
average_energy = np.mean(rms)

# Pitch
f0, voiced_flag, voiced_prob = librosa.pyin(
    y,
    fmin=librosa.note_to_hz("C2"),
    fmax=librosa.note_to_hz("C7")
)

valid_pitch = f0[~np.isnan(f0)]

if len(valid_pitch) > 0:
    average_pitch = np.mean(valid_pitch)
    pitch_variation = np.std(valid_pitch)
else:
    average_pitch = 0
    pitch_variation = 0

# MFCC
mfcc = librosa.feature.mfcc(
    y=y,
    sr=sr,
    n_mfcc=13
)

# Pause / silence
rms_db = librosa.amplitude_to_db(rms, ref=np.max)
silence_frames = rms_db < -35
pause_percentage = np.mean(silence_frames) * 100


print(f"Duration: {duration:.2f} seconds")
print(f"Sample Rate: {sr} Hz")
print(f"Average Energy: {average_energy:.4f}")
print(f"Average Pitch: {average_pitch:.2f} Hz")
print(f"Pitch Variation: {pitch_variation:.2f} Hz")
print(f"MFCC Features: {mfcc.shape}")
print(f"Estimated Pause/Silence: {pause_percentage:.1f}%")


# ============================================================
# 2. SPEECH-TO-TEXT — WHISPER
# ============================================================

print("\n[2] Converting speech to text with Whisper...")

model = whisper.load_model("base")

result = model.transcribe(audio_file)

whisper_text = result["text"].strip()

print("\n===== WHISPER TRANSCRIPTION =====")
print(whisper_text)
print("=================================")


# ============================================================
# 3. DEMO TEXT SELECTION
# ============================================================

print("\n[3] NLP Risk Analysis")

print("\nChoose input:")
print("1 - Use Whisper transcript")
print("2 - Enter a test victim statement")

choice = input("\nEnter 1 or 2: ").strip()

if choice == "2":

    print("\nEnter a test statement.")
    print("Example: I'm scared. Please help me. They are threatening to hurt me.")

    text = input("\nStatement: ").strip().lower()

else:

    text = whisper_text.lower()


# ============================================================
# 4. NLP RISK INDICATOR EXTRACTION
# ============================================================

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


def find_indicators(words, text):
    return [
        word for word in words
        if word in text
    ]


fear_indicators = find_indicators(fear_words, text)
threat_indicators = find_indicators(threat_words, text)
distress_indicators = find_indicators(distress_words, text)


print("\n===== NLP RISK INDICATORS =====")

print("Fear indicators:", fear_indicators)
print("Threat indicators:", threat_indicators)
print("Distress indicators:", distress_indicators)


# ============================================================
# 5. PROOF-OF-CONCEPT RISK SCORE
# ============================================================

risk_points = 0

# Fear indicators
risk_points += len(fear_indicators) * 10

# Distress indicators
risk_points += len(distress_indicators) * 10

# Threat indicators
risk_points += len(threat_indicators) * 20

# Maximum score
risk_score = min(risk_points, 100)


# ============================================================
# 6. RISK CLASSIFICATION
# ============================================================

if risk_score >= 75:
    risk_level = "CRITICAL"

elif risk_score >= 50:
    risk_level = "HIGH"

elif risk_score >= 25:
    risk_level = "MODERATE"

else:
    risk_level = "LOW"


# ============================================================
# 7. FINAL SAHAY RESULT
# ============================================================

print("\n========== SAHAY RISK ASSESSMENT ==========")

print(f"Analysed Text: {text}")

print(f"\nRisk Indicator Score: {risk_score}/100")

print(f"Risk Level: {risk_level}")

print("\n============================================")
print("          ANALYSIS COMPLETE")
print("============================================")