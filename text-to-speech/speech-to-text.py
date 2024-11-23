import speech_recognition as sr
import time
from datetime import datetime
import sys
from gtts import gTTS
import os
import pygame
import tempfile

class VistaCoreAssistant:
    def __init__(self):
        # Initialize recognition engine
        self.recognizer = sr.Recognizer()
        self.wake_words = ["hey vista", "hi vista", "hello vista"]
        self.exit_phrases = ["bye vista", "goodbye vista", "exit vista", "close vista"]
        
        # Configure speech recognition settings for better sentence completion
        self.recognizer.energy_threshold = 800
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15  # More stable energy adjustment
        self.recognizer.dynamic_energy_ratio = 1.5  # More sensitive to speech
        self.recognizer.pause_threshold = 1.2  # Longer pause allowed within phrases
        self.recognizer.phrase_threshold = 0.3  # More sensitive to phrase starts
        self.recognizer.non_speaking_duration = 1.0  # Wait longer for sentence completion
        
        # Timing configurations
        self.SILENCE_AFTER_SPEECH_TIMEOUT = 2.5  # Longer silence needed to end listening
        self.MAX_LISTEN_TIME = 30  # Longer maximum listening time
        self.INITIAL_SILENCE_TIMEOUT = 10
        
        # Initialize audio playback
        pygame.mixer.init()
        self.temp_dir = tempfile.mkdtemp()
        
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
        """Listen for speech and convert to text with improved sentence detection"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                # Shorter ambient noise adjustment to be more responsive
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                # Listen with increased phrase_time_limit for longer sentences
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit,
                    snowboy_configuration=None
                )
                
                try:
                    # Using a more permissive recognition setting
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

    def process_command(self, command):
        """Process the command and return a response"""
        return "I understood what you said. This is a static response for testing."

    def handle_conversation(self):
        """Handle the main conversation flow with improved command listening"""
        try:
            while True:
                # Listen for wake word with shorter phrase time limit
                print(f"Listening for wake words: {', '.join(self.wake_words)}")
                wake_word = self.speech_to_text(timeout=None, phrase_time_limit=2.0)
                
                if wake_word and self.is_wake_word(wake_word):
                    # Play acknowledgment
                    print("Wake word detected!")
                    self.play_acknowledgment()
                    
                    # Listen for command with longer phrase time limit
                    print("Listening for command...")
                    # Allow up to 10 seconds for a single command phrase
                    command = self.speech_to_text(timeout=None, phrase_time_limit=10.0)
                    
                    if command:
                        print(f"Command received: {command}")
                        
                        # Process command and get response
                        response = self.process_command(command)
                        
                        # Speak the response
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
        if text:
            return any(wake_word in text.lower() for wake_word in self.wake_words)
        return False

    def is_exit_command(self, text):
        """Check if the spoken text is an exit command"""
        if text:
            return any(exit_phrase in text.lower() for exit_phrase in self.exit_phrases)
        return False

    def handle_exit(self, message="Exiting VISTA..."):
        """Handle clean exit of the program"""
        print(message)
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                try:
                    os.remove(os.path.join(self.temp_dir, file))
                except:
                    pass
            os.rmdir(self.temp_dir)
        sys.exit(0)

# def main():
#     assistant = VistaCoreAssistant()
#     try:
#         assistant.handle_conversation()
#     except Exception as e:
#         print(f"Error in main: {str(e)}")
#         assistant.handle_exit()

# if __name__ == "__main__":
#     main()