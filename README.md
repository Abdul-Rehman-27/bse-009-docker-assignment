---
title: Whisper Speech To Text
emoji: 🎙️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Speech-to-Text Web App (Whisper Small)

A lightweight Flask web application that transcribes speech to text using
OpenAI's Whisper **small** model. Runs entirely on CPU, making it suitable
for free-tier Hugging Face Spaces hosting.

## Credit / Acknowledgment

This project is built on top of **OpenAI Whisper**:
- Original repository: https://github.com/openai/whisper
- All model weights and core inference code belong to OpenAI. This app only
  adds a web interface (Flask + HTML) and course-related engineering
  additions (testing, threading, etc.) around it.

## Model

- **Type**: Encoder-decoder Transformer (sequence-to-sequence) for automatic
  speech recognition
- **Checkpoint**: `small` (~244M parameters, CPU-friendly)
- **Input**: audio file (wav, mp3, m4a, flac, ogg, webm)
- **Output**: transcribed text (English or auto-detected language)

## Running locally

```bash
pip install -r requirements.txt
python app.py
# open http://localhost:7860
```

## Running with Docker

```bash
docker build -t whisper-app .
docker run -p 7860:7860 whisper-app
# open http://localhost:7860
```

## Deploying to Hugging Face Spaces

1. Create a new Space, choose **Docker** as the SDK.
2. Push this folder's contents (including this `README.md`, `Dockerfile`,
   `requirements.txt`, `app.py`, `templates/`) to the Space's git repo.
3. The Space will build the Docker image and expose the app on port `7860`
   automatically (this is set via `app_port` above).

## Project structure

```
.
├── Dockerfile
├── requirements.txt
├── app.py
├── testing.py
└── templates/
    └── index.html
```

## Limitations

- CPU inference is slower than GPU; large audio files may take longer.
- Whisper `small` trades some accuracy for speed/size compared to
  `medium`/`large` checkpoints.
- No GPU is used or required (per assignment constraints).

## Future work

- Add language selection dropdown
- Add streaming/live microphone transcription
- Add a progress indicator for long files
