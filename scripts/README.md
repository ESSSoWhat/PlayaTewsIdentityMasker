# Scripts Directory

This directory contains all the batch files, shell scripts, and setup scripts for the PlayaTews Identity Masker project.

## Directory Structure

```
scripts/
├── batch/          # Windows batch files (.bat)
├── shell/          # Unix/Linux shell scripts (.sh)
├── setup/          # Setup and installation scripts
└── README.md       # This file
```

## Batch Files (Windows)

Located in `scripts/batch/`

### Application Startup Scripts
- `start_playatews_app.bat` - Main application startup
- `start_app_local_python.bat` - Start with local Python installation
- `start_voice_changer.bat` - Voice changer server startup
- `start_voice_changer_alt.bat` - Alternative voice changer startup
- `start_voice_changer_minimal.bat` - Minimal voice changer startup
- `start_voice_changer_simple.bat` - Simple voice changer startup
- `start_voice_changer_working.bat` - Working voice changer startup

### Setup and Training Scripts
- `setup_local_python.bat` - Setup local Python environment
- `start_deepfacelab_trainer.bat` - DeepFaceLab trainer startup
- `train_facealigner.bat` - Face aligner training

## Shell Scripts (Unix/Linux)

Located in `scripts/shell/`

- `train_facealigner.sh` - Face aligner training (Unix/Linux version)

## Usage

### Windows Users
1. Navigate to the `scripts/batch/` directory
2. Run the appropriate batch file for your needs:
   - For main application: `start_playatews_app.bat`
   - For voice changer: `start_voice_changer.bat`
   - For setup: `setup_local_python.bat`

### Unix/Linux Users
1. Navigate to the `scripts/shell/` directory
2. Make scripts executable: `chmod +x *.sh`
3. Run the appropriate script: `./train_facealigner.sh`

## Script Descriptions

### Main Application Scripts
- **start_playatews_app.bat**: Launches the main PlayaTews Identity Masker application
- **start_app_local_python.bat**: Starts the application using a local Python installation

### Voice Changer Scripts
- **start_voice_changer.bat**: Standard voice changer server startup
- **start_voice_changer_alt.bat**: Alternative configuration for voice changer
- **start_voice_changer_minimal.bat**: Minimal voice changer setup
- **start_voice_changer_simple.bat**: Simple voice changer configuration
- **start_voice_changer_working.bat**: Known working voice changer setup

### Setup Scripts
- **setup_local_python.bat**: Sets up a local Python environment for the project
- **start_deepfacelab_trainer.bat**: Launches the DeepFaceLab trainer component
- **train_facealigner.bat/.sh**: Trains the face alignment model

## Notes

- All batch files are designed for Windows environments
- Shell scripts are designed for Unix/Linux environments
- Some scripts may require specific Python versions or dependencies
- Always check the requirements before running any script
- Backup your data before running training scripts

## Troubleshooting

If you encounter issues with any script:

1. Check that Python is installed and in your PATH
2. Verify all required dependencies are installed
3. Ensure you're running the script from the correct directory
4. Check the console output for error messages
5. Refer to the main project documentation for specific component issues 