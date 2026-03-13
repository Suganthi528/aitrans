# HiiMeet Setup Guide - Complete Installation

This guide will help you set up the complete HiiMeet video meeting platform with AI transcription and translation.

## Prerequisites

### Required Software

1. **Node.js** (v14 or higher)
   - Download from: https://nodejs.org/
   - Verify: `node --version`

2. **Python** (v3.8 or higher)
   - Download from: https://www.python.org/
   - Verify: `python --version`
   - Make sure to check "Add Python to PATH" during installation

3. **npm** (comes with Node.js)
   - Verify: `npm --version`

4. **pip** (comes with Python)
   - Verify: `pip --version`

## Installation Steps

### Step 1: Install Backend Dependencies

```bash
cd hiimeet/backend
npm install
```

### Step 2: Install Frontend Dependencies

```bash
cd hiimeet/video-meet/frontend-videocall
npm install
```

### Step 3: Install AI Transcription Service

```bash
cd hiimeet/ai-transcription
install.bat
```

Or manually:
```bash
pip install -r requirements.txt
copy .env.example .env
```

### Step 4: Configure Environment Variables

**Backend** (`hiimeet/backend/.env`):
```env
PORT=5001
HOST=0.0.0.0
```

**Frontend** (`hiimeet/video-meet/frontend-videocall/.env`):
```env
REACT_APP_BACKEND_URL=http://localhost:5001
REACT_APP_TRANSCRIPTION_SERVER=http://localhost:5002
```

**AI Service** (`hiimeet/ai-transcription/.env`):
```env
TRANSCRIPTION_PORT=5002
FLASK_ENV=development
```

## Running the Application

### Option 1: Start All Services at Once (Recommended)

```bash
cd hiimeet
start-all.bat
```

This will open 3 terminal windows:
- Backend Server (Port 5001)
- AI Transcription Service (Port 5002)
- Frontend Application (Port 3000)

### Option 2: Start Services Individually

**Terminal 1 - Backend:**
```bash
cd hiimeet/backend
npm start
```

**Terminal 2 - AI Transcription:**
```bash
cd hiimeet/ai-transcription
python transcription_service.py
```

**Terminal 3 - Frontend:**
```bash
cd hiimeet/video-meet/frontend-videocall
npm start
```

## Accessing the Application

Once all services are running:

1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:5001
3. **AI Service**: http://localhost:5002

The frontend will automatically open in your default browser.

## Using the AI Transcription Feature

1. Join or create a meeting room
2. Click the "🎤 Show Transcription" button
3. Select your preferred language from the dropdown
4. Click "Start Transcription" to begin
5. Speak into your microphone
6. See real-time transcriptions and translations

## Features Overview

### Video Meeting Features
- ✅ Real-time video and audio communication
- ✅ Screen sharing
- ✅ Text chat
- ✅ Participant management
- ✅ Reactions and hand raising
- ✅ Collaborative whiteboard
- ✅ Meeting scheduling
- ✅ Admin controls

### AI Transcription Features
- ✅ Real-time speech-to-text
- ✅ Automatic language translation (20+ languages)
- ✅ Live transcription feed
- ✅ Multi-participant support
- ✅ Language auto-detection

## Troubleshooting

### Backend Issues

**Port already in use:**
- The backend will automatically try ports 5001-5012
- Or manually change PORT in backend/.env

**Dependencies not installed:**
```bash
cd backend
npm install
```

### Frontend Issues

**Port 3000 in use:**
- Kill the process using port 3000
- Or the app will prompt to use another port

**Module not found:**
```bash
cd video-meet/frontend-videocall
npm install
```

### AI Transcription Issues

**Python not found:**
- Install Python from python.org
- Make sure Python is added to PATH

**pip install fails:**
- Update pip: `pip install --upgrade pip`
- Try: `pip install -r requirements.txt --user`

**Microphone not working:**
- Check browser permissions
- Allow microphone access when prompted
- Use HTTPS in production

**Translation not working:**
- Check internet connection
- Translation requires online API access

### Common Errors

**EADDRINUSE Error:**
- Port is already in use
- Close other applications using the port
- Or change the port in .env file

**Module not found:**
- Run `npm install` in the respective directory
- Delete node_modules and package-lock.json, then reinstall

**WebSocket connection failed:**
- Ensure all services are running
- Check firewall settings
- Verify correct URLs in .env files

## System Requirements

### Minimum Requirements
- CPU: Dual-core processor
- RAM: 4GB
- Storage: 500MB free space
- Internet: Broadband connection

### Recommended Requirements
- CPU: Quad-core processor
- RAM: 8GB or more
- Storage: 1GB free space
- Internet: High-speed broadband

## Browser Compatibility

### Supported Browsers
- ✅ Google Chrome (recommended)
- ✅ Microsoft Edge
- ✅ Firefox
- ✅ Safari (macOS)
- ✅ Opera

### Required Browser Features
- WebRTC support
- WebSocket support
- MediaRecorder API
- Microphone/Camera access

## Development Tips

### Hot Reload
- Frontend has hot reload enabled
- Backend requires restart for changes
- AI service requires restart for changes

### Debugging
- Check browser console for frontend errors
- Check terminal output for backend/AI errors
- Use browser DevTools Network tab for API calls

### Testing
- Test with multiple browser tabs for multi-user scenarios
- Use incognito mode for separate user sessions
- Test microphone permissions in different browsers

## Production Deployment

### Security Checklist
- [ ] Use HTTPS for all services
- [ ] Set up proper CORS policies
- [ ] Implement authentication
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging

### Performance Optimization
- [ ] Enable production build for React
- [ ] Use CDN for static assets
- [ ] Implement caching strategies
- [ ] Optimize database queries
- [ ] Use load balancing for scaling

### Deployment Platforms
- Frontend: Vercel, Netlify, AWS S3
- Backend: Heroku, AWS EC2, DigitalOcean
- AI Service: AWS EC2, Google Cloud, Azure

## Additional Resources

- **Backend Documentation**: See backend/README.md
- **AI Service Documentation**: See ai-transcription/README.md
- **Integration Guide**: See AI_TRANSCRIPTION_INTEGRATION.md
- **Feature Documentation**: See various .md files in root

## Getting Help

If you encounter issues:

1. Check this guide first
2. Review error messages in terminal/console
3. Verify all dependencies are installed
4. Ensure all services are running
5. Check firewall and network settings

## Next Steps

After successful setup:

1. Explore the video meeting features
2. Test the AI transcription with different languages
3. Customize the UI to match your brand
4. Add additional features as needed
5. Deploy to production when ready

## License

MIT License - Free to use and modify

---

**Happy Meeting! 🎉**
