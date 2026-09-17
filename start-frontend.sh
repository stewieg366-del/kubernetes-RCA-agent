#!/bin/bash
echo "Starting RCA Agent Frontend..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"
npm run dev
