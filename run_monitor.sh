#!/bin/bash

# Pharmaceutical News Monitor Runner Script

echo "=== Pharmaceutical News Monitor ==="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo
    echo "ERROR: OPENAI_API_KEY environment variable is not set!"
    echo "Please set it using: export OPENAI_API_KEY='your-key-here'"
    echo
    exit 1
fi

# Run the monitor
echo
echo "Starting news monitor..."
echo "Configuration: config.json"
echo "Output directory: data/"
echo
python pharma_news_monitor.py

echo
echo "Monitor completed! Check the data/ directory for results."