from flask import Flask, request, jsonify
import os
from pdf_processor import extract_text_from_pdf, parse_jadwal

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pdf'):
        # Save the uploaded PDF file temporarily
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Extract text and parse it
        text = extract_text_from_pdf(file_path)
        json_output = parse_jadwal(text)

        # Clean up the uploaded file
        os.remove(file_path)

        return jsonify(json_output), 200
    
    return jsonify({"error": "Invalid file format. Only PDF files are allowed."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)