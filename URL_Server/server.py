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
import logging



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('url_tracker.log')
    ]
)

app = Flask(__name__)
# CORS(app)


CORS(app, resources={
    r"/*": {
        "origins": ["chrome-extension://*", "http://localhost:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Global variables for storing browser data
browser_data = {
    'current_url': '',
    'urls': [],
    'token': '0'
}

class VoiceAssistant:
    def __init__(self):
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
        logging.info("Voice Assistant initialized")

    def text_to_speech(self, text, filename=None):
        """Convert text to speech and play it"""
        try:
            if filename is None:
                filename = os.path.join(self.temp_dir, 'response.mp3')
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filename)
            
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            clock = pygame.time.Clock()
            while pygame.mixer.music.get_busy():
                clock.tick(10)
            
            pygame.mixer.music.unload()
            os.remove(filename)
            
        except Exception as e:
            logging.error(f"Error in text to speech: {str(e)}")

    def play_acknowledgment(self):
        """Play a short acknowledgment sound"""
        self.text_to_speech("Hi! How can I help you today?", os.path.join(self.temp_dir, 'ack.mp3'))

    def speech_to_text(self, timeout=None, phrase_time_limit=None):
        """Listen for speech and convert to text"""
        try:
            with sr.Microphone() as source:
                logging.info("Listening...")
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
                    logging.info(f"Recognized: {text}")
                    return text
                except sr.UnknownValueError:
                    logging.info("Could not understand audio")
                except sr.RequestError:
                    logging.error("Could not request results from speech recognition service")
        except sr.WaitTimeoutError:
            logging.info("No speech detected within timeout period")
        except Exception as e:
            logging.error(f"Error in speech recognition: {str(e)}")
        
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
        
        logging.info("\n" + "="*50)
        logging.info("DATA SENT TO BACKEND:")
        logging.info("="*50)
        logging.info(f"COMMAND: {command}")
        logging.info(f"TOKEN: '{browser_data['token']}'")
        logging.info(f"CURRENT URL: {browser_data['current_url']}")
        logging.info("\nALL URLS:")
        for idx, url in enumerate(browser_data['urls'], 1):
            logging.info(f"{idx}. {url}")
        logging.info("="*50)
        
        response = requests.post(
            'http://195.242.13.147:50001/generate',
            json=payload
        )
        
        if response.ok:
            response_data = response.json()
            logging.info("\n" + "="*50)
            logging.info("BACKEND RESPONSE:")
            logging.info("="*50)
            logging.info(response_data.get('response', 'Response not received'))
            logging.info("="*50 + "\n")
            print(response_data)
            
            # Set token to '1' after successful request
            browser_data['token'] = '1'
            
            return response_data.get('response', 'Response not received')
        return "Response not received"
            
    except Exception as e:
        logging.error(f"Error sending command to backend: {str(e)}")
        return "Response not received"

def run_voice_assistant():
    """Main function to run the voice assistant"""
    assistant = VoiceAssistant()
    
    while True:
        try:
            logging.info(f"Listening for wake words: {', '.join(assistant.wake_words)}")
            wake_word = assistant.speech_to_text(timeout=None, phrase_time_limit=2.0)
            
            if wake_word and assistant.is_wake_word(wake_word):
                logging.info("Wake word detected!")
                assistant.play_acknowledgment()
                
                logging.info("Listening for command...")
                command = assistant.speech_to_text(timeout=None, phrase_time_limit=10.0)
                
                if command:
                    logging.info(f"Command received: {command}")
                    
                    if browser_data['urls']:
                        backend_response = send_command_to_backend(command)
                        assistant.text_to_speech(backend_response)
                    else:
                        assistant.text_to_speech("No page data available. Please wait for a page to load.")
            
            time.sleep(0.1)
                
        except Exception as e:
            logging.error(f"Error in voice assistant loop: {str(e)}")
            continue

@app.route('/process-links', methods=['POST'])
def process_links():
    """Handle incoming links from the Chrome extension"""
    logging.info("Received request to process links")
    try:
        global browser_data
        
        browser_update = request.get_json()
        # print(browser_data)
        
        if not browser_update:
            raise ValueError("No JSON data received")
        
        buffer = browser_update.get('token', '0')
        browser_data = {
            'current_url': browser_update.get('currentUrl', ''),
            'urls': browser_update.get('allUrls',  []),
            'token': str(buffer)
        }
        
        logging.info("\n" + "="*50)
        logging.info("Updated Browser Data:")
        logging.info("="*50)
        logging.info(f"Current URL: {browser_data['current_url']}")
        logging.info(f"Token: '{browser_data['token']}'")
        logging.info(f"URLs found: {len(browser_data['urls'])}")
        logging.info("="*50 + "\n")
        
        return jsonify({'status': 'success', 'message': 'Links processed successfully'})
        
    except Exception as e:
        error_msg = f"Error processing links: {str(e)}"
        logging.error(error_msg)
        return jsonify({'status': 'error', 'message': error_msg}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'current_page': browser_data['current_url'],
        'urls_collected': len(browser_data['urls'])
    })

def start_server():
    """Function to start the Flask server"""
    logging.info("\n" + "="*50)
    logging.info("Server starting on http://localhost:50001")
    logging.info("="*50 + "\n")
    app.run(host='0.0.0.0', port=50001, debug=False)

if __name__ == '__main__':
    try:
        # Start voice assistant in a separate thread
        voice_thread = threading.Thread(target=run_voice_assistant, daemon=True)
        voice_thread.start()
        logging.info("Voice assistant thread started")
        
        # Start the Flask server
        start_server()
        
    except KeyboardInterrupt:
        logging.info("\nShutting down server...")
    except Exception as e:
        logging.error(f"Error starting server: {str(e)}")