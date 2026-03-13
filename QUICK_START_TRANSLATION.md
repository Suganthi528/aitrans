# Quick Start: Real-Time Translation

Get your AI-powered real-time transcription and translation running in 5 minutes!

## Step 1: Install Python Dependencies (2 minutes)

```bash
cd hiimeet/ai-transcription
pip install -r requirements.txt
```

**Note:** If you encounter issues with PyAudio on Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

## Step 2: Start All Services (1 minute)

### Option A: Use the Batch Script (Easiest)

```bash
cd hiimeet
start-all.bat
```

This will start:
- Backend server (port 5001)
- AI Transcription service (port 5002)
- Frontend (port 3000)

### Option B: Start Manually

**Terminal 1 - Backend:**
```bash
cd hiimeet/backend
npm start
```

**Terminal 2 - AI Service:**
```bash
cd hiimeet/ai-transcription
python transcription_service.py
```

**Terminal 3 - Frontend:**
```bash
cd hiimeet/video-meet/frontend-videocall
npm start
```

## Step 3: Test the Service (1 minute)

Run the test script to verify everything works:

```bash
cd hiimeet/ai-transcription
python test_real_time.py
```

You should see:
```
✅ Service is healthy
✅ Found 20 supported languages
✅ Connected to transcription service
✅ All tests completed successfully!
```

## Step 4: Integrate into Your App (1 minute)

Add to your Videoroom component:

```javascript
import RealTimeTranscription from './RealTimeTranscription';

// In your component
const [showTranscription, setShowTranscription] = useState(false);

// In your JSX
<button onClick={() => setShowTranscription(!showTranscription)}>
  {showTranscription ? '🔇 Hide' : '🎤 Show'} Transcription
</button>

<RealTimeTranscription
  roomId={roomId}
  userId={socketRef.current?.id}
  userName={userName}
  isEnabled={showTranscription}
/>
```

## Step 5: Use It! (30 seconds)

1. Open your meeting app at `http://localhost:3000`
2. Join or create a meeting
3. Click "Show Transcription" button
4. Select your preferred language
5. Click "Start Recording"
6. Speak and watch the magic happen! ✨

## Troubleshooting

### Service Won't Start

**Problem:** Port already in use

**Solution:**
```bash
# Check what's using the port
netstat -ano | findstr :5002

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### No Transcription Appearing

**Problem:** Microphone not working

**Solution:**
1. Check browser permissions (allow microphone)
2. Ensure you're using HTTPS in production
3. Try Chrome or Edge browser
4. Check if another app is using the microphone

### Translation Not Working

**Problem:** Internet connection required

**Solution:**
- Ensure stable internet connection
- Google APIs are used for translation
- Check firewall settings

## What You Get

✅ **Real-time speech-to-text** - Continuous transcription every 3 seconds
✅ **Automatic translation** - 20+ languages supported
✅ **Multi-participant** - Everyone sees translations in their language
✅ **Easy integration** - Drop-in React component
✅ **Production ready** - Scalable architecture

## Example Usage

**Scenario:** International team meeting

- **John (USA)** speaks English → Everyone sees it in their language
- **Maria (Spain)** speaks Spanish → Translated to English, French, etc.
- **Yuki (Japan)** speaks Japanese → Translated for all participants
- **Everyone** sees real-time transcriptions in their chosen language!

## Next Steps

- Read the full guide: `REAL_TIME_TRANSLATION_GUIDE.md`
- Customize the UI in `RealTimeTranscription.css`
- Add more languages if needed
- Deploy to production

## Support

Having issues? Check:
1. All services are running (3 terminals)
2. Ports 3000, 5001, 5002 are available
3. Python dependencies installed correctly
4. Internet connection is stable

## Performance Tips

- Use good quality microphone
- Reduce background noise
- Speak clearly at moderate pace
- Ensure stable internet connection
- Close unnecessary browser tabs

---

**That's it! You're ready to break language barriers in your meetings! 🌍🎉**
