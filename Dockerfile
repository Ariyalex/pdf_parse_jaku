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
CMD ["python", "-m", "waitress", "--port", "${PORT:-5000}", "app.main:app"]