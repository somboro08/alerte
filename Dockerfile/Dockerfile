# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Install WeasyPrint system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libharfbuzz0b \
    libffi-dev \
    shared-mime-info

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
# Copy only requirements.txt to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 for the Gunicorn server
EXPOSE 8000

# Run the application using Gunicorn
# 'app:app' refers to the Flask application instance 'app' within the 'app.py' file
# The --bind 0.0.0.0:$PORT makes Gunicorn listen on the port provided by the environment variable,
# which is common in platforms like Render. Default to 8000 if not set.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]