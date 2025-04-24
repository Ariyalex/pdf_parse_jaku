from flask import Flask, request, jsonify
import os
import fitz  # PyMuPDF
import json
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def extract_text_from_pdf(input_pdf):
    doc = fitz.open(input_pdf)
    text = ""
    for page in doc:
        text += page.get_text("text")  # Extract text from each page
    return text

def save_raw_text(text, output_file="raw_pdf_text.txt"):
    """
    Save the raw extracted text from PDF to a text file without parsing
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[INFO] Raw PDF text saved to {output_file}")

def parse_jadwal(pdf_text, output_file="jadwal_mahasiswa.json"):
    lines = pdf_text.splitlines()

    info = {
        "nama": "",
        "nim": "",
        "semester": "",
        "tahun_akademik": "",
        "program_studi": "",
        "jadwal": []
    }

    # Extract student information handling line breaks between key and value
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for NIM with value on next line
        if line == "NIM" and i+1 < len(lines) and ":" in lines[i+1]:
            info["nim"] = lines[i+1].split(":")[-1].strip()
        # Check for Tahun Akademik on same line
        elif "Tahun Akademik" in line:
            info["tahun_akademik"] = line.split(":")[-1].strip()
        # Check for Nama Mahasiswa with value on next line
        elif line == "Nama Mahasiswa" and i+1 < len(lines) and ":" in lines[i+1]:
            info["nama"] = lines[i+1].split(":")[-1].strip()
        # Check for Semester with value on next line
        elif line == "Semester" and i+1 < len(lines) and ":" in lines[i+1]:
            info["semester"] = lines[i+1].split(":")[-1].strip()
        # Check for Program Studi with value on next line
        elif line == "Program Studi" and i+1 < len(lines) and ":" in lines[i+1]:
            info["program_studi"] = lines[i+1].split(":")[-1].strip()
        
        i += 1

    # Reset i for course parsing
    i = 0
    current = {}
    while i < len(lines):
        line = lines[i].strip()
        
        # Detect course number (1, 2, 3, ...)
        if re.match(r"^\d+\s*$", line):
            if current:
                info["jadwal"].append(current)
            current = {
                "no": int(line),
                "mata_kuliah": "",
                "sks": 0,
                "jadwal_kuliah": [],
                "dosen": []
            }
            i += 1
            
            # Fix bug #4: Handle multi-line course names
            current["mata_kuliah"] = lines[i].strip()  # Course name
            i += 1
            
            # Check if the next lines are continuation of the course name (not SKS and not a number)
            while i < len(lines) and not re.match(r"^\d+$", lines[i].strip()) and not re.match(r"^\d+\s*$", lines[i].strip()):
                current["mata_kuliah"] += " " + lines[i].strip()  # Add to course name
                i += 1

            # Get SKS (ensure the line containing the number is SKS)
            if i < len(lines) and re.match(r"^\d+$", lines[i].strip()):
                current["sks"] = int(lines[i].strip())
                i += 1
            else:
                current["sks"] = 0  # Default if no SKS found

            # Get class schedule and lecturers
            while i < len(lines):
                jadwal_line = lines[i].strip()
                
                # If the line contains a schedule, we can add it to "jadwal_kuliah"
                if re.search(r"R:\s*FST", jadwal_line):
                    # Fix bug #2 and #3: Separate schedule from lecturer if they're on the same line
                    parts = jadwal_line.strip().split("R: FST-")
                    if len(parts) >= 2:
                        day_time = parts[0].strip()
                        # Extract only the room number part (e.g., "305" from "R: FST-305")
                        room_number = parts[1].strip().split(" ", 1)[0]
                        
                        # Extract schedule components
                        day_match = re.match(r"([^,]+),", day_time)
                        time_match = re.search(r"(\d+:\d+-\d+:\d+)", day_time)
                        
                        if day_match and time_match:
                            day = day_match.group(1).strip()
                            time = time_match.group(1).strip()
                            # Use "FST-{room_number}" format without the "R: " prefix
                            room = f"FST-{room_number}"
                            
                            # Add structured schedule
                            current["jadwal_kuliah"].append({
                                "hari": day,
                                "waktu": time,
                                "ruangan": room
                            })
                        
                        # Check if there's a lecturer name on the same line
                        if len(parts[1].split(" ", 1)) > 1:
                            dosen_part = parts[1].split(" ", 1)[1].strip()
                            # Remove ID if present
                            dosen_name = re.sub(r"\(\d{8} \d{6} \d \d{3}\)", "", dosen_part).strip()
                            if dosen_name and len(dosen_name) >= 6:  # Changed from 5 to 6
                                current["dosen"].append({
                                    "nama": dosen_name
                                })
                    i += 1
                # Check if this is a lecturer line (not starting with a day)
                elif not re.search(r"^(Senin|Selasa|Rabu|Kamis|Jum'at|Sabtu|Minggu),", jadwal_line) and jadwal_line and not re.match(r"^\d+\s*$", jadwal_line):
                    # This is likely a lecturer name
                    dosen_name = re.sub(r"\(\d{8} \d{6} \d \d{3}\)", "", jadwal_line).strip()
                    
                    # Only add lecturer if not empty and has at least 6 characters (changed from 5)
                    if dosen_name and len(dosen_name) >= 6:
                        current["dosen"].append({
                            "nama": dosen_name
                        })
                    
                    i += 1
                else:
                    break
        else:
            i += 1

    if current:
        info["jadwal"].append(current)

    # Remove duplicate lecturers
    for course in info["jadwal"]:
        unique_dosens = []
        seen_names = set()
        for dosen in course["dosen"]:
            # Add length check here as well for any existing entries
            if dosen["nama"] not in seen_names and dosen["nama"] and len(dosen["nama"]) >= 6:
                seen_names.add(dosen["nama"])
                unique_dosens.append(dosen)
        course["dosen"] = unique_dosens

    # Save to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Data berhasil disimpan di {output_file}")
    
    # Return the parsed data as a dictionary
    return info

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Railway Backend! Use the /upload endpoint to upload PDFs."}), 200

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            logging.error("No file part in the request")
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        if file.filename == '':
            logging.error("No selected file")
            return jsonify({"error": "No selected file"}), 400

        if file and file.filename.endswith('.pdf'):
            # Save the uploaded PDF file temporarily
            temp_file_path = os.path.join('temp', file.filename)
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            file.save(temp_file_path)

            # Extract text and parse it
            text = extract_text_from_pdf(temp_file_path)
            save_raw_text(text, "raw_pdf_text.txt")  # Save raw text
            output_file = "jadwal_mahasiswa.json"
            parsed_data = parse_jadwal(text, output_file)  # Parse and save JSON

            # Clean up the temporary file
            os.remove(temp_file_path)

            return jsonify(parsed_data), 200

        logging.error("Invalid file format")
        return jsonify({"error": "Invalid file format"}), 400

    except Exception as e:
        logging.exception("An error occurred during file upload")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)