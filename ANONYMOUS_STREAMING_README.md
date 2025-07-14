# DeepFaceLive Anonymous Streaming Features

This enhanced version of DeepFaceLive includes powerful features for anonymous streaming across multiple platforms with advanced masking and recording capabilities.

## 🎭 Mask Management

### Default Masks
- **None**: No mask applied
- **Blur**: Gaussian blur effect for face protection
- **Pixelate**: Pixelation effect for anonymity
- **Anonymous**: Black bars over eyes and mouth areas
- **Custom**: Upload your own mask images

### Custom Mask Features
- Upload PNG, JPEG, GIF, WebP and other raster formats
- Adjustable intensity (0-100%)
- Automatic resizing to match video dimensions
- Blend modes for seamless integration

### Usage
1. Select mask type from dropdown
2. Adjust intensity slider
3. For custom masks: Click "Upload Mask" and select image file
4. Masks are applied in real-time to the merged frame

## 🌐 Multi-Platform Streaming

### Supported Platforms
- **OBS Virtual Camera**: Direct integration with OBS Studio
- **OBS NDI**: Network Device Interface for OBS
- **Discord**: Direct Discord streaming
- **Zoom**: Virtual camera for Zoom meetings
- **Microsoft Teams**: Teams virtual camera
- **Skype**: Skype virtual camera
- **Custom RTMP**: Stream to any RTMP server
- **Custom UDP**: Stream to any UDP endpoint

### Features
- Stream to multiple platforms simultaneously
- Individual platform enable/disable controls
- Custom RTMP URLs and UDP addresses
- Real-time FPS monitoring
- Automatic connection management

### Setup Instructions
1. Enable desired platforms using checkboxes
2. Configure custom URLs/addresses if needed
3. Start streaming - all enabled platforms receive the masked video feed

## 📹 Enhanced Recording

### Recording Formats
- **MP4**: High-quality H.264 compression
- **AVI**: Uncompressed or compressed options
- **MOV**: Apple QuickTime format
- **MKV**: Open container format
- **WEBM**: Web-optimized format
- **Image Sequence**: Individual frame files

### Recording Features
- **Auto-start recording**: Automatically start recording when streaming begins
- **Duration limits**: Set maximum recording time
- **Quality control**: Adjustable recording quality (1-100)
- **Frame rate control**: Customizable FPS (1-60)
- **Timestamped files**: Automatic filename generation with timestamps

### Usage
1. Select recording format
2. Set recording path directory
3. Configure quality and FPS settings
4. Enable auto-start if desired
5. Set duration limit (0 = unlimited)
6. Click "Is Recording" to start/stop

## 🔧 Installation & Setup

### Prerequisites
- DeepFaceLive installed and working
- DirectX12 compatible graphics card
- Windows 10
- 4GB RAM minimum

### Installation
1. Replace the existing DeepFaceLive files with the enhanced version
2. Run `python main.py run DeepFaceLive` to start
3. New components will appear in the UI

### Directory Structure
```
userdata/
├── masks/           # Custom mask images
├── recordings/      # Recorded video files
├── dfm_models/      # Face swap models
├── animatables/     # Face animation files
└── settings/        # Application settings
```

## 🎯 Use Cases

### Anonymous Streaming
1. Enable mask (Blur, Pixelate, or Anonymous)
2. Set up multi-platform streaming
3. Start recording for backup
4. Stream anonymously across platforms

### Content Creation
1. Use custom masks for creative effects
2. Record in high quality for post-processing
3. Stream to multiple platforms simultaneously
4. Auto-record for backup

### Privacy Protection
1. Enable Anonymous mask for complete privacy
2. Stream to video conferencing platforms
3. Record sessions for compliance
4. Use custom masks for partial privacy

## ⚙️ Configuration

### Mask Settings
- **Intensity**: Controls mask strength (0-100)
- **Custom Path**: Select custom mask image
- **Upload**: Add new mask images to library

### Streaming Settings
- **Platform Selection**: Enable/disable individual platforms
- **Custom URLs**: Configure RTMP/UDP endpoints
- **FPS Monitoring**: Real-time performance tracking

### Recording Settings
- **Format Selection**: Choose output format
- **Quality Control**: Adjust compression settings
- **Auto-start**: Automatic recording with streaming
- **Duration Limits**: Prevent excessive file sizes

## 🚀 Performance Tips

### For High FPS Streaming
- Use GPU acceleration
- Lower mask intensity for better performance
- Disable unnecessary platforms
- Use efficient recording formats (MP4)

### For Quality Recording
- Use high-quality settings
- Choose appropriate format for your needs
- Set reasonable duration limits
- Monitor disk space usage

### For Anonymous Streaming
- Use Anonymous mask for maximum privacy
- Enable auto-recording for backup
- Stream to multiple platforms for redundancy
- Test setup before important sessions

## 🔒 Privacy Features

### Built-in Privacy Protection
- Real-time face masking
- Multiple mask types for different privacy levels
- Anonymous streaming capabilities
- Automatic recording for compliance

### Custom Privacy Controls
- Upload custom masks for specific needs
- Adjustable intensity for partial privacy
- Multiple platform support for redundancy
- Recording backup for important sessions

## 📞 Support

For issues or questions:
1. Check the main DeepFaceLive documentation
2. Review the console output for error messages
3. Verify platform-specific requirements
4. Test with different mask types and settings

## 🔄 Updates

This enhanced version maintains compatibility with the original DeepFaceLive while adding:
- Advanced masking capabilities
- Multi-platform streaming
- Enhanced recording features
- Improved privacy controls

All original DeepFaceLive features remain fully functional. 