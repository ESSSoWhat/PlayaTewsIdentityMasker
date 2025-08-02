# PlayaTews Identity Masker - Background Agent Dockerfile
# Based on Ubuntu 22.04 with Python 3.11 and CUDA support

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Create ubuntu user and set up home directory
RUN useradd -m -s /bin/bash ubuntu && \
    echo "ubuntu ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /home/ubuntu

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Python and development tools
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    build-essential \
    cmake \
    pkg-config \
    
    # GUI dependencies for PyQt5
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libgtk-3-0 \
    libqt5core5a \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5opengl5 \
    libqt5opengl5-dev \
    qt5-default \
    qtbase5-dev \
    qtchooser \
    qt5-qmake \
    
    # OpenCV dependencies
    libopencv-dev \
    libopencv-contrib-dev \
    libopencv-python \
    libopencv-contrib-python \
    
    # Image processing libraries
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libjasper-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    
    # Audio processing (for voice features)
    libasound2-dev \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    
    # System utilities
    git \
    curl \
    wget \
    unzip \
    vim \
    nano \
    htop \
    tree \
    jq \
    yq \
    
    # Network tools
    net-tools \
    iputils-ping \
    telnet \
    
    # Development tools
    gdb \
    valgrind \
    strace \
    ltrace \
    
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install CUDA toolkit (optional, for GPU support)
# Uncomment if GPU support is needed
# RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb && \
#     dpkg -i cuda-keyring_1.0-1_all.deb && \
#     apt-get update && \
#     apt-get install -y cuda-toolkit-12-0 && \
#     rm cuda-keyring_1.0-1_all.deb

# Create Python virtual environment
RUN python3.11 -m venv /home/ubuntu/venv
ENV PATH="/home/ubuntu/venv/bin:$PATH"

# Upgrade pip and install basic Python packages
RUN pip install --upgrade pip setuptools wheel

# Install core Python dependencies
RUN pip install \
    numpy>=1.21.0,<1.28.0 \
    opencv-python>=4.5.0,<4.10.0 \
    opencv-contrib-python>=4.5.0,<4.10.0 \
    PyQt5>=5.15.0,<5.16.0 \
    psutil>=5.8.0,<6.0.0 \
    Pillow>=8.0.0,<11.0.0 \
    pyyaml>=6.0,<7.0 \
    requests>=2.25.0 \
    tqdm>=4.60.0

# Install development and testing tools
RUN pip install \
    pytest>=7.0.0,<8.0.0 \
    pytest-xdist>=3.0.0,<4.0.0 \
    pytest-cov>=4.0.0,<5.0.0 \
    black>=23.0.0,<24.0.0 \
    flake8>=6.0.0,<7.0.0 \
    mypy>=1.0.0,<2.0.0 \
    pre-commit>=3.0.0

# Install optional ML dependencies (commented out to keep image smaller)
# Uncomment if ML features are needed
# RUN pip install \
#     torch>=2.0.0,<2.3.0 \
#     torchvision>=0.15.0,<0.18.0 \
#     onnxruntime-gpu>=1.15.0,<1.18.0 \
#     gputil>=1.4.0,<2.0.0 \
#     pynvml>=11.4.0,<12.0.0

# Set up git configuration
RUN git config --global init.defaultBranch main && \
    git config --global user.name "Background Agent" && \
    git config --global user.email "agent@playatews.com"

# Create common development directories
RUN mkdir -p /home/ubuntu/{workspace,data,models,logs,temp}

# Set proper ownership
RUN chown -R ubuntu:ubuntu /home/ubuntu

# Switch to ubuntu user
USER ubuntu

# Set default shell
SHELL ["/bin/bash", "-c"]

# Create a simple startup script
RUN echo '#!/bin/bash\necho "PlayaTews Identity Masker - Background Agent Environment"\necho "Python version: $(python3.11 --version)"\necho "Working directory: $(pwd)"\necho "Virtual environment: $VIRTUAL_ENV"\nexec "$@"' > /home/ubuntu/start.sh && \
    chmod +x /home/ubuntu/start.sh

# Set the startup script as default command
CMD ["/home/ubuntu/start.sh", "/bin/bash"]
