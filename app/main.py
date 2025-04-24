from flask import Flask, request, jsonify, render_template, send_file
import os
from pdf_processor import extract_text_from_pdf, parse_jadwal
import json

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload PDF</title>
    </head>
    <body>
        <h1>Upload PDF File</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="application/pdf" required>
            <button type="submit">Upload</button>
        </form>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and file.filename.endswith('.pdf'):
            # Ensure the uploads directory exists with an absolute path
            base_dir = os.path.dirname(os.path.abspath(__file__))
            upload_dir = os.path.join(base_dir, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            # Save the file to the uploads directory
            file_path = os.path.join(upload_dir, file.filename)
            file.save(file_path)

            # Extract text and parse it
            text = extract_text_from_pdf(file_path)
            json_output = parse_jadwal(text)

            # Save the JSON output to a file
            json_file_path = os.path.join(upload_dir, 'jadwal_mahasiswa.json')
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_output, json_file, ensure_ascii=False, indent=4)

            # Clean up the uploaded file
            os.remove(file_path)

            # Return a link to download the JSON file
            return f'''
            <!doctype html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Upload Successful</title>
            </head>
            <body>
                <h1>Upload Successful</h1>
                <p>Download the JSON file: <a href="/download">Download JSON</a></p>
            </body>
            </html>
            '''

        return jsonify({"error": "Invalid file format. Only PDF files are allowed."}), 400

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route('/download')
def download_file():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(base_dir, 'uploads', 'jadwal_mahasiswa.json')
    if os.path.exists(json_file_path):
        return send_file(json_file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    if not os.environ.get('PORT'):
        print("[WARNING] Environment variable 'PORT' is not set. Using default port 5000.")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)