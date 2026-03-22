# AI Real-Time Transcription & Translation Service

Continuous audio transcription and language translation service powered by OpenAI Whisper and Google Translate, designed for video conferencing applications.

## Features

- **Real-time Speech-to-Text**: Continuous audio transcription using OpenAI Whisper
- **Multi-language Support**: 20+ languages supported
- **Automatic Language Detection**: Detects spoken language automatically
- **Real-time Translation**: Translates transcriptions to user's preferred language
- **Low Latency**: Optimized for real-time communication
- **GPU Acceleration**: Supports CUDA for faster processing

## Supported Languages

English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi, Bengali, Urdu, Turkish, Vietnamese, Thai, Dutch, Polish, Swedish

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster processing

### Install Dependencies

```bash
cd ai-transcription
pip install -r requirements.txt
```

### Install FFmpeg (Required for audio processing)

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure:

```env
PORT=5002
HOST=0.0.0.0

# Whisper model size: tiny, base, small, medium, large
# tiny: Fastest, least accurate (good for testing)
# base: Good balance for real-time (recommended)
# small: Better accuracy, slower
# medium/large: Best accuracy, requires GPU
WHISPER_MODEL=base

TRANSLATION_SERVICE=google
```

## Usage

### Start the Transcription Server

```bash
python transcription_server.py
```

The server will start on `http://localhost:5002`

### Check Server Status

```bash
curl http://localhost:5002/health
```

## Integration with Video Meeting App

The transcription service is already integrated with your video meeting frontend. To enable it:

1. Start the transcription server (see above)
2. In your video meeting, click the "🎤 Live Transcription" button
3. Select your preferred language
4. Click "Start Recording" to begin transcription

## API Endpoints

### HTTP Endpoints

- `GET /` - Service status
- `GET /health` - Detailed health check

### WebSocket Events

**Client → Server:**
- `join_transcription_room` - Join a transcription room
- `leave_transcription_room` - Leave a transcription room
- `stream_audio_chunk` - Send audio data for transcription
- `change_target_language` - Change translation target language

**Server → Client:**
- `transcription_result` - Transcription and translation result
- `transcription_error` - Error message
- `connection_status` - Connection status update

## Performance Optimization

### Model Selection

- **tiny**: ~1GB RAM, fastest, 32x real-time on CPU
- **base**: ~1GB RAM, good balance, 16x real-time on CPU (recommended)
- **small**: ~2GB RAM, better accuracy, 6x real-time on CPU
- **medium**: ~5GB RAM, high accuracy, requires GPU
- **large**: ~10GB RAM, best accuracy, requires GPU

### GPU Acceleration

If you have a CUDA-capable GPU:

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

The service will automatically use GPU if available.

## Troubleshooting

### "FFmpeg not found" error

Install FFmpeg (see Installation section above)

### Slow transcription

- Use a smaller Whisper model (tiny or base)
- Enable GPU acceleration if available
- Reduce audio chunk duration in `.env`

### Translation errors

- Check internet connection (Google Translate requires internet)
- Verify language codes are correct
- Check server logs for detailed error messages

### No transcription output

- Ensure microphone permissions are granted in browser
- Check audio quality and volume
- Verify audio chunks are being sent (check browser console)
- Check server logs for errors

## Development

### Run in Development Mode

```bash
# With auto-reload
python transcription_server.py
```

### View Logs

Logs are printed to console with timestamps and log levels.

## Production Deployment

### Using Gunicorn (Linux/macOS)

```bash
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5002 transcription_server:app
```

### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

CMD ["python", "transcription_server.py"]
```

## Architecture

```
┌─────────────────┐
│  Video Meeting  │
│   (Frontend)    │
└────────┬────────┘
         │ WebSocket
         │ (Audio Chunks)
         ▼
┌─────────────────┐
│  Transcription  │
│     Server      │
│  (Flask-SocketIO)│
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Whisper │ │ Google   │
│  AI    │ │Translate │
└────────┘ └──────────┘
```

## License

MIT License

## Credits

- OpenAI Whisper for speech recognition
- Google Translate for translation
- Flask-SocketIO for real-time communication
