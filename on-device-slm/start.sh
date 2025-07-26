#!/bin/bash
echo "Starting On-Device LLM Assistant..."
cd "$(dirname "$0")"

# Check if Ollama service is running
echo "Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Activate virtual environment
source venv/bin/activate

# Start the application
python launcher.py
