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

def run_vista_assistant():
    """Function to run Vista Assistant in a separate thread"""
    global vista_assistant
    try:
        vista_assistant = VistaCoreAssistant()
        vista_assistant.set_command_callback(update_current_command)
        vista_assistant.handle_conversation()
    except Exception as e:
        print(f"Error in Vista Assistant thread: {str(e)}")

def update_current_command(command):
    """Callback function to update the current command"""
    global current_command
    current_command = command
    print("\n=== Command Updated ===")
    print(f"New Command: {command}")
    print("=====================\n")

@app.route('/process-links', methods=['POST'])
def process_links():
    try:
        data = request.get_json()
        token = data.get('token', 0)
        current_url = data.get('currentUrl', '')
        
        # Print detailed information about the request
        print("\n" + "="*50)
        print("URL Processing Details:")
        print("="*50)
        print(f"Token: {token}")
        print(f"Current URL: {current_url}")
        print(f"Current Command: {current_command if current_command else 'No command'}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*50)
        print(f"Found URLs: {len(data['allUrls'])}")
        print("="*50 + "\n")
        
        # Prepare data for the SSH endpoint
        payload = {
            'token': token,
            'command': current_command if current_command else "",
            'urls': data['allUrls']
        }
        
        # Send request to SSH endpoint
        ssh_response = requests.post(
            'ssh:195.242.13.18/api/generate/',
            json=payload
        )
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'ssh_response': ssh_response.json() if ssh_response.ok else None
        })
        
    except Exception as e:
        print(f"\nError processing request: {str(e)}")
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