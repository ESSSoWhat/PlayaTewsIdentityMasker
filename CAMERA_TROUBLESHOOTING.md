# DeepFaceLive Camera Troubleshooting Guide

## ✅ Camera Status: WORKING

Your camera is working correctly! The test results show:
- **2 cameras detected**: Camera 0 (1280x720) and Camera 1 (1920x1080)
- **Camera capture working**: Successfully capturing frames
- **Models loading**: All face swap models available

## 🔍 If Camera Doesn't Appear in DeepFaceLive UI

### Step 1: Check Camera Source Settings

1. **Open DeepFaceLive**
2. **Navigate to the Camera Source panel** (usually in the first column)
3. **Enable Camera Source** by checking the box
4. **Select Camera Device**:
   - Try "Camera 0" first (1280x720)
   - If that doesn't work, try "Camera 1" (1920x1080)
5. **Select Camera Backend**:
   - Try "DirectShow" first
   - If that doesn't work, try "Compatible"
   - Other options: "Microsoft Media Foundation", "GStreamer"

### Step 2: Check Camera Resolution

1. **In Camera Source panel**, look for resolution settings
2. **Try different resolutions**:
   - Start with 640x480 (most compatible)
   - Then try 1280x720
   - Finally try 1920x1080

### Step 3: Check Camera Rotation

1. **Look for rotation settings** in Camera Source panel
2. **Try different rotations**: 0°, 90°, 180°, 270°
3. **Some cameras need rotation** to display correctly

### Step 4: Enable Processing Pipeline

Make sure these components are enabled:
1. **Camera Source** ✅ (should be enabled)
2. **Face Detector** ✅ (should be enabled)
3. **Face Aligner** ✅ (should be enabled)
4. **Face Swap DFM** ✅ (should be enabled)
5. **Face Merger** ✅ (should be enabled)

### Step 5: Check Frame Viewer

1. **Look for frame viewer panels** in the interface
2. **Camera frames should appear** in the viewer
3. **If frames are black**, try different camera settings

## 🔧 Advanced Troubleshooting

### If Camera Still Doesn't Appear:

1. **Restart DeepFaceLive**:
   ```bash
   # Kill existing processes
   taskkill /f /im python.exe
   
   # Restart the app
   .venv/Scripts/python.exe main.py run DeepFaceLive --userdata-dir .
   ```

2. **Check Camera Permissions**:
   - Ensure Windows allows camera access
   - Check if other apps are using the camera
   - Close other camera applications

3. **Try Different Camera Backends**:
   - DirectShow (most common)
   - Compatible (fallback)
   - Microsoft Media Foundation
   - GStreamer

4. **Check Camera Drivers**:
   - Update camera drivers
   - Ensure camera is recognized by Windows

### If Camera Appears But No Face Swap:

1. **Select a DFM Model**:
   - Go to Face Swap DFM panel
   - Select a model like "Keanu_Reeves" or "Mr_Bean"
   - Wait for model to load

2. **Check Model Loading**:
   - Look for model download progress
   - Ensure model files are in `dfm_models/` directory

3. **Enable Face Detection**:
   - Make sure Face Detector is enabled
   - Check if faces are being detected

## 📊 Expected Behavior

### When Working Correctly:
- **Camera feed appears** in frame viewer
- **Face detection boxes** appear around faces
- **Face swap effect** applied to detected faces
- **Real-time processing** at 25-30 FPS

### Performance Indicators:
- **GPU usage**: 40-70% (depending on model)
- **CPU usage**: 30-50%
- **Memory usage**: 2-4GB RAM
- **Frame rate**: 25-60 FPS

## 🐛 Common Issues and Solutions

### Issue: Black Camera Feed
**Solution**: 
- Try different camera backends
- Check camera permissions
- Restart the application

### Issue: Camera Not Detected
**Solution**:
- Update camera drivers
- Check Windows Device Manager
- Try different camera indices

### Issue: Face Swap Not Working
**Solution**:
- Select a DFM model
- Ensure face detection is enabled
- Check model loading status

### Issue: Low Frame Rate
**Solution**:
- Use lower resolution models
- Reduce camera resolution
- Close other applications

## ✅ Verification Checklist

- [ ] Camera Source enabled
- [ ] Camera device selected
- [ ] Camera backend selected
- [ ] Resolution set appropriately
- [ ] Face Detector enabled
- [ ] Face Aligner enabled
- [ ] Face Swap DFM enabled
- [ ] Face Merger enabled
- [ ] DFM model selected
- [ ] Camera feed visible in frame viewer

## 🚀 Quick Fix Commands

```bash
# Restart DeepFaceLive
taskkill /f /im python.exe
.venv/Scripts/python.exe main.py run DeepFaceLive --userdata-dir .

# Test camera functionality
.venv/Scripts/python.exe test_camera_fix.py

# Check GPU support
.venv/Scripts/python.exe test_gpu_setup.py
```

## 📞 Still Having Issues?

If the camera still doesn't appear after trying these steps:

1. **Check the console output** for error messages
2. **Try different camera settings** in the interface
3. **Test with a different camera** if available
4. **Check Windows camera privacy settings**
5. **Ensure no other applications are using the camera**

Your camera is working correctly - the issue is likely in the DeepFaceLive interface configuration! 