from flask import Flask, request, jsonify, render_template, send_file
import os
import sys
import logging
from app.pdf_processor import extract_text_from_pdf, parse_jadwal
import json
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    logger.info("Root endpoint accessed")
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
            logger.error("No file part in the request")
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        if file.filename == '':
            logger.error("No selected file")
            return jsonify({"error": "No selected file"}), 400

        if file and file.filename.endswith('.pdf'):
            # Ensure the uploads directory exists with an absolute path
            base_dir = os.path.dirname(os.path.abspath(__file__))
            upload_dir = os.path.join(base_dir, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            # Save the file to the uploads directory
            file_path = os.path.join(upload_dir, file.filename)
            file.save(file_path)
            logger.info(f"File saved to {file_path}")

            # Extract text and parse it
            text = extract_text_from_pdf(file_path)
            json_output = parse_jadwal(text)

            # Save the JSON output to a file
            json_file_path = os.path.join(upload_dir, 'jadwal_mahasiswa.json')
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_output, json_file, ensure_ascii=False, indent=4)
            logger.info(f"JSON output saved to {json_file_path}")

            # Clean up the uploaded file
            os.remove(file_path)
            logger.info(f"Uploaded file {file_path} removed after processing")

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

        logger.error("Invalid file format. Only PDF files are allowed.")
        return jsonify({"error": "Invalid file format. Only PDF files are allowed."}), 400

    except Exception as e:
        logger.error(f"Error during file upload: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route('/download')
def download_file():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(base_dir, 'uploads', 'jadwal_mahasiswa.json')
        if os.path.exists(json_file_path):
            logger.info(f"JSON file {json_file_path} found and ready for download")
            return send_file(json_file_path, as_attachment=True)
        logger.error("JSON file not found")
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        logger.error(f"Error during file download: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route('/health')
def health_check():
    logger.info("Health check endpoint accessed")
    return jsonify({"status": "healthy", "message": "Application is running correctly"}), 200

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Starting application on port {port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)