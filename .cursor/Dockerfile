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

# Background agent specific environment variables
ENV AGENT_ENV=production
ENV LOG_LEVEL=INFO
ENV MAX_WORKERS=4
ENV WORKER_TIMEOUT=300

# Create ubuntu user and set up home directory
RUN useradd -m -s /bin/bash ubuntu

# Set working directory
WORKDIR /home/ubuntu

# Install only essential system dependencies for background agents
RUN apt-get update && apt-get install -y \
    # Python and minimal development tools
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    build-essential \
    pkg-config \
    
    # Minimal GUI dependencies (only if PyQt5 is actually needed)
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libqt5core5a \
    libqt5gui5 \
    libqt5widgets5 \
    
    # Core OpenCV dependencies only
    libopencv-dev \
    libopencv-contrib-dev \
    
    # Essential image processing libraries
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    
    # Minimal audio processing (only if voice features are used)
    libasound2-dev \
    portaudio19-dev \
    
    # Essential system utilities only
    git \
    curl \
    wget \
    unzip \
    nano \
    jq \
    
    # Essential network tools
    net-tools \
    iputils-ping \
    
    # Clean up in the same layer
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

# Install only core Python dependencies needed for background agents
RUN pip install \
    numpy>=1.21.0,<1.28.0 \
    opencv-python>=4.5.0,<4.10.0 \
    opencv-contrib-python>=4.5.0,<4.10.0 \
    PyQt5>=5.15.0,<5.16.0 \
    psutil>=5.8.0,<6.0.0 \
    Pillow>=8.0.0,<11.0.0 \
    pyyaml>=6.0,<7.0 \
    requests>=2.25.0 \
    tqdm>=4.60.0 \
    # Background agent specific packages
    python-dotenv>=0.19.0 \
    structlog>=23.0.0 \
    schedule>=1.2.0 \
    watchdog>=3.0.0

# Install only essential development tools (comment out if not needed)
# RUN pip install \
#     pytest>=7.0.0,<8.0.0 \
#     black>=23.0.0,<24.0.0 \
#     flake8>=6.0.0,<7.0.0

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

# Create only essential directories
RUN mkdir -p /home/ubuntu/{workspace,data,models,logs,temp,config}

# Set proper ownership
RUN chown -R ubuntu:ubuntu /home/ubuntu

# Switch to ubuntu user
USER ubuntu

# Set default shell
SHELL ["/bin/bash", "-c"]

# Create a simple startup script
RUN echo '#!/bin/bash\necho "PlayaTews Identity Masker - Background Agent Environment"\necho "Python version: $(python3.11 --version)"\necho "Working directory: $(pwd)"\necho "Virtual environment: $VIRTUAL_ENV"\nexec "$@"' > /home/ubuntu/start.sh && \
    chmod +x /home/ubuntu/start.sh

# Add health check for background agent
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3.11 -c "import sys; sys.exit(0)"

# Set the startup script as default command
CMD ["/home/ubuntu/start.sh", "/bin/bash"]
