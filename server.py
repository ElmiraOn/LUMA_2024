from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/process-links', methods=['POST'])
def process_links():
    """
    Endpoint to receive the links from the extension, simulate processing,
    and print the received links to the terminal (console).
    """
    # Get the links data from the request
    data = request.get_json()
    
    # Print the received links to the terminal
    print("Received links:", data['links'])
    
    # Example of processed data (just echoing back the links)
    processed_data = {
        'status': 'success',  # You can include a status or other info
        'processed_links': data['links']  # Echo the links back
    }
    
    # Return the processed data back to the extension
    return jsonify(processed_data)


if __name__ == '__main__':
    # Start the Flask server on localhost:5000
    app.run(host='localhost', port=5000)
