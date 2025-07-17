#!/bin/bash

echo "Starting FaceAligner Trainer..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    echo "Please install Python3 and try again"
    exit 1
fi

# Set default workspace and faceset paths if not provided
WORKSPACE_DIR=${1:-"./workspace"}
FACESET_PATH=${2:-"./faceset.dfs"}

echo "Workspace Directory: $WORKSPACE_DIR"
echo "Faceset Path: $FACESET_PATH"
echo

# Run the FaceAligner trainer
python3 train_facealigner.py --workspace-dir "$WORKSPACE_DIR" --faceset-path "$FACESET_PATH"

echo
echo "FaceAligner training completed."