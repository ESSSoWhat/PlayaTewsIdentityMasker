# OBS-Style DeepFaceLive Interface Guide

## Overview

The OBS-Style interface transforms DeepFaceLive into a professional streaming and recording application similar to OBS Studio. This interface provides:

- **Multi-platform streaming** to Twitch, YouTube, Facebook, and custom RTMP servers
- **High-quality recording** in multiple formats (MP4, AVI, MOV, FLV)
- **Scene management** with customizable sources
- **Professional dark theme** matching OBS Studio's appearance
- **Real-time face processing** integrated with streaming workflow

## Features

### 🎥 Streaming Capabilities
- **Simultaneous multi-platform streaming** - Stream to multiple platforms at once
- **Platform support**: Twitch, YouTube, Facebook, Custom RTMP
- **Configurable quality settings**: Bitrate, resolution, FPS
- **Real-time streaming status** with statistics
- **Automatic stream validation** and error handling

### 📹 Recording Features
- **Multiple format support**: MP4, AVI, MOV, FLV
- **Quality presets**: High, Medium, Low, Custom
- **Timestamped file naming** for easy organization
- **Configurable resolution and framerate**
- **Background recording** while streaming

### 🎬 Scene Management
- **Multiple scenes** with instant switching
- **Source management**: Camera, File Source, Face Swap, Text, Image
- **Layer ordering** with drag-and-drop support
- **Scene duplication** and customization
- **Real-time source preview**

### 🎨 Professional Interface
- **OBS Studio-inspired design** with dark theme
- **Three-panel layout**: Scenes/Streaming, Preview, Face Processing
- **Compact controls** optimized for streaming workflow
- **Menu system** with professional streaming tools
- **Responsive layout** adapting to different screen sizes

## Getting Started

### Quick Launch

```bash
# Using the dedicated launch script (recommended)
python launch_obs_style.py

# Or using the main application with flag
python main.py run DeepFaceLive --obs-style
```

### Launch Options

```bash
# Basic launch
python launch_obs_style.py

# Custom user data directory
python launch_obs_style.py --userdata-dir /path/to/userdata

# Disable CUDA (CPU-only mode)
python launch_obs_style.py --no-cuda

# Enable debug mode
python launch_obs_style.py --debug
```

## Interface Layout

### Left Panel: Scenes and Streaming

**Scene Manager**
- **Add Scene**: Create new scenes for different streaming setups
- **Remove Scene**: Delete selected scenes
- **Duplicate Scene**: Copy scenes with all sources
- **Scene List**: Switch between scenes instantly
- **Sources**: Manage sources within each scene

**Stream Manager**
- **Start/Stop Streaming**: Begin streaming to configured platforms
- **Start/Stop Recording**: Record your content locally
- **Platform List**: View and configure streaming platforms
- **Recording Settings**: Choose format and quality

### Center Panel: Main Preview

**Preview Area**
- **Live preview** of current scene output
- **Real-time face processing** visualization
- **Studio Mode** for professional transitions (planned)
- **Preview controls**: Fullscreen, screenshots

### Right Panel: Face Processing

**Compact Controls**
- **Camera Source**: Configure video input
- **Face Detection**: Adjust detection settings
- **Face Swap**: Select and configure face swap models
- **Essential controls only** for streamlined workflow

## Streaming Setup

### 1. Configure Streaming Platforms

1. **Click "Add Platform"** in the Stream Manager
2. **Select platform**: Twitch, YouTube, Facebook, or Custom RTMP
3. **Click "Configure"** to enter stream details:
   - **Stream Key**: Your platform-specific stream key
   - **Server URL**: Auto-filled for major platforms
   - **Bitrate**: Recommended values provided per platform
4. **Test configuration** before going live

### Platform-Specific Settings

**Twitch**
- Server: `rtmp://live.twitch.tv/live`
- Max Bitrate: 6,000 kbps
- Recommended: 3,500 kbps
- Max Resolution: 1920x1080

**YouTube**
- Server: `rtmp://a.rtmp.youtube.com/live2`
- Max Bitrate: 51,000 kbps
- Recommended: 4,500 kbps
- Max Resolution: 3840x2160

**Facebook**
- Server: `rtmps://live-api-s.facebook.com:443/rtmp`
- Max Bitrate: 4,000 kbps
- Recommended: 2,000 kbps
- Max Resolution: 1920x1080

### 2. Setup Recording

1. **Choose format**: MP4 (recommended), AVI, MOV, or FLV
2. **Select quality**: High, Medium, Low, or Custom
3. **Recording location**: Automatically saved to `recordings/` folder
4. **File naming**: Auto-timestamped (e.g., `deepface_recording_20231215_143052.mp4`)

### 3. Configure Scenes

1. **Create scenes** for different streaming scenarios
2. **Add sources** to each scene:
   - **Camera**: Live video input
   - **File Source**: Pre-recorded videos
   - **Face Swap**: Real-time face replacement
   - **Text**: Overlays and titles
   - **Image**: Static graphics and logos
3. **Arrange sources** using up/down controls
4. **Switch scenes** during live streams

## Technical Requirements

### Dependencies

```bash
# Install required packages
pip install -r requirements_minimal.txt

# Additional streaming dependencies
pip install ffmpeg-python>=0.2.0
```

### System Requirements

**Minimum**
- Python 3.8+
- 4GB RAM
- Integrated graphics
- 1GB free disk space

**Recommended for Streaming**
- Python 3.9+
- 8GB+ RAM
- Dedicated GPU (NVIDIA recommended)
- 5GB+ free disk space
- Stable internet (upload speed ≥ 5 Mbps)

**FFmpeg Installation**

The streaming engine requires FFmpeg to be installed:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS (with Homebrew)
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
# Add to system PATH
```

## Advanced Configuration

### Stream Quality Settings

**Bitrate Guidelines**
- **Low quality**: 1,000-2,000 kbps
- **Medium quality**: 2,000-4,000 kbps  
- **High quality**: 4,000-8,000 kbps
- **Ultra quality**: 8,000+ kbps (YouTube only)

**Resolution Options**
- **720p**: 1280x720 (good for most streams)
- **1080p**: 1920x1080 (high quality)
- **1440p**: 2560x1440 (premium quality)
- **4K**: 3840x2160 (YouTube only)

**Frame Rate Settings**
- **30 FPS**: Standard for most content
- **60 FPS**: Smooth motion, higher bandwidth
- **Custom**: 24, 25, 50 FPS for specific needs

### Recording Quality Presets

**High Quality**
- Format: MP4
- Codec: H.264
- Bitrate: Variable (high)
- Resolution: 1920x1080
- FPS: 30

**Medium Quality**
- Format: MP4
- Codec: H.264
- Bitrate: 5,000 kbps
- Resolution: 1920x1080
- FPS: 30

**Low Quality**
- Format: MP4
- Codec: H.264
- Bitrate: 2,000 kbps
- Resolution: 1280x720
- FPS: 30

## Troubleshooting

### Common Issues

**Stream Not Starting**
1. Verify stream key is correct
2. Check internet connection
3. Ensure FFmpeg is installed
4. Verify platform-specific settings

**Poor Stream Quality**
1. Reduce bitrate for unstable connections
2. Lower resolution if CPU usage is high
3. Close unnecessary applications
4. Check upload bandwidth

**Recording Issues**
1. Ensure sufficient disk space
2. Check write permissions for recordings folder
3. Try different format (MP4 recommended)
4. Verify FFmpeg installation

**Face Processing Slow**
1. Enable GPU acceleration if available
2. Reduce face detection resolution
3. Optimize scene complexity
4. Close background applications

### Performance Optimization

**For Better Streaming**
1. **Use hardware encoding** when available
2. **Close unnecessary applications**
3. **Use wired internet connection**
4. **Monitor CPU/GPU usage**
5. **Test stream settings** before going live

**For Better Recording**
1. **Record to fast storage** (SSD recommended)
2. **Use efficient codecs** (H.264)
3. **Monitor disk space**
4. **Regular cleanup** of old recordings

## Tips and Best Practices

### Streaming Tips

1. **Test everything** before going live
2. **Have backup streams** configured
3. **Monitor chat** and stream health
4. **Use scenes** for smooth transitions
5. **Keep source material** organized

### Scene Management

1. **Name scenes descriptively** (e.g., "Intro", "Gameplay", "Outro")
2. **Duplicate scenes** for variations
3. **Test scene switches** before streaming
4. **Keep sources organized** by priority
5. **Use consistent** audio levels

### Recording Workflow

1. **Check available space** before recording
2. **Use timestamp naming** for organization
3. **Back up important recordings**
4. **Monitor recording status** during streams
5. **Test playback quality** regularly

## Support and Resources

### Getting Help

1. **Check this guide** for common solutions
2. **Review error messages** for specific issues
3. **Test with minimal setup** to isolate problems
4. **Check system requirements** and dependencies

### Additional Resources

- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **Streaming Guides**: Platform-specific streaming tutorials
- **Performance Monitoring**: Built-in stats and monitoring tools

## Future Enhancements

### Planned Features

- **Audio mixing** and advanced audio controls
- **Scene transitions** with effects
- **Plugin system** for custom sources
- **Stream overlays** and widgets
- **Advanced recording** options
- **Stream analytics** and monitoring
- **Cloud integration** for settings sync

### Contributing

The OBS-Style interface is designed to be extensible. Contributions are welcome for:

- New streaming platforms
- Additional source types
- UI improvements
- Performance optimizations
- Bug fixes and stability improvements

---

**Note**: This interface is designed for users familiar with streaming and content creation. For basic face swapping without streaming, use the standard DeepFaceLive interface.