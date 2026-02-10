#!/bin/bash
echo "Starting AI Chatbot..."
cd ~/ai-business-chatbot/backend
source venv/bin/activate
cd app
python3 main.py
