from flask import Flask, request, jsonify
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Try different import approaches to handle potential module issues
try:
    from app.pdf_processor import extract_text_from_pdf, parse_jadwal
    logging.info("Successfully imported pdf_processor from app package")
except ImportError:
    try:
        from pdf_processor import extract_text_from_pdf, parse_jadwal
        logging.info("Successfully imported pdf_processor directly")
    except ImportError:
        logging.error("Failed to import pdf_processor module")
        
# Initialize Flask app
app = Flask(__name__)

def handle_pdf_processing(file):
    """
    Helper function to process the PDF file and return parsed JSON data.
    """
    if not file or file.filename == '':
        return {"error": "No selected file"}, 400
    
    if not file.filename.endswith('.pdf'):
        return {"error": "Invalid file format. Only PDF files are allowed."}, 400

    try:
        # Ensure the uploads directory exists for temporary storage
        base_dir = os.path.dirname(os.path.abspath(__file__))
        upload_dir = os.path.join(base_dir, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # Save the file temporarily
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)

        # Extract text and parse it
        text = extract_text_from_pdf(file_path)
        json_output = parse_jadwal(text)

        # Clean up the uploaded file immediately
        os.remove(file_path)

        return json_output, 200

    except Exception as e:
        logging.error(f"Error during PDF processing: {str(e)}")
        return {"error": "Internal Server Error", "message": str(e)}, 500

@app.route('/')
def home():
    logging.info("Root endpoint accessed")
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload PDF</title>
    </head>
    <body>
        <h1>Upload PDF File (Web Testing)</h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="application/pdf" required>
            <button type="submit">Upload</button>
        </form>
        <p>Main API endpoint: POST <code>/usukaparse</code></p>
    </body>
    </html>
    '''

@app.route('/usukaparse', methods=['POST'])
def usuka_parse():
    """
    Primary route for processing PDF files and returning JSON output.
    Expects a 'file' field in the POST request.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    result, status_code = handle_pdf_processing(request.files['file'])
    return jsonify(result), status_code

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Secondary route for web-based testing. 
    Calls the same processing logic as /usukaparse.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    result, status_code = handle_pdf_processing(request.files['file'])
    return jsonify(result), status_code

@app.route('/ping')
def ping():
    return "pong", 200

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
