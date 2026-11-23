import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzeAudio = async () => {
    if (!file) {
      setError("Please select an audio file first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        "Could not connect to AAVAZ backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const riskClass = result?.risk_level?.toLowerCase() || "";

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>AVAAZ</h1>
          <p>AI-Assisted Victim Stress & Risk Assessment</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Ready
        </div>
      </header>

      <main className="container">
        {/* Upload */}
        <section className="upload-card">
          <h2>Audio Assessment</h2>
          <p className="muted">
            Upload a victim interaction for analysis.
          </p>

          <div className="upload-row">
            <label className="file-input">
              <input
                type="file"
                accept=".wav,.mp3,.m4a,.ogg"
                onChange={(e) => {
                  setFile(e.target.files[0]);
                  setResult(null);
                  setError("");
                }}
              />

              <span>
                {file ? file.name : "Choose audio file"}
              </span>
            </label>

            <button
              className="analyze-btn"
              onClick={analyzeAudio}
              disabled={loading}
            >
              {loading ? "Analysing..." : "Analyse"}
            </button>
          </div>

          {error && <p className="error">{error}</p>}
        </section>

        {/* Loading */}
        {loading && (
          <section className="loading-card">
            <div className="spinner"></div>
            <p>Processing audio with AVAAZ...</p>
          </section>
        )}

        {/* Results */}
        {result && (
          <>
            {/* Risk Overview */}
            <section className="risk-grid">
              <div className="card">
                <p className="label">SVI SCORE</p>

                <div className="score">
                  {result.risk_score}
                  <span>/100</span>
                </div>

                <p className="muted">
                  Stress Vulnerability Index
                </p>
              </div>

              <div className={`card risk-card ${riskClass}`}>
                <p className="label">RISK LEVEL</p>

                <div className="risk-level">
                  {result.risk_level}
                </div>

                <p className="muted">
                  Current assessment category
                </p>
              </div>

              <div className="card">
                <p className="label">AUDIO DURATION</p>

                <div className="metric">
                  {result.audio_features.duration}s
                </div>

                <p className="muted">
                  Analysed audio
                </p>
              </div>
            </section>

            {/* Transcript */}
            <section className="card">
              <div className="section-title">
                <h2>Whisper Transcript</h2>
                <span className="tag">SPEECH → TEXT</span>
              </div>

              <div className="transcript">
                {result.transcript || "No speech detected."}
              </div>
            </section>

            {/* Audio Features */}
            <section className="card">
              <div className="section-title">
                <h2>Audio Analysis</h2>
                <span className="tag">LIBROSA</span>
              </div>

              <div className="feature-grid">
                <div className="feature">
                  <span>Average Pitch</span>
                  <strong>
                    {result.audio_features.average_pitch} Hz
                  </strong>
                </div>

                <div className="feature">
                  <span>Pitch Variation</span>
                  <strong>
                    {result.audio_features.pitch_variation} Hz
                  </strong>
                </div>

                <div className="feature">
                  <span>Energy</span>
                  <strong>
                    {result.audio_features.average_energy}
                  </strong>
                </div>

                <div className="feature">
                  <span>Pause / Silence</span>
                  <strong>
                    {result.audio_features.pause_percentage}%
                  </strong>
                </div>
              </div>
            </section>

            {/* Risk Indicators */}
            <section className="card">
              <div className="section-title">
                <h2>Risk Indicators</h2>
                <span className="tag">NLP</span>
              </div>

              <div className="indicator-grid">
                <Indicator
                  title="Fear"
                  items={result.risk_indicators.fear}
                />

                <Indicator
                  title="Threat"
                  items={result.risk_indicators.threat}
                />

                <Indicator
                  title="Distress"
                  items={result.risk_indicators.distress}
                />
              </div>
            </section>
          </>
        )}
      </main>

      <footer>
        AVAAZ • AI-assisted assessment • Human oversight required
      </footer>
    </div>
  );
}

function Indicator({ title, items }) {
  return (
    <div className="indicator">
      <h3>{title}</h3>

      <div className="chips">
        {items.length > 0 ? (
          items.map((item, index) => (
            <span className="chip" key={index}>
              {item}
            </span>
          ))
        ) : (
          <span className="none">None detected</span>
        )}
      </div>
    </div>
  );
}

export default App;