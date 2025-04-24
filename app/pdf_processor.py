from flask import Flask, request, jsonify
import os
from pdf_text import extract_text_from_pdf, parse_jadwal

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pdf'):
        # Save the uploaded PDF file temporarily
        temp_file_path = os.path.join('temp', file.filename)
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
        file.save(temp_file_path)
        
        # Extract text and parse it
        text = extract_text_from_pdf(temp_file_path)
        output_file = "jadwal_mahasiswa.json"
        parse_jadwal(text, output_file)
        
        # Read the JSON output
        with open(output_file, 'r', encoding='utf-8') as json_file:
            json_data = json_file.read()
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        return jsonify(json_data), 200
    
    return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)