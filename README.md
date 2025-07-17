# PlayaTewsIdentityMasker

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
