# DeepFaceLive Anonymous Streaming - Testing Guide

## 🧪 Testing Methods

### 1. **Basic Verification Test**
Run the basic test script to verify all components are properly installed:

```bash
python test_app.py
```

This will test:
- ✅ File structure
- ✅ Import capabilities
- ✅ Directory creation
- ✅ Enum definitions

### 2. **Full Application Test**

#### Prerequisites
- Webcam connected and working
- Python environment with required dependencies
- DirectX12 compatible graphics card

#### Step 1: Start the Application
```bash
python main.py run DeepFaceLive
```

#### Step 2: Verify New UI Components
Look for these new panels in the interface:
- **Mask Manager** (5th column)
- **Multi-Platform Streamer** (5th column)
- **Enhanced Recorder** (5th column)

### 3. **Feature-by-Feature Testing**

## 🎭 Testing Mask Management

### Test 1: Basic Mask Types
1. **Start the application**
2. **Navigate to Mask Manager panel**
3. **Test each mask type**:
   - Select "None" - should show normal video
   - Select "Blur" - should apply blur effect
   - Select "Pixelate" - should apply pixelation
   - Select "Anonymous" - should show black bars over eyes/mouth
   - Select "Custom" - should enable custom mask path

### Test 2: Mask Intensity
1. **Select any mask type** (except None)
2. **Adjust intensity slider** (0-100%)
3. **Verify effect changes** in real-time
4. **Test extreme values** (0% and 100%)

### Test 3: Custom Mask Upload
1. **Prepare a test image** (PNG, JPEG, GIF, or WebP)
2. **Select "Custom" mask type**
3. **Click "Upload Mask" button**
4. **Select your test image**
5. **Verify mask appears** in the video feed
6. **Adjust intensity** to see blending effect

## 🌐 Testing Multi-Platform Streaming

### Test 1: Platform Enable/Disable
1. **Navigate to Multi-Platform Streamer panel**
2. **Test each platform checkbox**:
   - OBS Virtual Camera
   - OBS NDI
   - Discord
   - Zoom
   - Teams
   - Skype
   - Custom RTMP
   - Custom UDP
3. **Verify checkboxes work** without errors

### Test 2: Custom Settings
1. **Enable Custom RTMP**
2. **Enter test URL**: `rtmp://localhost/live/test`
3. **Verify URL is saved**
4. **Enable Custom UDP**
5. **Set address**: `127.0.0.1`
6. **Set port**: `1234`
7. **Verify settings are saved**

### Test 3: FPS Monitoring
1. **Start camera feed**
2. **Check "Avg FPS" display**
3. **Verify FPS updates** in real-time
4. **Test with different mask types** to see performance impact

## 📹 Testing Enhanced Recording

### Test 1: Recording Formats
1. **Navigate to Enhanced Recorder panel**
2. **Test each recording format**:
   - MP4
   - AVI
   - MOV
   - MKV
   - WEBM
   - Image Sequence
3. **Verify format selection works**

### Test 2: Recording Settings
1. **Set recording path** to a test directory
2. **Adjust quality** (1-100)
3. **Set FPS** (1-60)
4. **Enable auto-start recording**
5. **Set duration limit** (e.g., 60 seconds)
6. **Verify all settings save** correctly

### Test 3: Recording Functionality
1. **Configure recording settings**
2. **Click "Is Recording" checkbox**
3. **Verify recording starts**
4. **Check output directory** for recorded files
5. **Stop recording** and verify files are complete

## 🔧 Integration Testing

### Test 1: Pipeline Integration
1. **Enable camera source**
2. **Enable face detection**
3. **Enable mask manager** with any mask
4. **Enable multi-platform streaming**
5. **Enable enhanced recording**
6. **Verify all components work together**

### Test 2: Performance Testing
1. **Monitor FPS** with different combinations
2. **Test with high-intensity masks**
3. **Enable multiple platforms simultaneously**
4. **Start recording while streaming**
5. **Verify system remains stable**

### Test 3: Error Handling
1. **Test with invalid mask files**
2. **Test with invalid streaming URLs**
3. **Test with full disk space**
4. **Verify graceful error handling**

## 📊 Performance Benchmarks

### Expected Performance
- **Base FPS**: 25-30 FPS (depending on hardware)
- **With Blur Mask**: 20-25 FPS
- **With Pixelate Mask**: 22-27 FPS
- **With Anonymous Mask**: 25-30 FPS
- **With Custom Mask**: 20-25 FPS

### Resource Usage
- **CPU**: 30-50% (depending on mask type)
- **GPU**: 40-70% (depending on mask type)
- **Memory**: 2-4GB RAM
- **Disk**: Varies based on recording settings

## 🐛 Troubleshooting

### Common Issues

#### Issue: Application won't start
**Solution**:
1. Check Python dependencies
2. Verify DirectX12 compatibility
3. Check webcam availability
4. Review console output for errors

#### Issue: Masks not appearing
**Solution**:
1. Verify mask type is selected
2. Check intensity setting
3. Ensure camera feed is active
4. Test with different mask types

#### Issue: Recording not working
**Solution**:
1. Check recording path permissions
2. Verify disk space
3. Test with different formats
4. Check recording settings

#### Issue: Streaming platforms not connecting
**Solution**:
1. Verify platform-specific requirements
2. Check network connectivity
3. Test with different URLs
4. Review platform documentation

### Debug Information
- **Console Output**: Check for error messages
- **Log Files**: Review application logs
- **Performance Monitor**: Monitor system resources
- **Network Monitor**: Check streaming connections

## ✅ Success Criteria

### Basic Functionality
- ✅ Application starts without errors
- ✅ All new UI panels are visible
- ✅ Camera feed works normally
- ✅ Mask effects apply correctly
- ✅ Recording starts and stops
- ✅ Platform checkboxes work

### Advanced Features
- ✅ Custom mask upload works
- ✅ Mask intensity adjustment works
- ✅ Multiple recording formats work
- ✅ Auto-recording works
- ✅ Duration limits work
- ✅ FPS monitoring works

### Integration
- ✅ All components work together
- ✅ Performance is acceptable
- ✅ Error handling works
- ✅ Settings persist between sessions

## 📝 Test Report Template

Use this template to document your testing:

```
Test Date: _______________
Tester: _________________

✅ Basic Tests
- [ ] Application starts
- [ ] All UI panels visible
- [ ] Camera feed works
- [ ] No console errors

✅ Mask Management
- [ ] None mask works
- [ ] Blur mask works
- [ ] Pixelate mask works
- [ ] Anonymous mask works
- [ ] Custom mask upload works
- [ ] Intensity adjustment works

✅ Multi-Platform Streaming
- [ ] All platform checkboxes work
- [ ] Custom RTMP settings work
- [ ] Custom UDP settings work
- [ ] FPS monitoring works

✅ Enhanced Recording
- [ ] All recording formats work
- [ ] Quality settings work
- [ ] FPS settings work
- [ ] Auto-start works
- [ ] Duration limits work

✅ Integration
- [ ] All components work together
- [ ] Performance is acceptable
- [ ] Error handling works
- [ ] Settings persist

Performance Notes:
- Base FPS: _______
- With Blur Mask: _______
- With Pixelate Mask: _______
- With Anonymous Mask: _______

Issues Found:
1. _________________
2. _________________
3. _________________

Overall Assessment: ✅ PASS / ❌ FAIL
```

## 🚀 Quick Start Testing

For a quick test of all features:

1. **Run basic test**: `python test_app.py`
2. **Start application**: `python main.py run DeepFaceLive`
3. **Enable camera source**
4. **Select "Blur" mask with 50% intensity**
5. **Enable "OBS Virtual Camera"**
6. **Start recording in MP4 format**
7. **Verify everything works together**

This should give you a complete test of the anonymous streaming capabilities! 