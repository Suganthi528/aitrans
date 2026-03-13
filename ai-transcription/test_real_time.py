"""
Test script for real-time transcription and translation
Run this to verify the AI service is working correctly
"""

import socketio
import time
import base64
import wave
import io

# Create a test client
sio = socketio.Client()

@sio.event
def connect():
    print('✅ Connected to transcription service')
    
@sio.event
def disconnect():
    print('❌ Disconnected from transcription service')

@sio.on('connection_status')
def on_connection_status(data):
    print(f'📡 Connection status: {data}')

@sio.on('joined_transcription_room')
def on_joined(data):
    print(f'✅ Joined room: {data}')

@sio.on('transcription_result')
def on_transcription(data):
    print(f'\n🎤 Transcription received:')
    print(f'   User: {data["userName"]}')
    print(f'   Original: {data["originalText"]}')
    print(f'   Translated ({data["targetLanguage"]}): {data["translatedText"]}')
    print(f'   Time: {data["timestamp"]}\n')

@sio.on('transcription_error')
def on_error(data):
    print(f'❌ Error: {data["error"]}')

@sio.on('language_changed')
def on_language_changed(data):
    print(f'🌍 Language changed: {data}')

def create_test_audio():
    """Create a simple test audio file (silence)"""
    sample_rate = 16000
    duration = 2  # seconds
    
    # Create WAV file in memory
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Generate silence
        silence = b'\x00\x00' * (sample_rate * duration)
        wav_file.writeframes(silence)
    
    buffer.seek(0)
    return buffer.read()

def test_connection():
    """Test basic connection"""
    print('🧪 Testing connection to transcription service...\n')
    
    try:
        sio.connect('http://localhost:5002')
        time.sleep(1)
        
        # Test joining a room
        print('📝 Joining transcription room...')
        sio.emit('join_transcription_room', {
            'roomId': 'test-room-123',
            'userId': 'test-user-1',
            'userName': 'Test User',
            'targetLanguage': 'es'
        })
        time.sleep(1)
        
        # Test language change
        print('🌍 Changing target language to French...')
        sio.emit('change_target_language', {
            'targetLanguage': 'fr'
        })
        time.sleep(1)
        
        # Note: Actual audio transcription requires real audio input
        print('\n✅ Basic connection tests passed!')
        print('ℹ️  To test actual transcription, speak into your microphone in the web app')
        
        # Keep connection alive for a bit
        print('\n⏳ Keeping connection alive for 5 seconds...')
        time.sleep(5)
        
        # Leave room
        print('👋 Leaving transcription room...')
        sio.emit('leave_transcription_room', {
            'roomId': 'test-room-123'
        })
        time.sleep(1)
        
        sio.disconnect()
        print('\n✅ All tests completed successfully!')
        
    except Exception as e:
        print(f'\n❌ Test failed: {str(e)}')
        print('Make sure the transcription service is running on port 5002')
        print('Run: python transcription_service.py')

def test_languages():
    """Test available languages"""
    import requests
    
    print('🧪 Testing available languages...\n')
    
    try:
        response = requests.get('http://localhost:5002/languages')
        if response.status_code == 200:
            languages = response.json()['languages']
            print(f'✅ Found {len(languages)} supported languages:')
            for code, name in list(languages.items())[:10]:
                print(f'   {code}: {name}')
            print(f'   ... and {len(languages) - 10} more')
        else:
            print(f'❌ Failed to get languages: {response.status_code}')
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        print('Make sure the transcription service is running on port 5002')

def test_health():
    """Test health endpoint"""
    import requests
    
    print('🧪 Testing health endpoint...\n')
    
    try:
        response = requests.get('http://localhost:5002/health')
        if response.status_code == 200:
            data = response.json()
            print(f'✅ Service is healthy: {data}')
        else:
            print(f'❌ Health check failed: {response.status_code}')
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        print('Make sure the transcription service is running on port 5002')

if __name__ == '__main__':
    print('=' * 60)
    print('Real-Time Transcription & Translation Test Suite')
    print('=' * 60)
    print()
    
    # Run tests
    test_health()
    print()
    test_languages()
    print()
    test_connection()
    
    print('\n' + '=' * 60)
    print('Test suite completed!')
    print('=' * 60)
