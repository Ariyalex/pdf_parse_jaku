from flask import Flask, request, jsonify
import os
from pdf_processor import extract_text_from_pdf, parse_jadwal

app = Flask(__name__)

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
            try:
                os.makedirs(upload_dir, exist_ok=True)
                print(f"[DEBUG] Upload directory created or already exists: {upload_dir}")
            except Exception as e:
                print(f"[ERROR] Failed to create upload directory: {e}")
                raise

            # Save the file to the uploads directory
            file_path = os.path.join(upload_dir, file.filename)
            print(f"[DEBUG] Saving file to: {file_path}")
            file.save(file_path)

            # Extract text and parse it
            text = extract_text_from_pdf(file_path)
            json_output = parse_jadwal(text)

            # Clean up the uploaded file
            os.remove(file_path)

            return jsonify(json_output), 200

        return jsonify({"error": "Invalid file format. Only PDF files are allowed."}), 400

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)