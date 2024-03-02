# Use the official Python 3.8 slim image as the base image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Update the package list and install necessary dependencies
RUN apt-get update && \
    apt-get install -y python3-dev default-libmysqlclient-dev build-essential pkg-config && \
    # Upgrade pip to the latest version
    pip install --upgrade pip && \
    # Install dependencies specified in requirements.txt
    pip install -r requirements.txt && \
    # Remove build-essential, which is no longer needed after installation
    apt-get remove -y build-essential && \
    # Remove any automatically installed and no longer required packages
    apt-get autoremove -y && \
    # Clean up the package cache to reduce image size
    apt-get clean && \
    # Remove the package list files to free up space
    rm -rf /var/lib/apt/lists/*

# Expose port 6000 for the Flask application
EXPOSE 6000

# Make the script.sh file executable
RUN chmod +x script.sh

# Set the default command to run the script.sh when the container starts
CMD ["./script.sh"]
