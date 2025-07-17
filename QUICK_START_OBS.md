# Quick Start Guide - DeepFaceLive OBS-Style

## 🚀 Get Started in 5 Minutes

### 1. Launch the Application

**Option A: Using the launcher script (Recommended)**
```bash
python run_obs_style.py
```

**Option B: Using the main script**
```bash
python main.py run DeepFaceLiveOBS
```

### 2. Configure Your Camera

1. The application will start with the OBS-style interface
2. Your camera should automatically be detected
3. If not, check the traditional controls panel on the right side

### 3. Set Up Streaming (Optional)

1. Go to the **Streaming** tab in the right panel
2. Click **Configure Twitch** (or your preferred platform)
3. Enter your stream key
4. Set quality to **720p** for best performance
5. Click **Start Streaming** in the center panel

### 4. Set Up Recording (Optional)

1. Go to the **Recording** tab in the right panel
2. Choose **MP4** format
3. Set quality to **1080p**
4. Click **Start Recording** in the center panel

### 5. Start Face Swapping

1. Load your face swap model in the traditional controls
2. The face swap will automatically be applied to your stream/recording
3. Adjust quality settings in the **Video** tab if needed

## 🎯 Key Features to Try

### Multi-Platform Streaming
- Configure multiple platforms at once
- Stream to Twitch, YouTube, and Facebook simultaneously
- Each platform can have different quality settings

### Scene Management
- Create multiple scenes for different content
- Add overlays, images, and text to your scenes
- Switch between scenes during your stream

### Audio Controls
- Adjust microphone volume
- Include desktop audio
- Monitor your audio output

## 🔧 Performance Tips

### For Streaming
- Start with **720p** quality
- Use **2500 kbps** bitrate
- Set FPS to **30** for better performance

### For Recording
- Use **1080p** quality for best results
- Set bitrate to **8000 kbps**
- Choose **MP4** format for compatibility

### General
- Close other applications while streaming
- Use **Balanced** quality preset
- Set thread count to **4** for most systems

## 🆘 Need Help?

### Common Issues

**Application won't start:**
- Make sure you're in the DeepFaceLive root directory
- Check that all dependencies are installed
- Try running with `--no-cuda` flag

**Poor performance:**
- Reduce quality settings
- Close other applications
- Check your GPU drivers

**No camera detected:**
- Check camera permissions
- Try a different camera index
- Restart the application

### Getting More Help

- Read the full documentation: `OBS_STYLE_UI_README.md`
- Check the console output for error messages
- Try the traditional interface: `python run_obs_style.py --traditional`

## 🎉 What's Next?

Once you're comfortable with the basics:

1. **Explore Scene Management**: Create different scenes for different content
2. **Try Multi-Platform**: Stream to multiple platforms at once
3. **Customize Audio**: Set up proper audio monitoring
4. **Advanced Settings**: Fine-tune quality and performance settings
5. **Face Swap Models**: Load and configure different face swap models

## 📱 Keyboard Shortcuts

- **F11**: Toggle fullscreen
- **Ctrl+S**: Start/Stop streaming
- **Ctrl+R**: Start/Stop recording
- **Ctrl+Q**: Quit application

## 🎬 Example Workflow

1. **Setup**: Configure your streaming platforms and recording settings
2. **Prepare**: Load your face swap model and test the preview
3. **Stream**: Click "Start Streaming" and begin your content
4. **Record**: Click "Start Recording" to save your stream
5. **Switch Scenes**: Use the scene management to change your layout
6. **Monitor**: Keep an eye on FPS and audio levels
7. **End**: Stop streaming and recording when finished

Enjoy your new OBS-style DeepFaceLive experience! 🎥✨