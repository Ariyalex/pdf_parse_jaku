# Railway Backend Project

This project is a backend application that accepts a PDF file as input and outputs a structured JSON file. It utilizes Flask for handling web requests and PyMuPDF for PDF processing.

## Project Structure

```
railway-backend
├── app
│   ├── main.py          # Entry point of the application
│   ├── pdf_processor.py  # Logic for processing PDF files
│   └── utils
│       └── __init__.py  # Utility functions and classes
├── requirements.txt      # Project dependencies
├── Dockerfile             # Docker image instructions
├── .dockerignore          # Files to ignore in Docker builds
├── .gitignore             # Files to ignore in Git
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd railway-backend
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application:**
   Start the Flask server:
   ```
   python app/main.py
   ```

4. **Using Docker:**
   To build and run the application using Docker, execute the following commands:
   ```
   docker build -t railway-backend .
   docker run -p 5000:5000 railway-backend
   ```

## Usage

- Send a POST request to `/upload` with the PDF file as form data.
- The server will process the PDF and return a JSON file containing the extracted data.

## License

This project is licensed under the MIT License. See the LICENSE file for details.