# New Layout UI Implementation

## Overview

This document describes the new layout UI implementation for the PlayaTews Identity Masker application, which follows the exact three-panel design specified in the ASCII art layout.

## Layout Structure

The new layout implements a three-panel design with the following structure:

```
┌─────────────────────────────────────────────────────────────┐
│                    LEFT PANEL                               │
│  • DFM Quick Access                                        │
│  • Input Sources (File, Camera)                            │
│  • Voice Changer                                           │
├─────────────────────────────────────────────────────────────┤
│                    CENTER PANEL                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              PROCESSING COMPONENTS                      │ │
│  │ [Detection] [Alignment] [Face Swap] [Enhancement]      │ │
│  │                                                         │ │
│  │🎬 ENHANCED OUTPUT PREVIEW - LIVE FACE SWAP             │ │
│  │                                                         │ │
│  │              [LARGE PREVIEW AREA]                       │ │
│  │                                                         │ │
│  │        [Fullscreen] [Maximize] [Settings]               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              VIEWERS & CONTROLS                         │ │
│  │ [Camera] [Face Align] [Face Swap] [Merged] | [Controls]│ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    RIGHT PANEL                              │
│  • Settings                                                │
│  • Additional Controls                                     │
└─────────────────────────────────────────────────────────────┘
```

## Panel Details

### Left Panel
- **DFM Quick Access**: List of available DFM models with load/refresh controls
- **Input Sources**: Camera and file input configuration
  - Camera settings (device selection, resolution)
  - File settings (browse for video files)
- **Voice Changer**: Voice modification controls
  - Enable/disable voice changer
  - Effect selection (Pitch Shift, Echo, Reverb, etc.)
  - Pitch adjustment slider

### Center Panel
- **Processing Components**: Toggle buttons for each processing stage
  - Detection
  - Alignment
  - Face Swap
  - Enhancement
- **Enhanced Output Preview**: Large preview area with title
  - Live face swap preview
  - Fullscreen, maximize, and settings controls
- **Viewers & Controls**: Viewer selection buttons
  - Camera, Face Align, Face Swap, Merged views
  - Controls button for additional options

### Right Panel
- **Settings**: Application configuration
  - Quality settings (Low, Medium, High, Ultra)
  - FPS settings (15, 24, 30, 60)
  - Memory allocation (2GB, 4GB, 8GB, 16GB)
  - Advanced settings toggle
- **Additional Controls**: Recording and streaming
  - Start/Stop Recording button
  - Start/Stop Streaming button
  - Performance monitoring (FPS, Memory, CPU)

## Features

### Modern Design
- Dark theme with professional styling
- Responsive layout with resizable panels
- Consistent button and control styling
- Hover effects and visual feedback

### Functionality
- Real-time performance monitoring
- Fullscreen support (F11 key)
- Keyboard shortcuts
- Status bar with operation feedback
- Menu bar with File, View, and Help menus

### Integration
- Compatible with existing backend components
- Supports face swap components
- Voice changer integration
- Stream output backend integration

## Usage

### Running the New Layout

1. **Direct Usage**: Import and use the `QNewLayoutUI` class directly
2. **Test Script**: Use the provided `test_new_layout.py` script
3. **Integration**: Replace existing UI components with the new layout

### Example Integration

```python
from apps.PlayaTewsIdentityMasker.ui.QNewLayoutUI import QNewLayoutUI

# Create the new layout UI
ui = QNewLayoutUI(
    stream_output_backend=stream_output,
    userdata_path=userdata_path,
    face_swap_components=face_swap_components,
    viewers_components=viewers_components,
    voice_changer_backend=voice_changer_backend
)

# Show the UI
ui.show()
```

## File Structure

```
apps/PlayaTewsIdentityMasker/ui/
├── QNewLayoutUI.py          # Main new layout implementation
└── ...

test_new_layout.py           # Test script for the new layout
NEW_LAYOUT_README.md         # This documentation file
```

## Technical Details

### Dependencies
- PyQt5 for the UI framework
- Standard Python libraries (pathlib, typing)
- Backend components from the existing application

### Architecture
- **QMainWindow**: Main application window
- **QSplitter**: Resizable three-panel layout
- **QGroupBox**: Organized sections within panels
- **QPushButton**: Interactive controls
- **QComboBox**: Dropdown selections
- **QListWidget**: Model and source lists
- **QLabel**: Display areas and indicators

### Styling
- CSS-like stylesheet for consistent appearance
- Dark color scheme (#2b2b2b background)
- Professional button and control styling
- Hover effects and state indicators

## Future Enhancements

### Planned Features
- Drag and drop support for files
- Customizable panel layouts
- Theme selection (light/dark modes)
- Advanced performance monitoring
- Plugin system for additional controls

### Integration Opportunities
- OBS Studio integration
- Streamlabs integration
- Custom voice changer plugins
- Advanced face swap models

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure proper Python path setup
2. **Missing Dependencies**: Install PyQt5 and required packages
3. **Backend Integration**: Verify backend component compatibility
4. **Performance Issues**: Check system requirements and memory allocation

### Support
- Check existing documentation for backend integration
- Review error logs for specific issues
- Test with minimal configuration first
- Verify all dependencies are properly installed

## Conclusion

The new layout UI provides a modern, professional interface for the PlayaTews Identity Masker application while maintaining compatibility with existing backend components. The three-panel design offers excellent organization and usability for face swap operations, voice changing, and streaming functionality. 