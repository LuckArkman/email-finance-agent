import pytest
import requests
import time
import os

GATEWAY_URL = "http://localhost:5000"
AUDIO_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def auth_token():
    # Attempt to register/login
    try:
        reg_resp = requests.post(f"{GATEWAY_URL}/api/hermes/auth/register", json={
            "email": "test_e2e@example.com",
            "password": "Password123!",
            "firstName": "TestUser"
        })
    except Exception:
        pass
        
    resp = requests.post(f"{GATEWAY_URL}/api/hermes/auth/login", json={
        "email": "test_e2e@example.com",
        "password": "Password123!"
    })
    
    if resp.status_code == 200:
        return resp.json().get("token")
    return None

def test_auth_flow(auth_token):
    assert auth_token is not None, "Auth flow failed, could not get JWT token."

def test_agent_chat_flow(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "messages": [
            {"role": "user", "content": "Olá, isto é um teste end-to-end. Responde apenas com a palavra CONFIRMADO."}
        ]
    }
    
    # Wait for agent to be responsive
    time.sleep(2)
    resp = requests.post(f"{GATEWAY_URL}/api/hermes/agent/chat", json=payload, headers=headers)
    assert resp.status_code == 200, f"Chat failed: {resp.text}"
    
    data = resp.json()
    assert "reply" in data
    assert "CONFIRMADO" in data["reply"].upper()

def test_audio_stt_tts_flow():
    # Generate a dummy valid OGG file by creating a small WAV file and passing it to the STT endpoint.
    # The STT endpoint doesn't strictly care if it's OGG or WAV because Whisper handles it via FFmpeg.
    test_audio_path = "test_audio.wav"
    import wave, struct, math
    with wave.open(test_audio_path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        # Just a short tone
        for i in range(16000):
            value = int(32767 * 0.3 * math.sin(2 * math.pi * 440 * i / 16000))
            f.writeframes(struct.pack('<h', value))
            
    with open(test_audio_path, 'rb') as f:
        files = {'file': ('test_audio.wav', f, 'audio/wav')}
        resp = requests.post(f"{AUDIO_URL}/transcribe", files=files)
        
    assert resp.status_code == 200, f"STT failed: {resp.text}"
    data = resp.json()
    assert "text" in data
    
    # Now test TTS
    data = {
        "text": "Teste de síntese de voz",
        "language": "pt"
    }
    resp = requests.post(f"{AUDIO_URL}/synthesize", data=data)
    assert resp.status_code == 200, f"TTS failed: {resp.text}"
    assert resp.headers['Content-Type'] == 'audio/wav'
    assert len(resp.content) > 1000 # ensure it actually returned audio bytes

def test_whatsapp_text_message():
    payload = {
        "sender_phone": "351999999999",
        "text": "Este é um teste automatizado pelo E2E"
    }
    
    resp = requests.post(f"{GATEWAY_URL}/api/hermes/whatsapp/message", json=payload)
    assert resp.status_code == 200, f"WhatsApp text message route failed: {resp.text}"
