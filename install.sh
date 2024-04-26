#!/bin/bash

# Exit on any error
set -e

# Define directory variables
REPO_URL="https://github.com/conlan0/jarvis.git"
INSTALL_DIR="/opt/jarvis"
SERVICE_USER="jarvis"

# Update and upgrade the system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python3, pip, virtualenv, and git
sudo apt-get install -y python3 python3-pip python3-venv git

# Create a non-root user for running the application
sudo useradd -r -s /bin/false $SERVICE_USER || true  # Ignore if user already exists

# Ensure the installation directory exists and has proper ownership
sudo mkdir -p $INSTALL_DIR
sudo chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR

# Clone the application repository
sudo -u $SERVICE_USER git clone $REPO_URL $INSTALL_DIR

# Set up a Python virtual environment
cd $INSTALL_DIR
sudo -u $SERVICE_USER python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file and request OpenAI API credentials from the user
echo "Creating .env file..."
touch .env

# Adding sleep to allow the user to see what is happening before the first input
echo "Please enter your OpenAI API key:"
read -p "API Key: " openai_api_key
echo "OPENAI_API_KEY=$openai_api_key" >> .env

# Clear prompt for Assistant ID
echo "Please enter your Assistant ID:"
read -p "Assistant ID: " assistant_id
echo "ASSISTANT_ID=$assistant_id" >> .env

# Clear prompt for Chat Thread ID
echo "Please enter your Chat Thread ID:"
read -p "Chat Thread ID: " chat_thread_id
echo "CHAT_THREAD_ID=$chat_thread_id" >> .env

# Create systemd service file
cat <<EOF | sudo tee /etc/systemd/system/jarvis.service
[Unit]
Description=AI Jarvis Voice Assistant
After=network.target

[Service]
User=$SERVICE_USER
EnvironmentFile=$INSTALL_DIR/.env
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python jarvis.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable and start the new service
sudo systemctl enable jarvis.service
sudo systemctl start jarvis.service

echo "Jarvis application installation and service setup completed successfully."
