#!/bin/bash

echo "Starting FaceAligner Trainer..."
echo

# Check for most up-to-date launch resources
echo "Checking for most up-to-date launch resources..."
echo

# Check if git is available and this is a git repository
if command -v git &> /dev/null; then
    # Check if we're in a git repository
    if git rev-parse --git-dir &> /dev/null; then
        echo "Git repository detected. Checking for updates..."
        
        # Fetch latest changes from remote
        if git fetch --quiet; then
            # Check if local is behind remote
            BEHIND_COUNT=$(git rev-list HEAD...origin/main --count 2>/dev/null)
            if [ "$BEHIND_COUNT" -gt 0 ] 2>/dev/null; then
                echo "Warning: Local repository is $BEHIND_COUNT commits behind remote"
                echo "Consider running 'git pull' to update to the latest version"
                echo
                read -p "Do you want to update now? (y/n): " UPDATE_CHOICE
                if [[ "$UPDATE_CHOICE" =~ ^[Yy]$ ]]; then
                    echo "Updating repository..."
                    if git pull; then
                        echo "Repository updated successfully"
                    else
                        echo "Error: Failed to update repository"
                        echo "Continuing with current version..."
                    fi
                fi
            else
                echo "Repository is up to date"
            fi
        else
            echo "Warning: Could not fetch latest changes from remote repository"
        fi
    else
        echo "Not a git repository - skipping update check"
    fi
else
    echo "Git not available - skipping update check"
fi

# Check for critical resource files
echo "Checking critical resource files..."
if [ ! -f "train_facealigner.py" ]; then
    echo "Error: train_facealigner.py not found"
    echo "Please ensure all required files are present"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "Warning: requirements.txt not found"
    echo "Dependencies may not be properly installed"
fi

echo "Resource check completed."
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