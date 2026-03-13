import os
import io
import json
import wave
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import speech_recognition as sr
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import numpy as np
from collections import defaultdict

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Store user language preferences
user_languages = {}
room_participants = defaultdict(set)
active_transcriptions = {}

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh-CN': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'nl': 'Dutch',
    'pl': 'Polish',
    'sv': 'Swedish'
}

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300  # Lower threshold for faster detection
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.5  # Shorter pause detection

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'AI Transcription Service'})

@app.route('/languages', methods=['GET'])
def get_languages():
    return jsonify({'languages': SUPPORTED_LANGUAGES})

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connection_status', {'status': 'connected', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    # Clean up user data
    if request.sid in user_languages:
        del user_languages[request.sid]
    
    # Remove from all rooms
    for room_id in list(room_participants.keys()):
        if request.sid in room_participants[room_id]:
            room_participants[room_id].remove(request.sid)
            if len(room_participants[room_id]) == 0:
                del room_participants[room_id]

@socketio.on('join_transcription_room')
def handle_join_room(data):
    room_id = data.get('roomId')
    user_id = data.get('userId')
    user_name = data.get('userName')
    target_language = data.get('targetLanguage', 'en')
    
    join_room(room_id)
    room_participants[room_id].add(request.sid)
    
    user_languages[request.sid] = {
        'userId': user_id,
        'userName': user_name,
        'roomId': room_id,
        'targetLanguage': target_language,
        'sourceLanguage': 'auto'
    }
    
    print(f'{user_name} joined transcription room {room_id} with target language: {target_language}')
    
    emit('joined_transcription_room', {
        'roomId': room_id,
        'targetLanguage': target_language,
        'message': 'Successfully joined transcription service'
    })

@socketio.on('leave_transcription_room')
def handle_leave_room(data):
    room_id = data.get('roomId')
    leave_room(room_id)
    
    if request.sid in room_participants[room_id]:
        room_participants[room_id].remove(request.sid)
    
    if request.sid in user_languages:
        del user_languages[request.sid]
    
    emit('left_transcription_room', {'roomId': room_id})

@socketio.on('change_target_language')
def handle_change_language(data):
    target_language = data.get('targetLanguage')
    
    if request.sid in user_languages:
        user_languages[request.sid]['targetLanguage'] = target_language
        emit('language_changed', {
            'targetLanguage': target_language,
            'message': f'Target language changed to {SUPPORTED_LANGUAGES.get(target_language, target_language)}'
        })

@socketio.on('transcribe_audio')
def handle_transcribe_audio(data):
    try:
        room_id = data.get('roomId')
        audio_data = data.get('audioData')
        user_id = data.get('userId')
        user_name = data.get('userName')
        source_language = data.get('sourceLanguage', 'en')
        
        if not audio_data:
            emit('transcription_error', {'error': 'No audio data provided'})
            return
        
        # Convert base64 audio to bytes
        import base64
        audio_bytes = base64.b64decode(audio_data)
        
        # Perform speech recognition
        audio_file = io.BytesIO(audio_bytes)
        
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        
        # Recognize speech using Google Speech Recognition
        try:
            # Detect language automatically if set to auto
            if source_language == 'auto':
                original_text = recognizer.recognize_google(audio)
            else:
                original_text = recognizer.recognize_google(audio, language=source_language)
            
            print(f'Transcribed: {original_text} (from {user_name})')
            
            # Detect the actual source language
            detected_source_lang = 'en'  # default
            try:
                from deep_translator import single_detection
                detected_source_lang = single_detection(original_text, api_key='auto')
                print(f'🔍 Detected source language: {detected_source_lang}')
            except:
                detected_source_lang = 'en'
            
            # Send original transcription to all participants
            transcription_data = {
                'roomId': room_id,
                'userId': user_id,
                'userName': user_name,
                'originalText': original_text,
                'sourceLanguage': detected_source_lang,
                'timestamp': data.get('timestamp')
            }
            
            # Translate for each participant based on their target language
            for participant_sid in room_participants.get(room_id, []):
                if participant_sid in user_languages:
                    target_lang = user_languages[participant_sid]['targetLanguage']
                    
                    # Always translate to target language
                    try:
                        translated_text = GoogleTranslator(
                            source='auto', 
                            target=target_lang
                        ).translate(original_text)
                        
                        socketio.emit('transcription_result', {
                            **transcription_data,
                            'translatedText': translated_text,
                            'targetLanguage': target_lang
                        }, room=participant_sid)
                    except Exception as e:
                        print(f'Translation error: {str(e)}')
                        # Send original text if translation fails
                        socketio.emit('transcription_result', {
                            **transcription_data,
                            'translatedText': original_text,
                            'targetLanguage': target_lang,
                            'translationError': True
                        }, room=participant_sid)
            
        except sr.UnknownValueError:
            emit('transcription_error', {'error': 'Could not understand audio'})
        except sr.RequestError as e:
            emit('transcription_error', {'error': f'Speech recognition service error: {str(e)}'})
            
    except Exception as e:
        print(f'Transcription error: {str(e)}')
        emit('transcription_error', {'error': str(e)})

@socketio.on('stream_audio_chunk')
def handle_audio_stream(data):
    """Handle real-time audio streaming for continuous transcription"""
    try:
        room_id = data.get('roomId')
        user_id = data.get('userId')
        user_name = data.get('userName')
        chunk_data = data.get('chunkData')
        is_final = data.get('isFinal', False)
        source_language = data.get('sourceLanguage', 'auto')
        
        # Store chunks for this user
        if user_id not in active_transcriptions:
            active_transcriptions[user_id] = {
                'chunks': [],
                'room_id': room_id,
                'user_name': user_name,
                'source_language': source_language
            }
        
        active_transcriptions[user_id]['chunks'].append(chunk_data)
        
        # Process when final chunk is received or buffer is large enough
        if is_final or len(active_transcriptions[user_id]['chunks']) >= 5:
            # Combine all chunks and process
            try:
                import base64
                combined_audio = b''.join([
                    base64.b64decode(chunk) 
                    for chunk in active_transcriptions[user_id]['chunks']
                ])
                
                # Process the combined audio
                process_audio_transcription(
                    room_id=room_id,
                    audio_bytes=combined_audio,
                    user_id=user_id,
                    user_name=user_name,
                    source_language=source_language
                )
                
                # Clear chunks if final, otherwise keep last 2 for continuity
                if is_final:
                    del active_transcriptions[user_id]
                else:
                    active_transcriptions[user_id]['chunks'] = active_transcriptions[user_id]['chunks'][-2:]
                    
            except Exception as e:
                print(f'Audio processing error: {str(e)}')
                if user_id in active_transcriptions:
                    del active_transcriptions[user_id]
            
    except Exception as e:
        print(f'Audio streaming error: {str(e)}')
        emit('transcription_error', {'error': str(e)})

def process_audio_transcription(room_id, audio_bytes, user_id, user_name, source_language='auto'):
    """Process audio bytes and transcribe with translation"""
    try:
        # Convert audio bytes to AudioFile
        audio_file = io.BytesIO(audio_bytes)
        
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        
        # Recognize speech
        try:
            if source_language == 'auto':
                original_text = recognizer.recognize_google(audio)
            else:
                original_text = recognizer.recognize_google(audio, language=source_language)
            
            if not original_text or len(original_text.strip()) == 0:
                return
            
            print(f'🎤 Transcribed: "{original_text}" (from {user_name})')
            
            # Detect the actual source language using GoogleTranslator
            detected_source_lang = 'en'  # default
            try:
                from deep_translator import single_detection
                detected_source_lang = single_detection(original_text, api_key='auto')
                print(f'🔍 Detected source language: {detected_source_lang}')
            except:
                # Fallback: assume English if detection fails
                detected_source_lang = 'en'
            
            # Prepare transcription data
            transcription_data = {
                'roomId': room_id,
                'userId': user_id,
                'userName': user_name,
                'originalText': original_text,
                'sourceLanguage': detected_source_lang,
                'timestamp': int(threading.current_thread().ident)
            }
            
            # Translate for each participant based on their target language
            for participant_sid in room_participants.get(room_id, []):
                if participant_sid in user_languages:
                    target_lang = user_languages[participant_sid]['targetLanguage']
                    
                    # Always translate to target language (GoogleTranslator handles same-language gracefully)
                    try:
                        translated_text = GoogleTranslator(
                            source='auto', 
                            target=target_lang
                        ).translate(original_text)
                        
                        socketio.emit('transcription_result', {
                            **transcription_data,
                            'translatedText': translated_text,
                            'targetLanguage': target_lang
                        }, room=participant_sid)
                        
                        print(f'📝 Translated to {target_lang}: "{translated_text}"')
                    except Exception as e:
                        print(f'Translation error for {target_lang}: {str(e)}')
                        # Send original text if translation fails
                        socketio.emit('transcription_result', {
                            **transcription_data,
                            'translatedText': original_text,
                            'targetLanguage': target_lang,
                            'translationError': True
                        }, room=participant_sid)
            
        except sr.UnknownValueError:
            # Silent or unclear audio - don't emit error
            pass
        except sr.RequestError as e:
            print(f'Speech recognition service error: {str(e)}')
            
    except Exception as e:
        print(f'Transcription processing error: {str(e)}')

if __name__ == '__main__':
    port = int(os.getenv('TRANSCRIPTION_PORT', 5002))
    print(f'🤖 AI Transcription Service starting on port {port}')
    print(f'📝 Supported languages: {len(SUPPORTED_LANGUAGES)}')
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
