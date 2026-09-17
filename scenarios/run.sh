#!/bin/bash
set -e

if [ "$#" -lt 2 ]; then
    echo "Usage: ./scenarios/run.sh <action> <scenario_name>"
    echo "Actions: trigger, reset, validate"
    echo "Scenarios: oom, bad-deployment, dependency-failure"
    exit 1
fi

ACTION=$1
SCENARIO=$2

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/${SCENARIO}/${ACTION}.sh"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Scenario script not found at $SCRIPT_PATH"
    exit 1
fi

chmod +x "$SCRIPT_PATH"
bash "$SCRIPT_PATH"
