FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app /app/app

# Create uploads directory
RUN mkdir -p /app/app/uploads

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting application..."\n\
echo "PORT: $PORT"\n\
python -c "import os; from waitress import serve; from app.main import app; serve(app, host=\"0.0.0.0\", port=int(os.environ.get(\"PORT\", 8080)))"' > /app/start.sh

# Make startup script executable
RUN chmod +x /app/start.sh

# Use the startup script
CMD ["/app/start.sh"]