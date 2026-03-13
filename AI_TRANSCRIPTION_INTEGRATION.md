# AI Transcription & Translation Integration Guide

## Overview

This document explains how to integrate the AI-powered real-time transcription and translation feature into your video meeting application.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Frontend      │◄───────►│   Backend        │◄───────►│  AI Service     │
│   (React)       │         │   (Node.js)      │         │  (Python)       │
│   Port 3000     │         │   Port 5001      │         │  Port 5002      │
└─────────────────┘         └──────────────────┘         └─────────────────┘
       │                                                          │
       │                                                          │
       └──────────────────────────────────────────────────────────┘
                    WebSocket Connection for Real-time
                    Audio Streaming & Transcription
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd hiimeet/ai-transcription
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Frontend `.env` file already updated with:
```
REACT_APP_TRANSCRIPTION_SERVER=http://localhost:5002
```

### 3. Start All Services

Use the convenient start script:
```bash
cd hiimeet
start-all.bat
```

Or start services individually:

**Backend:**
```bash
cd backend
npm start
```

**AI Transcription Service:**
```bash
cd ai-transcription
python transcription_service.py
```

**Frontend:**
```bash
cd video-meet/frontend-videocall
npm start
```

## Integration into Videoroom Component

Add the TranscriptionPanel to your Videoroom.js:

```javascript
import TranscriptionPanel from './TranscriptionPanel';

// Inside your Videoroom component
const [showTranscription, setShowTranscription] = useState(false);

// In your JSX
<div className="meeting-container">
  {/* Your existing video grid */}
  
  {showTranscription && (
    <TranscriptionPanel
      roomId={roomId}
      userId={socketRef.current?.id}
      userName={userName}
      isEnabled={showTranscription}
    />
  )}
  
  {/* Add toggle button */}
  <button onClick={() => setShowTranscription(!showTranscription)}>
    {showTranscription ? '🔇 Hide Transcription' : '🎤 Show Transcription'}
  </button>
</div>
```

## Features

### For Users

1. **Select Target Language**: Choose which language you want to see translations in
2. **Start Transcription**: Click the microphone button to begin real-time transcription
3. **View Live Feed**: See transcriptions and translations from all participants
4. **Automatic Translation**: Speech is automatically translated to your chosen language

### For Developers

1. **Easy Integration**: Drop-in React component
2. **WebSocket Communication**: Real-time bidirectional communication
3. **Scalable Architecture**: Python service can be deployed separately
4. **Multiple Language Support**: 20+ languages out of the box
5. **Error Handling**: Graceful fallbacks for translation failures

## How It Works

### Audio Flow

1. User speaks into microphone
2. Frontend captures audio using MediaRecorder API
3. Audio is encoded to base64 and sent via WebSocket
4. Python service receives and processes audio
5. Google Speech Recognition transcribes audio to text
6. Deep Translator translates text to each participant's language
7. Translated text is broadcast back to all participants
8. Frontend displays transcription in real-time

### Language Detection

- Automatic language detection for source audio
- Manual language selection for target translation
- Fallback to original text if translation fails

## API Reference

### TranscriptionPanel Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| roomId | string | Yes | Meeting room identifier |
| userId | string | Yes | Current user's ID |
| userName | string | Yes | Current user's name |
| isEnabled | boolean | Yes | Enable/disable transcription |

### WebSocket Events

**Emit Events:**
- `join_transcription_room` - Join transcription session
- `transcribe_audio` - Send audio for transcription
- `change_target_language` - Update translation language

**Listen Events:**
- `transcription_result` - Receive transcribed/translated text
- `transcription_error` - Handle errors
- `connection_status` - Monitor connection

## Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| en | English | es | Spanish |
| fr | French | de | German |
| it | Italian | pt | Portuguese |
| ru | Russian | ja | Japanese |
| ko | Korean | zh-CN | Chinese |
| ar | Arabic | hi | Hindi |
| bn | Bengali | ur | Urdu |
| tr | Turkish | vi | Vietnamese |
| th | Thai | nl | Dutch |
| pl | Polish | sv | Swedish |

## Performance Considerations

### Audio Processing
- Audio chunks are processed every 5 seconds
- Keeps last 50 transcriptions in memory
- Automatic cleanup on disconnect

### Network Usage
- WebSocket for efficient bidirectional communication
- Base64 encoding for audio transmission
- Compressed audio chunks to reduce bandwidth

### Scalability
- Python service can be deployed on separate server
- Multiple instances can be load-balanced
- Redis can be added for session management

## Troubleshooting

### Transcription Not Working

1. **Check Microphone Permissions**
   - Browser must have microphone access
   - Check browser settings

2. **Verify Service Connection**
   - Ensure AI service is running on port 5002
   - Check console for connection errors

3. **Network Issues**
   - Verify WebSocket connection
   - Check firewall settings

### Translation Errors

1. **Internet Connection**
   - Translation requires online API access
   - Check network connectivity

2. **Language Support**
   - Verify language code is supported
   - Some languages have limited support

### Audio Quality Issues

1. **Microphone Quality**
   - Use good quality microphone
   - Reduce background noise

2. **Network Latency**
   - Check network speed
   - Consider local deployment for better performance

## Production Deployment

### Security Considerations

1. **HTTPS Required**
   - Microphone access requires HTTPS in production
   - Use SSL certificates

2. **API Keys**
   - Consider using paid translation APIs for better reliability
   - Implement rate limiting

3. **Authentication**
   - Add authentication to transcription service
   - Validate room access

### Scaling

1. **Separate Deployment**
   - Deploy Python service independently
   - Use container orchestration (Docker/Kubernetes)

2. **Load Balancing**
   - Multiple AI service instances
   - WebSocket sticky sessions

3. **Caching**
   - Cache common translations
   - Use Redis for session management

## Future Enhancements

- [ ] Offline mode using Whisper AI
- [ ] Voice-to-voice translation
- [ ] Meeting transcription export (PDF, TXT)
- [ ] Speaker identification
- [ ] Sentiment analysis
- [ ] AI-generated meeting summaries
- [ ] Custom vocabulary/terminology
- [ ] Real-time closed captions overlay

## Support

For issues or questions:
1. Check the console logs
2. Verify all services are running
3. Review the README.md in ai-transcription folder
4. Check network connectivity

## License

MIT License - Free to use and modify
