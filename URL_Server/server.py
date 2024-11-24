# URL_Server/server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import threading
import sys
import os
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from speech_tasks.speech import VistaCoreAssistant

app = Flask(__name__)
CORS(app)

# Global variables
vista_assistant = None
current_command = None
browser_data = {
    'current_url': 'https://www.yorku.ca/about/contact/',
    'urls': [],
    'token': '0'
}

def run_vista_assistant():
    """Function to run Vista Assistant in a separate thread"""
    global vista_assistant
    try:
        vista_assistant = VistaCoreAssistant()
        vista_assistant.set_command_callback(handle_command)
        vista_assistant.handle_conversation()
    except Exception as e:
        print(f"Error in Vista Assistant thread: {str(e)}")

def send_command_to_backend(command):
    """Send command to backend and wait for response"""
    try:
        payload = {
            'token': browser_data['token'],
            'command': command,
            'urls': browser_data['urls']
        }
        
        print("\n=== Sending Command to Backend ===")
        print(f"Command: {command}")
        print(f"Token: '{browser_data['token']}'")
        print(f"Current URL: {browser_data['current_url']}")
        print("================================\n")
        
        # Send request and wait for backend response
        response = requests.post(
            'http://195.242.13.18:50001/generate',
            json=payload
        )
        
        if response.ok:
            response_data = response.json()
            return response_data.get('response', 'Response not received')
        return "Response not received"
            
    except Exception as e:
        print(f"Error sending command to backend: {str(e)}")
        return "Response not received"

def handle_command(command):
    """Handle command after wake word"""
    global current_command, vista_assistant
    
    try:
        current_command = command
        print("\n=== Command Received ===")
        print(f"Command: {command}")
        print("========================\n")
        
        if command and browser_data['urls']:
            # Send command to backend and wait for response
            backend_response = send_command_to_backend(command)
            # Relay actual backend response through voice assistant
            if vista_assistant:
                vista_assistant.text_to_speech(backend_response)
        elif command:
            if vista_assistant:
                vista_assistant.text_to_speech("No page data available. Please wait for a page to load.")
            
    except Exception as e:
        print(f"Error handling command: {str(e)}")
        if vista_assistant:
            vista_assistant.text_to_speech("Error processing command")

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
        
        # Just acknowledge receipt of data
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"\nError storing browser data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop-vista', methods=['POST'])
def stop_vista():
    """Endpoint to safely stop the Vista Assistant"""
    global vista_assistant
    try:
        if vista_assistant:
            vista_assistant.handle_exit("Stopping Vista Assistant via web request")
            return jsonify({'status': 'success', 'message': 'Vista Assistant stopped'})
        return jsonify({'status': 'warning', 'message': 'Vista Assistant was not running'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def start_server():
    """Function to start the Flask server"""
    print("\n" + "="*50)
    print("Server starting on http://localhost:5000")
    print("="*50 + "\n")
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    try:
        # Start Vista Assistant in a separate thread
        vista_thread = threading.Thread(target=run_vista_assistant, daemon=True)
        vista_thread.start()
        
        # Start the Flask server
        start_server()
        
    except KeyboardInterrupt:
        print("\nShutting down server and Vista Assistant...")
        if vista_assistant:
            vista_assistant.handle_exit()
    except Exception as e:
        print(f"Error starting server: {str(e)}")