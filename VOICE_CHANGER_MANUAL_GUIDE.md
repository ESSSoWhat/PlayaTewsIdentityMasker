# Voice Changer Manual Startup Guide

## Quick Start
1. Open Command Prompt as Administrator
2. Navigate to your project directory
3. Run: `start_voice_changer.bat`

## Manual Steps (if batch file doesn't work)

### Step 1: Navigate to Server Directory
```cmd
cd voice-changer\server
```

### Step 2: Install Requirements
```cmd
python -m pip install -r requirements.txt
```

### Step 3: Start Server
```cmd
python MMVCServerSIO.py
```

### Step 4: Access Web Interface
Open your browser and go to:
- http://localhost:8080
- http://localhost:8081 (alternative port)

## Troubleshooting

### If you get import errors:
1. Make sure you're in the correct directory
2. Try: `python -m pip install --upgrade pip`
3. Try: `python -m pip install -r requirements.txt --force-reinstall`

### If ports are in use:
1. Check what's using the ports: `netstat -ano | findstr :8080`
2. Kill the process or use a different port

### If server won't start:
1. Check the error messages
2. Look for missing dependencies
3. Try running as Administrator

## Common Issues

### Torch/TorchAudio Issues
If you get torch-related errors:
1. Try: `python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu`
2. Or: `python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118`

### Port Already in Use
If port 8080 is in use:
1. Find the process: `netstat -ano | findstr :8080`
2. Kill it: `taskkill /PID <PID> /F`
3. Or modify the server to use a different port

### Permission Issues
If you get permission errors:
1. Run Command Prompt as Administrator
2. Check file permissions
3. Make sure antivirus isn't blocking the application

## Support
- Check voice-changer/README.md for documentation
- Look for error messages in the console
- Check voice-changer/logs/ for log files
