# server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    print("Server starting on http://localhost:5000")
    app.run(host='localhost', port=5000, debug=True)