# DeepFaceLive OBS-Style UI

This document describes the new OBS Studio-style user interface for DeepFaceLive, which provides enhanced streaming and recording capabilities with a professional streaming software interface.

## Features

### 🎥 Multi-Platform Streaming
- **Twitch Integration**: Stream directly to Twitch with configurable quality settings
- **YouTube Live**: Stream to YouTube with custom stream keys
- **Facebook Live**: Stream to Facebook Live
- **Custom RTMP**: Support for any RTMP server
- **Multi-Platform**: Stream to multiple platforms simultaneously

### 📹 Enhanced Recording
- **Multiple Formats**: MP4, MKV, AVI, MOV support
- **Quality Presets**: 1080p, 720p, 480p, 360p
- **Custom Settings**: Configurable FPS, bitrate, and quality
- **Automatic Naming**: Date/time-based file naming with scene information

### 🎬 Scene Management
- **Multiple Scenes**: Create and switch between different scenes
- **Source Management**: Add, remove, and configure sources within scenes
- **Scene Transitions**: Smooth transitions between scenes
- **Source Properties**: Configure individual source settings

### 🎛️ Professional Controls
- **OBS-Style Layout**: Familiar interface for streamers
- **Real-time Preview**: Live preview of your stream/recording
- **Audio Controls**: Microphone and desktop audio management
- **Performance Settings**: Quality presets and thread management

## Getting Started

### Running the OBS-Style Version

To run DeepFaceLive with the new OBS-style interface:

```bash
python main.py run DeepFaceLiveOBS --userdata-dir /path/to/your/workspace
```

### Traditional Version

The original interface is still available:

```bash
python main.py run DeepFaceLive --userdata-dir /path/to/your/workspace
```

## Interface Overview

### Main Layout

The OBS-style interface is divided into three main panels:

1. **Left Panel**: Scenes and Sources
   - Scene list with add/remove/duplicate functionality
   - Source management for the current scene
   - Source properties and configuration

2. **Center Panel**: Preview and Controls
   - Live preview of your stream/recording
   - Start/Stop streaming and recording buttons
   - Settings access

3. **Right Panel**: Configuration Tabs
   - **Streaming**: Platform configuration and settings
   - **Recording**: Format, quality, and path settings
   - **Audio**: Microphone and monitoring controls
   - **Video**: Resolution and face swap settings

### Streaming Setup

#### 1. Configure Platforms

1. Go to the **Streaming** tab in the right panel
2. Click **Configure [Platform]** for each platform you want to use
3. Enter your stream key or RTMP URL
4. Set quality, FPS, and bitrate settings
5. Enable the platforms you want to use

#### 2. Start Streaming

1. Click **Start Streaming** in the center panel
2. The button will turn green and show "Stop Streaming"
3. Your stream will be sent to all enabled platforms simultaneously

### Recording Setup

#### 1. Configure Recording

1. Go to the **Recording** tab in the right panel
2. Select your preferred format (MP4, MKV, AVI, MOV)
3. Choose quality preset (1080p, 720p, 480p, 360p)
4. Set FPS and bitrate
5. Configure recording path

#### 2. Start Recording

1. Click **Start Recording** in the center panel
2. The button will turn green and show "Stop Recording"
3. Files will be saved with automatic naming: `YYYYMMDD_HHMMSS_scene.ext`

### Scene Management

#### Creating Scenes

1. In the left panel, click the **+** button next to "Scenes"
2. Enter a name for your new scene
3. The scene will be added to your scene list

#### Adding Sources

1. Select a scene from the scene list
2. Click the **+** button next to "Sources"
3. Choose the type of source:
   - **Camera**: Live camera feed
   - **Image**: Static image or logo
   - **Video**: Video file
   - **Audio**: Audio input
   - **Text**: Text overlay
   - **Browser**: Web page content

#### Configuring Sources

1. Select a source from the source list
2. Click **Properties** to configure:
   - Position and size
   - Visibility settings
   - Source-specific options

## Advanced Features

### Multi-Platform Streaming

The enhanced streaming backend supports streaming to multiple platforms simultaneously:

- Each platform can have different quality settings
- Independent stream keys for each platform
- Automatic reconnection on connection loss
- Platform-specific optimization

### Audio Management

- **Microphone Volume**: Adjust microphone input level
- **Desktop Audio**: Include system audio in your stream
- **Audio Monitoring**: Hear your audio output for monitoring
- **Volume Controls**: Individual volume sliders for each audio source

### Performance Optimization

- **Quality Presets**: High Quality, Balanced, Performance
- **Thread Management**: Configure CPU thread usage
- **GPU Acceleration**: Automatic GPU detection and utilization
- **Memory Management**: Optimized memory usage for streaming

### Face Swap Integration

The OBS-style interface fully integrates with DeepFaceLive's face swap capabilities:

- **Real-time Face Swap**: Live face swapping during streaming
- **Quality Settings**: Adjust face swap quality for performance
- **Multiple Faces**: Support for multiple face swaps in a single scene
- **Face Detection**: Automatic face detection and alignment

## Configuration Files

### Settings Location

Settings are stored in your userdata directory:
```
userdata/
├── settings/
│   ├── states.dat          # Backend state
│   └── window_state.dat    # UI layout state
├── recordings/             # Recording output
├── scenes/                 # Scene configurations
└── sources/                # Source configurations
```

### Scene Configuration

Scenes are saved as JSON files with the following structure:
```json
{
  "name": "Scene Name",
  "sources": [
    {
      "name": "Camera Source",
      "type": "camera",
      "enabled": true,
      "visible": true,
      "x": 0,
      "y": 0,
      "width": 1920,
      "height": 1080
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### Streaming Issues
- **Connection Failed**: Check your stream key and internet connection
- **Poor Quality**: Reduce bitrate or quality settings
- **High CPU Usage**: Lower quality presets or reduce thread count

#### Recording Issues
- **No Recording**: Check recording path and permissions
- **Large File Sizes**: Reduce bitrate or quality settings
- **Format Issues**: Try different recording formats

#### Performance Issues
- **Low FPS**: Reduce quality settings or disable unused sources
- **High Memory Usage**: Close unused applications
- **GPU Issues**: Update graphics drivers

### Getting Help

- Check the main DeepFaceLive documentation
- Review the console output for error messages
- Ensure all dependencies are properly installed
- Verify your hardware meets the minimum requirements

## Future Enhancements

Planned features for future releases:

- **Stream Chat Integration**: Display chat overlays
- **Advanced Transitions**: Custom scene transition effects
- **Plugin System**: Third-party plugin support
- **Mobile App**: Remote control via mobile device
- **Cloud Streaming**: Direct cloud platform integration
- **Advanced Audio**: Multi-track audio support
- **Video Effects**: Built-in video effects and filters

## Contributing

The OBS-style UI is built on top of the existing DeepFaceLive framework. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This OBS-style interface follows the same license as the main DeepFaceLive project.