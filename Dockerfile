FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app /app/app

# Use Waitress to run the application
CMD ["python", "-c", "import os; from waitress import serve; from app.main import app; serve(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))"]