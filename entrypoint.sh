#!/bin/bash
set -e

# Start Ollama in the background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
echo "Waiting for Ollama to start..."
sleep 5

# Check if the model exists, pull only if it doesn't
if ! ollama list | grep -q "gemma2:2b"; then
  echo "Model gemma2:2b not found, pulling..."
  ollama pull gemma2:2b
else
  echo "Model gemma2:2b already exists, skipping pull"
fi

# Start the Python app
echo "Starting Python application..."
python3 app.py