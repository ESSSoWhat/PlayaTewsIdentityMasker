# Voice Changer Troubleshooting Guide

## Issues Found and Fixed

### 1. TorchAudio Import Error
**Problem**: `[WinError 127] The specified procedure could not be found`
**Solution**: Reinstall torchaudio with CPU version
```cmd
python -m pip uninstall torchaudio -y
python -m pip install torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. Server File Encoding Issue
**Problem**: `'charmap' codec can't decode byte`
**Solution**: Fixed file encoding to UTF-8

## Startup Options

### Option 1: Working Startup Script
Run: `start_voice_changer_working.bat`
- Automatically fixes torchaudio
- Installs all dependencies
- Tests server before starting

### Option 2: Alternative Server
If the main server still has issues:
```cmd
cd voice-changer\server
python MMVCServerSIO_alt.py
```

### Option 3: Manual Steps
1. Fix torchaudio:
   ```cmd
   python -m pip uninstall torchaudio -y
   python -m pip install torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

2. Install dependencies:
   ```cmd
   cd voice-changer\server
   python -m pip install uvicorn fastapi websockets numpy scipy
   python -m pip install librosa sounddevice resampy
   python -m pip install onnxruntime faiss-cpu torchcrepe
   ```

3. Start server:
   ```cmd
   python MMVCServerSIO.py
   ```

## Accessing Voice Changer

Once the server is running:
1. Open your browser
2. Go to: http://localhost:8080
3. You should see the voice changer interface

## Troubleshooting

### If server won't start:
1. Check error messages in console
2. Ensure no other applications are using port 8080
3. Try running as Administrator
4. Check antivirus isn't blocking the application

### If torchaudio still fails:
1. Try: `python -m pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu`
2. Or use the alternative server

### If encoding issues persist:
1. Use the alternative server: `MMVCServerSIO_alt.py`
2. Or manually fix the encoding of the server file

## Support
- Check voice-changer/README.md for documentation
- Look for error messages in the console
- Check voice-changer/logs/ for log files
