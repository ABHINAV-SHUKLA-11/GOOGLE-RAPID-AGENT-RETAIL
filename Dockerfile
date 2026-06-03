# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (e.g., 5000 or 8080)
EXPOSE 8080

# Start command (change 'main.py' to your entry file)
CMD ["python", "main.py"]