from flask import Flask, jsonify, request
from flask_cors import CORS
import speech_recognition as sr
import threading
import pygame
import tempfile
from gtts import gTTS
import os
import requests
import time

app = Flask(__name__)
CORS(app)

# Global variables
browser_data = {
    'current_url': '',
    'urls': [],
    'token': '0'
}

class VoiceAssistant:
    def __init__(self):
        # Initialize recognition engine
        self.recognizer = sr.Recognizer()
        self.wake_words = ["hey vista", "hi vista", "hello vista"]
        
        # Configure speech recognition settings
        self.recognizer.energy_threshold = 800
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 1.2
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 1.0
        
        # Initialize audio playback
        pygame.mixer.init()
        self.temp_dir = tempfile.mkdtemp()
        print("Voice Assistant initialized")

    def text_to_speech(self, text, filename=None):
        """Convert text to speech and play it"""
        try:
            if filename is None:
                filename = os.path.join(self.temp_dir, 'response.mp3')
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filename)
            
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.music.unload()
            os.remove(filename)
            
        except Exception as e:
            print(f"Error in text to speech: {str(e)}")

    def play_acknowledgment(self):
        """Play a short acknowledgment sound"""
        self.text_to_speech("mm hmm", os.path.join(self.temp_dir, 'ack.mp3'))

    def speech_to_text(self, timeout=None, phrase_time_limit=None):
        """Listen for speech and convert to text"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                try:
                    text = self.recognizer.recognize_google(
                        audio,
                        language="en-US",
                        show_all=False
                    ).lower()
                    print(f"Recognized: {text}")
                    return text
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError:
                    print("Could not request results from speech recognition service")
        except sr.WaitTimeoutError:
            print("No speech detected within timeout period")
        except Exception as e:
            print(f"Error in speech recognition: {str(e)}")
        
        return None

    def is_wake_word(self, text):
        """Check if the spoken text contains any wake words"""
        if text:
            return any(wake_word in text.lower() for wake_word in self.wake_words)
        return False

def send_command_to_backend(command):
    """Send command to backend and wait for response"""
    try:
        payload = {
            'token': browser_data['token'],
            'command': command,
            'urls': browser_data['urls']
        }
        
        print("\n" + "="*50)
        print("DATA SENT TO BACKEND:")
        print("="*50)
        print(f"COMMAND: {command}")
        print(f"TOKEN: '{browser_data['token']}'")
        print(f"CURRENT URL: {browser_data['current_url']}")
        print("\nALL URLS:")
        for idx, url in enumerate(browser_data['urls'], 1):
            print(f"{idx}. {url}")
        print("="*50)
        
        response = requests.post(
            'http://195.242.13.18:50001/generate',
            json=payload
        )
        
        if response.ok:
            response_data = response.json()
            print("\n" + "="*50)
            print("BACKEND RESPONSE:")
            print("="*50)
            print(response_data.get('response', 'Response not received'))
            print("="*50 + "\n")
            
            return response_data.get('response', 'Response not received')
        return "Response not received"
            
    except Exception as e:
        print(f"Error sending command to backend: {str(e)}")
        return "Response not received"

def run_voice_assistant():
    """Main function to run the voice assistant"""
    assistant = VoiceAssistant()
    
    while True:
        try:
            # Listen for wake word
            print(f"Listening for wake words: {', '.join(assistant.wake_words)}")
            wake_word = assistant.speech_to_text(timeout=None, phrase_time_limit=2.0)
            
            if wake_word and assistant.is_wake_word(wake_word):
                print("Wake word detected!")
                assistant.play_acknowledgment()
                
                # Listen for command
                print("Listening for command...")
                command = assistant.speech_to_text(timeout=None, phrase_time_limit=10.0)
                
                if command:
                    print(f"Command received: {command}")
                    
                    # Only process command if we have URLs
                    if browser_data['urls']:
                        # Send command to backend and wait for response
                        backend_response = send_command_to_backend(command)
                        # Relay the response through voice
                        assistant.text_to_speech(backend_response)
                    else:
                        assistant.text_to_speech("No page data available. Please wait for a page to load.")
            
            time.sleep(0.1)
                
        except Exception as e:
            print(f"Error in voice assistant loop: {str(e)}")
            continue

@app.route('/process-links', methods=['POST'])
def process_links():
    """Store browser data (currentUrl and URLs) sent from background.js"""
    try:
        global browser_data
        
        # Get data sent from browser's background.js
        browser_update = request.get_json()
        
        # Store the browser data
        browser_data = {
            'current_url': browser_update.get('currentUrl', ''),
            'urls': browser_update.get('allUrls', []),
            'token': str(browser_update.get('token', '0'))
        }
        
        print("\n" + "="*50)
        print("Updated Browser Data:")
        print("="*50)
        print(f"Current URL: {browser_data['current_url']}")
        print(f"Token: '{browser_data['token']}'")
        print(f"URLs found: {len(browser_data['urls'])}")
        print("="*50 + "\n")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"\nError storing browser data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def start_server():
    """Function to start the Flask server"""
    print("\n" + "="*50)
    print("Server starting on http://localhost:5000")
    print("="*50 + "\n")
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    try:
        # Start voice assistant in a separate thread
        voice_thread = threading.Thread(target=run_voice_assistant, daemon=True)
        voice_thread.start()
        
        # Start the Flask server
        start_server()
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {str(e)}")