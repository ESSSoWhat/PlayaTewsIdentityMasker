# PlayaTewsIdentityMasker - Professional Face-Swapping & Streaming

🔥 Real-time face swapping with professional streaming capabilities  
🎯 High-quality face processing technology  
🎥 **OBS Studio-style interface** - Now the primary interface!  
📹 **Multi-platform streaming** to Twitch, YouTube, Facebook  
🎬 **Professional recording** and scene management  

## 🚀 OBS-Style Interface (Primary)

PlayaTewsIdentityMasker now features a professional streaming interface inspired by OBS Studio as the main interface!

### 🚀 Key Features

- **Multi-Platform Streaming**: Stream simultaneously to Twitch, YouTube, Facebook, and custom RTMP servers
- **Professional Recording**: High-quality recording in MP4, AVI, MOV, and FLV formats
- **Scene Management**: Create and switch between different streaming setups
- **Dark Theme UI**: Professional interface matching OBS Studio's design
- **Real-time Processing**: Seamless integration of face processing with streaming workflow

## 🎮 Quick Start

### Primary Launch Methods (OBS-Style Interface)

```bash
# Simplest way - Quick launcher
python launch.py

# Primary OBS-style launcher with options
python run_obs_style.py

# Using main script (OBS is now default)
python main.py run PlayaTewsIdentityMasker
```

### Legacy Traditional Interface

```bash
# Traditional interface (legacy mode)
python run_obs_style.py --traditional

# Or using main script
python main.py run PlayaTewsIdentityMaskerTraditional
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
=======
# PlayaTewsIdentityMasker
 cursor/update-application-and-repository-name-ad7b

Real-time face swapping application for live streaming and video processing.

## Features
- Real-time face detection and swapping
- GPU acceleration support
- Live streaming integration
- Multiple face model support
- Optimized performance

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements_minimal.txt`
3. Run the application: `python main.py run PlayaTewsIdentityMasker`

## Local Development Path
Local path: `C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master`
=======
 main

A real-time face swapping application for live streaming and video processing.

## Features

- Real-time face detection and swapping
- Live streaming support
- GPU acceleration with CUDA
- Multiple face swap models
- Camera and file input support
- Cross-platform compatibility (Windows, macOS, Linux)

## Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (optional, for acceleration)
- PyQt5 for GUI

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PlayaTewsIdentityMasker.git
cd PlayaTewsIdentityMasker
```

2. Install dependencies:
```bash
pip install -r requirements_minimal.txt
```

3. Run the application:
```bash
python main.py run PlayaTewsIdentityMasker
```

## Usage

### Basic Usage

1. Launch the application
2. Select your input source (camera or video file)
3. Choose a face swap model
4. Adjust settings as needed
5. Start the face swapping process

### Command Line Options

```bash
python main.py run PlayaTewsIdentityMasker --userdata-dir /path/to/data --no-cuda
```

- `--userdata-dir`: Specify workspace directory
- `--no-cuda`: Disable CUDA acceleration

## Building

### Desktop Application

To build a standalone executable:

```bash
python build_desktop.py
```

This will create:
- Windows: `PlayaTewsIdentityMasker-Setup.exe`
- Linux: `PlayaTewsIdentityMasker-x86_64.AppImage`
- macOS: `PlayaTewsIdentityMasker.app`

## Local Path

The application is configured for the local path:
`C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.
 main
