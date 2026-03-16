# Use an official Python base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy all project files to the container
COPY . .

# Install dependencies (Flask, etc.)
RUN pip install --no-cache-dir flask

# Expose the port your app will run on
EXPOSE 80

# Command to run the Flask app
CMD ["python", "app.py"]
