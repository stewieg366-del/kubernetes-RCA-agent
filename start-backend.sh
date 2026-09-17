#!/bin/bash
echo "Starting RCA Agent Backend..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
else
    echo "Warning: Could not find venv/bin/activate"
fi

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
