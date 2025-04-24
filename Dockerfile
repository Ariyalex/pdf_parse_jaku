FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/app/uploads

# Use Railway's PORT environment variable with a shell command
CMD sh -c "gunicorn --workers=2 --threads=4 --timeout=120 --bind 0.0.0.0:\${PORT:-8080} app.main:app"