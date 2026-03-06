import os
import fitz  # PyMuPDF
import json
import re
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_text_from_pdf(input_pdf):
    """
    Extracts text from a PDF file.
    """
    try:
        doc = fitz.open(input_pdf)
        text = ""
        for page in doc:
            text += page.get_text("text")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return ""

def parse_jadwal(pdf_text):
    """
    Parses the extracted text into a structured dictionary.
    """
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
        
        if line == "NIM" and i+1 < len(lines) and ":" in lines[i+1]:
            info["nim"] = lines[i+1].split(":")[-1].strip()
        elif "Tahun Akademik" in line:
            info["tahun_akademik"] = line.split(":")[-1].strip()
        elif line == "Nama Mahasiswa" and i+1 < len(lines) and ":" in lines[i+1]:
            info["nama"] = lines[i+1].split(":")[-1].strip()
        elif line == "Semester" and i+1 < len(lines) and ":" in lines[i+1]:
            info["semester"] = lines[i+1].split(":")[-1].strip()
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
                "id": str(uuid.uuid4()),
                "mata_kuliah": "",
                "sks": 0,
                "jadwal_kuliah": [],
                "dosen": []
            }
            i += 1
            
            # Handle multi-line course names
            if i < len(lines):
                current["mata_kuliah"] = lines[i].strip()
                i += 1
            
            while i < len(lines) and not re.match(r"^\d+$", lines[i].strip()) and not re.match(r"^\d+\s*$", lines[i].strip()):
                current["mata_kuliah"] += " " + lines[i].strip()
                i += 1

            # Get SKS
            if i < len(lines) and re.match(r"^\d+$", lines[i].strip()):
                current["sks"] = int(lines[i].strip())
                i += 1

            # Get class schedule and lecturers
            while i < len(lines):
                jadwal_line = lines[i].strip()
                
                if re.search(r"R:", jadwal_line):
                    parts = jadwal_line.strip().split("R: ")
                    if len(parts) >= 2:
                        day_time = parts[0].strip()
                        room_info = parts[1].strip().split(" ", 1)[0]
                        
                        day_match = re.match(r"([^,]+),", day_time)
                        time_match = re.search(r"(\d+:\d+-\d+:\d+)", day_time)
                        
                        if day_match and time_match:
                            current["jadwal_kuliah"].append({
                                "id": str(uuid.uuid4()),
                                "hari": day_match.group(1).strip(),
                                "waktu": time_match.group(1).strip(),
                                "ruangan": room_info
                            })
                        
                        if len(parts[1].split(" ", 1)) > 1:
                            dosen_name = re.sub(r"\(\d{8} \d{6} \d \d{3}\)", "", parts[1].split(" ", 1)[1]).strip()
                            if dosen_name and len(dosen_name) >= 6:
                                current["dosen"].append({"nama": dosen_name})
                    i += 1
                elif not re.search(r"^(Senin|Selasa|Rabu|Kamis|Jum'at|Sabtu|Minggu),", jadwal_line) and jadwal_line and not re.match(r"^\d+\s*$", jadwal_line):
                    dosen_name = re.sub(r"\(\d{8} \d{6} \d \d{3}\)", "", jadwal_line).strip()
                    if dosen_name and len(dosen_name) >= 6:
                        current["dosen"].append({"nama": dosen_name})
                    i += 1
                else:
                    break
        else:
            i += 1

    if current:
        info["jadwal"].append(current)

    # Clean up duplicate lecturers
    for course in info["jadwal"]:
        unique_dosens = []
        seen_names = set()
        for dosen in course["dosen"]:
            if dosen["nama"] not in seen_names:
                seen_names.add(dosen["nama"])
                unique_dosens.append(dosen)
        course["dosen"] = unique_dosens

    return info
