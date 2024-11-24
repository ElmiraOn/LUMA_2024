import os
import speech_recognition as sr
import time
from datetime import datetime
import sys
from gtts import gTTS
import pygame

class VistaCoreAssistant:
    def __init__(self):
        # Initialize recognition engine
        self.recognizer = sr.Recognizer()
        self.wake_words = ["hey vista", "hi vista", "hello vista"]
        self.exit_phrases = ["bye vista", "goodbye vista", "exit vista", "close vista"]
        
        # Configure speech recognition settings
        self.recognizer.energy_threshold = 800
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 1.2
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 1.0
        
        # Timing configurations
        self.SILENCE_AFTER_SPEECH_TIMEOUT = 2.5
        self.MAX_LISTEN_TIME = 30
        self.INITIAL_SILENCE_TIMEOUT = 10

        # Initialize audio playback
        pygame.mixer.init()

        # Use a fixed directory for temporary files
        self.temp_dir = "temp_files"
        os.makedirs(self.temp_dir, exist_ok=True)  # Ensure the directory exists
        
        print("VISTA Speech Recognition initialized")

    def text_to_speech(self, text, filename=None):
        """Convert text to speech and play it"""
        try:
            if filename is None:
                filename = os.path.join(self.temp_dir, 'response.mp3')
            
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filename)
            
            # Play the speech
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Clean up
            pygame.mixer.music.unload()
            os.remove(filename)
            
        except Exception as e:
            print(f"Error in text to speech: {str(e)}")

    def play_acknowledgment(self):
        """Play a Siri-like acknowledgment sound"""
        self.text_to_speech("mm hmm", os.path.join(self.temp_dir, 'ack.mp3'))

    def speech_to_text(self, timeout=None, phrase_time_limit=None):
        """Listen for speech and convert to text"""
        try:
            # with sr.Microphone() as source:
            mic_index = 3  # You can change this to the index of your microphone
            with sr.Microphone(device_index=mic_index) as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                try:
                    text = self.recognizer.recognize_google(audio, language="en-US").lower()
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

    def process_command(self, command):
        """Process the command and return a response"""
        return "I understood what you said. This is a static response for testing."

    def handle_conversation(self):
        """Handle the main conversation flow"""
        try:
            while True:
                print(f"Listening for wake words: {', '.join(self.wake_words)}")
                wake_word = self.speech_to_text(timeout=None, phrase_time_limit=2.0)
                
                if wake_word and self.is_wake_word(wake_word):
                    print("Wake word detected!")
                    self.play_acknowledgment()
                    print("Listening for command...")
                    command = self.speech_to_text(timeout=None, phrase_time_limit=10.0)
                    if command:
                        print(f"Command received: {command}")
                        response = self.process_command(command)
                        print(f"Responding: {response}")
                        self.text_to_speech(response)
                elif wake_word and self.is_exit_command(wake_word):
                    self.text_to_speech("Goodbye!")
                    self.handle_exit()
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.text_to_speech("Goodbye!")
            self.handle_exit("\nKeyboard interrupt detected")

    def is_wake_word(self, text):
        """Check if the spoken text contains any of the wake words"""
        return any(wake_word in text.lower() for wake_word in self.wake_words)

    def is_exit_command(self, text):
        """Check if the spoken text is an exit command"""
        return any(exit_phrase in text.lower() for exit_phrase in self.exit_phrases)

    def handle_exit(self, message="Exiting VISTA..."):
        """Handle clean exit of the program"""
        print(message)
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                try:
                    os.remove(os.path.join(self.temp_dir, file))
                except:
                    pass
        sys.exit(0)

# Uncomment to run the assistant
# if __name__ == "__main__":
#     assistant = VistaCoreAssistant()
#     assistant.handle_conversation()
