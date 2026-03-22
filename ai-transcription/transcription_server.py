#!/usr/bin/env python3
"""
AI-Powered Real-Time Transcription, Translation & Text-to-Speech Service
Supports continuous audio streaming with language detection, translation, and TTS
"""

import os
import io
import base64
import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Set, Optional
import tempfile
import uuid

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from faster_whisper import WhisperModel
from pydub import AudioSegment
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import numpy as np

# TTS Imports
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning("Edge TTS not available, falling back to other TTS engines")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("Google TTS not available")

try:
    import soundfile as sf
    SOUND_FILE_AVAILABLE = True
except ImportError:
    SOUND_FILE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=False
)

# Global state
transcription_rooms: Dict[str, Set[str]] = {}
user_preferences: Dict[str, Dict] = {}
tts_sessions: Dict[str, Dict] = {}  # Track TTS sessions per user

# TTS Configuration
TTS_ENGINE = os.getenv('TTS_ENGINE', 'edge')  # 'edge', 'google', 'azure'
TTS_VOICE_MAPPING = {
    'en': 'en-US-JennyNeural',  # English
    'es': 'es-ES-ElviraNeural',  # Spanish
    'fr': 'fr-FR-DeniseNeural',  # French
    'de': 'de-DE-KatjaNeural',   # German
    'it': 'it-IT-ElsaNeural',    # Italian
    'pt': 'pt-BR-FranciscaNeural', # Portuguese
    'ru': 'ru-RU-SvetlanaNeural', # Russian
    'ja': 'ja-JP-NanamiNeural',  # Japanese
    'ko': 'ko-KR-SunHiNeural',   # Korean
    'zh': 'zh-CN-XiaoxiaoNeural', # Chinese
    'ar': 'ar-SA-ZariyahNeural',  # Arabic
    'hi': 'hi-IN-SwaraNeural',    # Hindi
    'tr': 'tr-TR-EmelNeural',    # Turkish
    'vi': 'vi-VN-HoaiMyNeural',  # Vietnamese
    'th': 'th-TH-PremwadeeNeural', # Thai
    'nl': 'nl-NL-ColetteNeural', # Dutch
    'pl': 'pl-PL-ZofiaNeural',   # Polish
    'sv': 'sv-SE-SofieNeural',   # Swedish
}

# Performance and Quality Settings
MAX_TTS_LENGTH = 200  # Maximum characters for TTS (optimal for latency)
TTS_RATE = '+0%'  # Speech rate (can be adjusted for tone preservation)
TTS_VOLUME = '+0%'  # Volume level
TTS_PITCH = '+0Hz'  # Pitch adjustment for tone preservation
LOW_LATENCY_MODE = os.getenv('LOW_LATENCY_MODE', 'true').lower() == 'true'

# Load Whisper model
WHISPER_MODEL_SIZE = os.getenv('WHISPER_MODEL', 'base')
logger.info(f"Loading Whisper model: {WHISPER_MODEL_SIZE}")

# Check if CUDA is available
# device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cpu"
logger.info(f"Using device: {device}")

try:
    # whisper_model = whisper.load_model(WHISPER_MODEL_SIZE, device=device)
    whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device=device, compute_type="int8")
    logger.info(f"✅ Whisper model '{WHISPER_MODEL_SIZE}' loaded successfully on {device}")
except Exception as e:
    logger.error(f"❌ Failed to load Whisper model: {e}")
    whisper_model = None

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    'en': 'english',
    'es': 'spanish',
    'fr': 'french',
    'de': 'german',
    'it': 'italian',
    'pt': 'portuguese',
    'ru': 'russian',
    'ja': 'japanese',
    'ko': 'korean',
    'zh-CN': 'chinese (simplified)',
    'ar': 'arabic',
    'hi': 'hindi',
    'bn': 'bengali',
    'ur': 'urdu',
    'tr': 'turkish',
    'vi': 'vietnamese',
    'th': 'thai',
    'nl': 'dutch',
    'pl': 'polish',
    'sv': 'swedish'
}


def convert_audio_to_wav(audio_data: bytes) -> bytes:
    """Convert audio data to WAV format suitable for Whisper"""
    try:
        # Load audio from bytes
        audio = AudioSegment.from_file(io.BytesIO(audio_data))
        
        # Convert to mono, 16kHz (Whisper's expected format)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        
        # Export as WAV
        wav_io = io.BytesIO()
        audio.export(wav_io, format='wav')
        wav_io.seek(0)
        
        return wav_io.read()
    except Exception as e:
        logger.error(f"Error converting audio: {e}")
        raise


def transcribe_audio(audio_data: bytes, source_language: str = 'auto') -> Dict:
    """Transcribe audio using Whisper"""
    if not whisper_model:
        # Dummy response since model not loaded
        return {
            'text': 'Transcription not available (Whisper model not loaded)',
            'language': 'en',
            'success': True
        }
    
    try:
        # Convert audio to WAV format
        wav_data = convert_audio_to_wav(audio_data)
        
        # Save to temporary file (Whisper requires file path)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(wav_data)
            temp_path = temp_file.name
        
        try:
            # Transcribe with Whisper
            if source_language == 'auto':
                segments, info = whisper_model.transcribe(
                    temp_path,
                    language=None  # Auto-detect
                )
            else:
                # Map language code to Whisper language name
                whisper_lang = SUPPORTED_LANGUAGES.get(source_language, 'english')
                segments, info = whisper_model.transcribe(
                    temp_path,
                    language=whisper_lang
                )
            
            text = ''.join([segment.text for segment in segments]).strip()
            detected_language = info.language
            
            logger.info(f"Transcribed: '{text}' (language: {detected_language})")
            
            return {
                'text': text,
                'language': detected_language,
                'success': True
            }
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return {
            'text': '',
            'language': 'unknown',
            'success': False,
            'error': str(e)
        }


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text using Google Translator"""
    if not text or not text.strip():
        return text
    
    # If source and target are the same, no translation needed
    if source_lang == target_lang:
        return text
    
    try:
        # Normalize language codes
        source_lang = source_lang.lower().replace('_', '-')
        target_lang = target_lang.lower().replace('_', '-')
        
        # Use Google Translator
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        
        logger.info(f"Translated '{text}' from {source_lang} to {target_lang}: '{translated}'")
        return translated
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # Return original text if translation fails


async def text_to_speech_edge(text: str, language: str, user_id: str) -> Optional[str]:
    """Convert text to speech using Edge TTS with tone preservation and low latency"""
    if not EDGE_TTS_AVAILABLE or not text or not text.strip():
        return None
    
    try:
        # Truncate text for optimal latency
        if len(text) > MAX_TTS_LENGTH:
            text = text[:MAX_TTS_LENGTH-3] + "..."
        
        # Get voice for language
        voice = TTS_VOICE_MAPPING.get(language, 'en-US-JennyNeural')
        
        # Configure prosody for tone preservation
        prosody_options = {
            'rate': TTS_RATE,
            'volume': TTS_VOLUME,
            'pitch': TTS_PITCH
        }
        
        # Create TTS communication with optimizations
        communicate = edge_tts.Communicate(text, voice, rate=prosody_options['rate'])
        
        # Use streaming for lower latency
        audio_data = await communicate.stream()
        
        # Convert to base64 efficiently
        audio_buffer = io.BytesIO()
        chunk_count = 0
        
        for chunk in audio_data:
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
                chunk_count += 1
                
                # For low latency mode, process chunks as they come
                if LOW_LATENCY_MODE and chunk_count > 5:
                    break
        
        audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode('utf-8')
        
        logger.info(f"TTS generated for {user_id}: {len(text)} chars in {language} ({'low-latency' if LOW_LATENCY_MODE else 'standard'} mode)")
        return audio_base64
        
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
        return None


def text_to_speech_google(text: str, language: str, user_id: str) -> Optional[str]:
    """Convert text to speech using Google TTS"""
    if not GTTS_AVAILABLE or not text or not text.strip():
        return None
    
    try:
        # Normalize language code for gTTS
        lang_code = language.split('-')[0] if '-' in language else language
        
        # Create TTS
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            
            # Read file and convert to base64
            with open(temp_file.name, 'rb') as audio_file:
                audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # Clean up
            os.unlink(temp_file.name)
        
        logger.info(f"Google TTS generated for {user_id}: {len(text)} chars in {language}")
        return audio_base64
        
    except Exception as e:
        logger.error(f"Google TTS error: {e}")
        return None


async def generate_speech_translation(text: str, target_language: str, user_id: str) -> Optional[str]:
    """Generate speech translation for user"""
    if not text or not target_language:
        return None
    
    try:
        # Try Edge TTS first (better quality)
        if TTS_ENGINE == 'edge' and EDGE_TTS_AVAILABLE:
            return await text_to_speech_edge(text, target_language, user_id)
        
        # Fallback to Google TTS
        if GTTS_AVAILABLE:
            return text_to_speech_google(text, target_language, user_id)
        
        logger.warning(f"No TTS engine available for user {user_id}")
        return None
        
    except Exception as e:
        logger.error(f"Speech generation error: {e}")
        return None


@app.route('/')
def index():
    """Health check endpoint"""
    return {
        'status': 'ok',
        'service': 'AI Transcription Service',
        'model': WHISPER_MODEL_SIZE,
        'device': device,
        'timestamp': datetime.now().isoformat()
    }


@app.route('/health')
def health():
    """Detailed health check"""
    return {
        'status': 'healthy',
        'whisper_model': WHISPER_MODEL_SIZE,
        'model_loaded': whisper_model is not None,
        'device': device,
        'cuda_available': torch.cuda.is_available(),
        'active_rooms': len(transcription_rooms),
        'timestamp': datetime.now().isoformat()
    }


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"✅ Client connected: {request.sid}")
    emit('connection_status', {
        'connected': True,
        'model': WHISPER_MODEL_SIZE,
        'device': device
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"❌ Client disconnected: {request.sid}")
    
    # Clean up user from all rooms
    for room_id in list(transcription_rooms.keys()):
        if request.sid in transcription_rooms[room_id]:
            transcription_rooms[room_id].remove(request.sid)
            if not transcription_rooms[room_id]:
                del transcription_rooms[room_id]
    
    # Clean up user preferences
    if request.sid in user_preferences:
        del user_preferences[request.sid]


@socketio.on('join_transcription_room')
def handle_join_room(data):
    """Handle user joining transcription room"""
    room_id = data.get('roomId')
    user_id = data.get('userId')
    user_name = data.get('userName')
    target_language = data.get('targetLanguage', 'en')
    
    if not room_id:
        emit('transcription_error', {'error': 'Room ID required'})
        return
    
    # Join Socket.IO room
    join_room(room_id)
    
    # Track room membership
    if room_id not in transcription_rooms:
        transcription_rooms[room_id] = set()
    transcription_rooms[room_id].add(request.sid)
    
    # Store user preferences
    user_preferences[request.sid] = {
        'roomId': room_id,
        'userId': user_id,
        'userName': user_name,
        'targetLanguage': target_language
    }
    
    logger.info(f"👤 {user_name} joined transcription room {room_id} (target: {target_language})")
    emit('transcription_status', {
        'joined': True,
        'roomId': room_id,
        'message': f'Joined transcription room successfully'
    })


@socketio.on('leave_transcription_room')
def handle_leave_room(data):
    """Handle user leaving transcription room"""
    room_id = data.get('roomId')
    
    if room_id:
        leave_room(room_id)
        
        if room_id in transcription_rooms and request.sid in transcription_rooms[room_id]:
            transcription_rooms[room_id].remove(request.sid)
            if not transcription_rooms[room_id]:
                del transcription_rooms[room_id]
        
        logger.info(f"👋 User left transcription room {room_id}")


@socketio.on('change_target_language')
def handle_language_change(data):
    """Handle user changing target language"""
    room_id = data.get('roomId')
    user_id = data.get('userId')
    target_language = data.get('targetLanguage', 'en')
    
    if request.sid in user_preferences:
        user_preferences[request.sid]['targetLanguage'] = target_language
        logger.info(f"🌐 User {user_id} changed target language to {target_language}")
        
        emit('language_changed', {
            'targetLanguage': target_language,
            'success': True
        })


@socketio.on('stream_audio_chunk')
def handle_audio_chunk(data):
    """Handle incoming audio chunk for transcription"""
    room_id = data.get('roomId')
    user_id = data.get('userId')
    user_name = data.get('userName')
    chunk_data = data.get('chunkData')
    source_language = data.get('sourceLanguage', 'auto')
    
    if not chunk_data:
        emit('transcription_error', {'error': 'No audio data provided'})
        return
    
    if not whisper_model:
        emit('transcription_error', {'error': 'Transcription service not available'})
        return
    
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(chunk_data)
        
        # Check if audio is long enough (at least 0.5 seconds)
        if len(audio_bytes) < 8000:  # Rough estimate for 0.5s at 16kHz
            logger.debug(f"Audio chunk too short, skipping")
            return
        
        # Transcribe audio
        transcription_result = transcribe_audio(audio_bytes, source_language)
        
        if not transcription_result['success']:
            emit('transcription_error', {
                'error': transcription_result.get('error', 'Transcription failed')
            })
            return
        
        original_text = transcription_result['text']
        detected_language = transcription_result['language']
        
        # Skip if no text detected
        if not original_text or len(original_text.strip()) < 2:
            logger.debug(f"No meaningful text detected, skipping")
            return
        
        # Broadcast transcription to all users in the room
        # Each user will receive translation in their preferred language with TTS
        if room_id in transcription_rooms:
            for sid in transcription_rooms[room_id]:
                user_prefs = user_preferences.get(sid, {})
                target_lang = user_prefs.get('targetLanguage', 'en')
                enable_tts = user_prefs.get('enableTTS', False)
                
                # Skip TTS for the original speaker (avoid echo)
                is_speaker = (sid == user_id)
                
                # Translate if needed
                if detected_language != target_lang:
                    translated_text = translate_text(original_text, detected_language, target_lang)
                else:
                    translated_text = original_text
                
                # Send transcription result to user
                transcription_data = {
                    'userId': user_id,
                    'userName': user_name,
                    'originalText': original_text,
                    'translatedText': translated_text,
                    'sourceLanguage': detected_language,
                    'targetLanguage': target_lang,
                    'timestamp': datetime.now().isoformat(),
                    'isSpeaker': is_speaker
                }
                
                socketio.emit('transcription_result', transcription_data, room=sid)
                
                # Generate and send TTS if enabled and not the speaker
                if enable_tts and not is_speaker and translated_text and translated_text.strip():
                    # Run TTS generation asynchronously to avoid blocking
                    socketio.start_background_task(
                        generate_and_send_tts,
                        translated_text,
                        target_lang,
                        sid,
                        user_id,
                        user_name
                    )
        
        logger.info(f"📝 Transcribed from {user_name}: '{original_text}' ({detected_language})")
        
    except Exception as e:
        logger.error(f"Error processing audio chunk: {e}", exc_info=True)
        emit('transcription_error', {
            'error': f'Failed to process audio: {str(e)}'
        })


def generate_and_send_tts(text: str, target_language: str, target_sid: str, original_user_id: str, original_user_name: str):
    """Background task to generate TTS and send to specific user"""
    try:
        # Generate speech asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        audio_base64 = loop.run_until_complete(
            generate_speech_translation(text, target_language, target_sid)
        )
        
        loop.close()
        
        if audio_base64:
            # Send TTS audio to specific user
            socketio.emit('tts_audio', {
                'userId': original_user_id,
                'userName': original_user_name,
                'audioData': audio_base64,
                'text': text,
                'language': target_language,
                'timestamp': datetime.now().isoformat()
            }, room=target_sid)
            
            logger.info(f"🔊 TTS sent to {target_sid}: {text[:50]}...")
        else:
            logger.debug(f"TTS generation failed for {target_sid}")
            
    except Exception as e:
        logger.error(f"TTS background task error: {e}")


@socketio.on('toggle_tts')
def handle_toggle_tts(data):
    """Handle user toggling TTS on/off"""
    user_id = data.get('userId')
    enable_tts = data.get('enableTTS', False)
    
    if request.sid in user_preferences:
        user_preferences[request.sid]['enableTTS'] = enable_tts
        logger.info(f"🔊 TTS {'enabled' if enable_tts else 'disabled'} for user {user_id}")
        
        emit('tts_status', {
            'enabled': enable_tts,
            'message': f'TTS {"enabled" if enable_tts else "disabled"}'
        })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting AI Transcription Service on {host}:{port}")
    logger.info(f"📊 Whisper Model: {WHISPER_MODEL_SIZE}")
    logger.info(f"🖥️  Device: {device}")
    
    socketio.run(
        app,
        host=host,
        port=port,
        debug=False,
        use_reloader=False
    )
