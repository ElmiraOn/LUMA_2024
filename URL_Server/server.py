# URL_Server/server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import threading
import sys
import os

# Add the speech_tasks directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from speech_tasks.speech import VistaCoreAssistant

app = Flask(__name__)
CORS(app)

# Global variable to store the VistaCoreAssistant instance
vista_assistant = None

def run_vista_assistant():
    """Function to run Vista Assistant in a separate thread"""
    global vista_assistant
    try:
        vista_assistant = VistaCoreAssistant()
        vista_assistant.handle_conversation()
    except Exception as e:
        print(f"Error in Vista Assistant thread: {str(e)}")

@app.route('/process-links', methods=['POST'])
def process_links():
    try:
        data = request.get_json()
        
        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Print received data in a structured way
        print("\n=== URL Extraction Results ===")
        print(f"Timestamp: {timestamp}")
        print(f"Current URL: {data['currentUrl']}")
        print(f"Found {len(data['allUrls'])} URLs:")
        for idx, url in enumerate(data['allUrls'], 1):
            print(f"{idx}. {url}")
        print("===========================\n")
        
        return jsonify({
            'status': 'success',
            'timestamp': timestamp,
            'message': f'Processed {len(data["allUrls"])} URLs'
        })
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
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
    print("Server starting on http://localhost:5000")
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