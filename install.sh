#!/bin/bash

# Exit on any error
set -e

# Define directory variables
REPO_URL="https://github.com/conlan0/jarvis.git"
INSTALL_DIR="/opt/jarvis"

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python3, pip, virtualenv, and git
sudo apt-get install -y python3 python3-pip python3-venv git portaudio19-dev

# Ensure the installation directory exists
sudo mkdir -p $INSTALL_DIR
sudo chown $USER:$USER $INSTALL_DIR

# Clone the application repository
git clone $REPO_URL $INSTALL_DIR

# Set up a Python virtual environment
cd $INSTALL_DIR
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install sounddevice to list audio devices
pip install sounddevice

# List available audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Create .env file and request OpenAI API credentials from the user
echo "Creating .env file..."
touch .env

# Request the device index for the microphone
echo "Please enter the device index you would like to use for Jarvis:"
read -p "Device Index: " device_index
echo "DEVICE_INDEX=$device_index" >> .env

# Request OpenAI API key
echo "Please enter your OpenAI API key:"
read -p "API Key: " openai_api_key
echo "OPENAI_API_KEY=$openai_api_key" >> .env

# Request for Assistant ID
echo "Please enter your Assistant ID:"
read -p "Assistant ID: " assistant_id
echo "ASSISTANT_ID=$assistant_id" >> .env

# Request for Chat Thread ID
echo "Please enter your Chat Thread ID:"
read -p "Chat Thread ID: " chat_thread_id
echo "CHAT_THREAD_ID=$chat_thread_id" >> .env

# Make Jarvis dir writable for application
sudo chmod 777 /opt/jarvis

echo "Jarvis application installation completed successfully."
