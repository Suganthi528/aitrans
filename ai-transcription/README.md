# AI Real-Time Transcription & Translation Service

This Python-based AI service provides real-time speech transcription and translation for the video meeting application.

## Features

- 🎤 Real-time speech-to-text transcription
- 🌍 Automatic language translation (20+ languages supported)
- 🔄 Continuous audio streaming and processing
- 🤖 AI-powered language detection
- 📝 Live transcription feed for all participants

## Supported Languages

- English, Spanish, French, German, Italian
- Portuguese, Russian, Japanese, Korean
- Chinese (Simplified), Arabic, Hindi, Bengali
- Urdu, Turkish, Vietnamese, Thai
- Dutch, Polish, Swedish, and more...

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Microphone access

### Setup Steps

1. Navigate to the ai-transcription directory:
```bash
cd hiimeet/ai-transcription
```

2. Run the setup script (Windows):
```bash
setup.bat
```

Or manually install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (copy from `.env.example`):
```bash
copy .env.example .env
```

## Running the Service

Start the transcription service:

```bash
python transcription_service.py
```

The service will start on port 5002 by default.

## How It Works

1. **Audio Capture**: The frontend captures audio from the user's microphone
2. **Streaming**: Audio chunks are sent to the Python service via WebSocket
3. **Transcription**: Google Speech Recognition API transcribes the audio
4. **Translation**: Deep Translator translates text to each participant's chosen language
5. **Broadcasting**: Translated text is sent back to all participants in real-time

## API Endpoints

### HTTP Endpoints

- `GET /health` - Health check
- `GET /languages` - Get list of supported languages

### WebSocket Events

#### Client → Server

- `join_transcription_room` - Join a transcription room
- `leave_transcription_room` - Leave a transcription room
- `change_target_language` - Change translation target language
- `transcribe_audio` - Send audio for transcription
- `stream_audio_chunk` - Stream audio chunks for continuous transcription

#### Server → Client

- `connection_status` - Connection status update
- `transcription_result` - Transcribed and translated text
- `transcription_error` - Error message
- `language_changed` - Language change confirmation

## Configuration

Edit `.env` file to configure:

```env
TRANSCRIPTION_PORT=5002
FLASK_ENV=development
```

## Integration with Frontend

The TranscriptionPanel component is already created in the frontend. To use it:

```javascript
import TranscriptionPanel from './TranscriptionPanel';

<TranscriptionPanel 
  roomId={roomId}
  userId={userId}
  userName={userName}
  isEnabled={true}
/>
```

## Troubleshooting

### Microphone Access Issues
- Ensure browser has microphone permissions
- Check system microphone settings
- Use HTTPS for production (required for microphone access)

### Translation Errors
- Check internet connection (requires online API access)
- Verify language codes are correct
- Some languages may have limited support

### Performance Issues
- Reduce audio chunk size for faster processing
- Use a more powerful server for multiple concurrent users
- Consider using Whisper AI for better accuracy (requires more resources)

## Future Enhancements

- [ ] Offline transcription using Whisper AI
- [ ] Custom vocabulary support
- [ ] Speaker diarization (identify different speakers)
- [ ] Transcription history export
- [ ] Real-time audio translation (voice-to-voice)
- [ ] Sentiment analysis
- [ ] Meeting summary generation

## Dependencies

- Flask - Web framework
- Flask-SocketIO - WebSocket support
- SpeechRecognition - Speech-to-text
- Deep-Translator - Translation service
- PyDub - Audio processing
- NumPy - Numerical operations

## License

MIT License
