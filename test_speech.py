# import speech_recognition as sr
# from gtts import gTTS
# import os
# import pygame
# import tempfile
# import time
# from datetime import datetime

# def text_to_speech(text):
#     """
#     Converts text to speech and plays the audio using pygame.
#     """
#     try:
#         # Generate speech audio using gTTS
#         tts = gTTS(text=text, lang='en')

#         # Specify a custom writable directory
#         custom_temp_dir = os.path.expanduser("~/custom_temp")
#         os.makedirs(custom_temp_dir, exist_ok=True)  # Create directory if it doesn't exist
#         temp_audio_path = os.path.join(custom_temp_dir, "temp_audio.mp3")
        
#         # Save the audio file
#         tts.save(temp_audio_path)
        
#         # Initialize pygame mixer to play audio
#         pygame.mixer.init()
#         pygame.mixer.music.load(temp_audio_path)
#         pygame.mixer.music.play()
        
#         # Wait for the audio to finish playing
#         while pygame.mixer.music.get_busy():
#             time.sleep(0.1)
        
#         # Cleanup: Remove the temporary file
#         os.remove(temp_audio_path)
#     except Exception as e:
#         print(f"Error in text-to-speech: {e}")


# def speech_to_text():
#     """
#     Captures audio input from the microphone and converts it to text using speech recognition.
#     """
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Please speak into the microphone...")
#         try:
#             # Adjust the recognizer sensitivity to ambient noise and record audio
#             recognizer.adjust_for_ambient_noise(source)
#             audio = recognizer.listen(source)
            
#             # Recognize speech using Google Web Speech API
#             recognized_text = recognizer.recognize_google(audio)
#             print(f"You said: {recognized_text}")
#             return recognized_text
#         except sr.UnknownValueError:
#             print("Sorry, I could not understand the audio.")
#         except sr.RequestError as e:
#             print(f"Could not request results; {e}")
#     return None

# def main():
#     """
#     Main function to demonstrate speech-to-text and text-to-speech.
#     """
#     print("Starting Speech-to-Text and Text-to-Speech Program...")
#     while True:
#         print("\nOptions:")
#         print("1. Speak and Convert to Text")
#         print("2. Enter Text to Convert to Speech")
#         print("3. Exit")
        
#         choice = input("Enter your choice: ")
        
#         if choice == "1":
#             # Speech-to-Text
#             text = speech_to_text()
#             if text:
#                 print(f"Recognized Text: {text}")
#         elif choice == "2":
#             # Text-to-Speech
#             text = input("Enter text to convert to speech: ")
#             text_to_speech(text)
#         elif choice == "3":
#             print("Exiting program...")
#             break
#         else:
#             print("Invalid choice. Please try again.")

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print("\nProgram terminated.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
###############################
# import speech_recognition as sr

# recognizer = sr.Recognizer()

# # Check for microphone access
# try:
#     with sr.Microphone() as source:
#         print("Microphone is accessible. Please speak...")
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)
#         print("ok")
#         # print("Speech recorded successfully!")
# except Exception as e:
#     print(f"Error accessing the microphone: {e}")

###################
import speech_recognition as sr

recognizer = sr.Recognizer()

# Check available microphones
mic_list = sr.Microphone.list_microphone_names()
print("Available microphones:")
for i, mic in enumerate(mic_list):
    print(f"{i}: {mic}")

# Use a specific microphone (if needed)
mic_index = 3  # You can change this to the index of your microphone
with sr.Microphone(device_index=mic_index) as source:
    print("Microphone initialized successfully. Please speak...")
    recognizer.adjust_for_ambient_noise(source)
    audio = recognizer.listen(source)
    print("Speech recorded successfully!")
