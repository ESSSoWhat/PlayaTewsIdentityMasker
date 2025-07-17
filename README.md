# DeepFaceLive - Professional Streaming Edition

🔥 Real-time face swapping in live video streams  
🎯 High-quality DeepFake technology  
🎥 **NEW**: OBS Studio-style interface with multi-platform streaming  
📹 **NEW**: Professional recording and scene management  

## ✨ New OBS-Style Interface

Transform your DeepFaceLive experience with our professional streaming interface inspired by OBS Studio!

### 🚀 Key Features

- **Multi-Platform Streaming**: Stream simultaneously to Twitch, YouTube, Facebook, and custom RTMP servers
- **Professional Recording**: High-quality recording in MP4, AVI, MOV, and FLV formats
- **Scene Management**: Create and switch between different streaming setups
- **Dark Theme UI**: Professional interface matching OBS Studio's design
- **Real-time Processing**: Seamless integration of face processing with streaming workflow

## 🎮 Quick Start

### Launch OBS-Style Interface

```bash
# Easy launch with dedicated script
python launch_obs_style.py

# Or use the main application
python main.py run DeepFaceLive --obs-style
```

### Traditional Interface

```bash
# Standard DeepFaceLive interface
python main.py run DeepFaceLive
```

## 📋 System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 1GB free disk space
- FFmpeg (for streaming/recording)

### Recommended for Streaming
- Python 3.9+
- 8GB+ RAM
- Dedicated GPU (NVIDIA recommended)
- 5GB+ free disk space
- Stable internet (5+ Mbps upload)

## 🛠️ Installation

### 1. Install Dependencies

```bash
# Install core requirements
pip install -r requirements_minimal.txt

# Install FFmpeg (required for streaming)
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS (with Homebrew):
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/download.html
```

### 2. Quick Setup

```bash
# Clone or download the repository
git clone <repository-url>
cd deepfacelive

# Launch the application
python launch_obs_style.py
```

## 🎥 Streaming Setup Guide

### Configure Platforms

1. **Add Platform** in the Stream Manager
2. **Select your platform**: Twitch, YouTube, Facebook, or Custom RTMP
3. **Enter stream key** and configure quality settings
4. **Test configuration** before going live

### Platform Settings

| Platform | Max Bitrate | Recommended | Max Resolution |
|----------|-------------|-------------|----------------|
| Twitch   | 6,000 kbps  | 3,500 kbps  | 1920x1080     |
| YouTube  | 51,000 kbps | 4,500 kbps  | 3840x2160     |
| Facebook | 4,000 kbps  | 2,000 kbps  | 1920x1080     |

### Recording Settings

- **Format**: MP4 (recommended), AVI, MOV, FLV
- **Quality**: High, Medium, Low, Custom
- **Auto-timestamped** file naming
- **Background recording** while streaming

## 🎬 Scene Management

- **Multiple scenes** for different streaming setups
- **Source types**: Camera, File Source, Face Swap, Text, Image
- **Layer ordering** with intuitive controls
- **Real-time switching** during live streams
- **Scene duplication** for quick setup

## 📖 Documentation

- **[Complete OBS-Style Guide](OBS_STYLE_INTERFACE_GUIDE.md)** - Comprehensive documentation
- **[Troubleshooting](OBS_STYLE_INTERFACE_GUIDE.md#troubleshooting)** - Common issues and solutions
- **[Advanced Configuration](OBS_STYLE_INTERFACE_GUIDE.md#advanced-configuration)** - Quality settings and optimization

## 🎯 Interface Comparison

### OBS-Style Interface (NEW)
✅ Multi-platform streaming  
✅ Professional recording  
✅ Scene management  
✅ Streaming-optimized UI  
✅ Real-time preview  
✅ Quality presets  

### Traditional Interface
✅ Face swapping  
✅ Model training  
✅ Basic recording  
✅ Advanced face processing  

## 🚀 Launch Commands

```bash
# OBS-Style interface (recommended for streaming)
python launch_obs_style.py

# With custom settings
python launch_obs_style.py --userdata-dir ./my_workspace --debug

# Traditional interface
python main.py run DeepFaceLive

# With specific options
python main.py run DeepFaceLive --userdata-dir ./workspace --no-cuda
```

## 🎨 Interface Preview

The OBS-Style interface features:

- **Left Panel**: Scene and streaming controls
- **Center Panel**: Live preview with professional controls
- **Right Panel**: Compact face processing controls
- **Menu System**: Professional streaming tools
- **Dark Theme**: Eye-friendly interface for long streaming sessions

## 🔧 Troubleshooting

### Common Issues

**Stream won't start?**
- Verify stream key and platform settings
- Check FFmpeg installation
- Test internet connection

**Poor quality?**
- Adjust bitrate for your internet speed
- Lower resolution if CPU usage is high
- Close unnecessary applications

**Face processing slow?**
- Enable GPU acceleration
- Reduce detection resolution
- Optimize scene complexity

See the [complete troubleshooting guide](OBS_STYLE_INTERFACE_GUIDE.md#troubleshooting) for more solutions.

## 🌟 What's New

### Version 2.0 - OBS-Style Interface
- ✨ Professional streaming interface
- 🎥 Multi-platform streaming support
- 📹 High-quality recording with multiple formats
- 🎬 Advanced scene management
- 🎨 Professional dark theme
- ⚡ Optimized streaming workflow

### Enhanced Features
- Real-time streaming statistics
- Automatic stream validation
- Professional menu system
- Compact face processing controls
- Background recording capability

## 🎯 Use Cases

### Content Creators
- Stream to multiple platforms simultaneously
- Create different scenes for various content types
- Record high-quality content for editing
- Professional appearance with dark theme

### Streamers
- Real-time face swapping during live streams
- Quick scene switching for dynamic content
- Multiple platform monetization
- Professional streaming workflow

### Developers
- Extensible interface for custom sources
- Plugin-ready architecture
- Professional codebase organization
- Modern Python streaming implementation

## 🚀 Getting Started Tips

1. **Start with the OBS-Style interface** for the best experience
2. **Configure one platform first** before adding multiple streams
3. **Test your setup** before going live
4. **Use scenes** to organize different streaming setups
5. **Monitor performance** and adjust quality as needed

---

**Ready to start streaming?** Launch with `python launch_obs_style.py` and experience professional-grade face swapping with streaming capabilities!
