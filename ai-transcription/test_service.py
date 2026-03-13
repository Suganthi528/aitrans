"""
Simple test script to verify the transcription service is working
"""
import requests
import json

TRANSCRIPTION_SERVER = 'http://localhost:5002'

def test_health():
    """Test if the service is running"""
    try:
        response = requests.get(f'{TRANSCRIPTION_SERVER}/health')
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to service: {str(e)}")
        print(f"   Make sure the service is running on {TRANSCRIPTION_SERVER}")
        return False

def test_languages():
    """Test if languages endpoint works"""
    try:
        response = requests.get(f'{TRANSCRIPTION_SERVER}/languages')
        if response.status_code == 200:
            data = response.json()
            languages = data.get('languages', {})
            print(f"✅ Languages endpoint working")
            print(f"   Supported languages: {len(languages)}")
            print(f"   Sample languages: {list(languages.items())[:5]}")
            return True
        else:
            print(f"❌ Languages endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing languages: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("AI Transcription Service - Test Suite")
    print("=" * 50)
    print()
    
    print("Testing service endpoints...")
    print()
    
    # Test health endpoint
    health_ok = test_health()
    print()
    
    # Test languages endpoint
    languages_ok = test_languages()
    print()
    
    # Summary
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Languages:    {'✅ PASS' if languages_ok else '❌ FAIL'}")
    print()
    
    if health_ok and languages_ok:
        print("🎉 All tests passed! Service is ready to use.")
        print()
        print("Next steps:")
        print("1. Start the backend server (npm start in backend folder)")
        print("2. Start the frontend (npm start in frontend folder)")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("⚠️  Some tests failed. Please check:")
        print("1. Is the service running? (python transcription_service.py)")
        print("2. Is it running on the correct port? (default: 5002)")
        print("3. Are all dependencies installed? (pip install -r requirements.txt)")
    
    print()

if __name__ == '__main__':
    main()
