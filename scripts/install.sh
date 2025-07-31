#!/bin/bash

# Shepherd - Intelligent Workflow Orchestrator
# Installation Script for Ubuntu/Debian and RedHat/CentOS/Fedora
# By InfraWorks.io

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        OS_ID=$ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
    else
        log_error "Cannot detect operating system"
        exit 1
    fi
    
    log_info "Detected OS: $OS"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "Please do not run this script as root"
        log_info "Run as a regular user with sudo privileges"
        exit 1
    fi
}

# Check sudo privileges
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        log_info "This script requires sudo privileges"
        log_info "You may be prompted for your password"
        sudo -v
    fi
}

# Update package manager
update_packages() {
    log_info "Updating package manager..."
    
    case "$OS_ID" in
        ubuntu|debian)
            sudo apt update
            ;;
        rhel|centos|fedora|rocky|almalinux)
            if command_exists dnf; then
                sudo dnf update -y
            else
                sudo yum update -y
            fi
            ;;
        *)
            log_warning "Unknown OS, skipping package update"
            ;;
    esac
    
    log_success "Package manager updated"
}

# Install Python 3.9+
install_python() {
    log_info "Checking Python installation..."
    
    # Check if Python 3.9+ is already installed
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            log_success "Python $PYTHON_VERSION already installed"
            return
        fi
    fi
    
    log_info "Installing Python 3.9+..."
    
    case "$OS_ID" in
        ubuntu|debian)
            sudo apt install -y python3.9 python3.9-dev python3.9-venv python3-pip
            ;;
        rhel|centos|fedora|rocky|almalinux)
            if command_exists dnf; then
                sudo dnf install -y python39 python39-devel python39-pip
            else
                sudo yum install -y python39 python39-devel python39-pip
            fi
            ;;
        *)
            log_error "Unsupported OS for automatic Python installation"
            log_info "Please install Python 3.9+ manually"
            exit 1
            ;;
    esac
    
    log_success "Python installed"
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    case "$OS_ID" in
        ubuntu|debian)
            sudo apt install -y \
                build-essential \
                libssl-dev \
                libffi-dev \
                git \
                curl \
                wget
            ;;
        rhel|centos|fedora|rocky|almalinux)
            if command_exists dnf; then
                sudo dnf groupinstall -y "Development Tools"
                sudo dnf install -y \
                    openssl-devel \
                    libffi-devel \
                    git \
                    curl \
                    wget
            else
                sudo yum groupinstall -y "Development Tools"
                sudo yum install -y \
                    openssl-devel \
                    libffi-devel \
                    git \
                    curl \
                    wget
            fi
            ;;
        *)
            log_error "Unsupported OS for automatic dependency installation"
            exit 1
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Create and activate virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    # Determine Python command
    if command_exists python3.9; then
        PYTHON_CMD=python3.9
    elif command_exists python3; then
        PYTHON_CMD=python3
    else
        log_error "Python 3 not found"
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    log_success "Virtual environment activated and pip upgraded"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found"
        exit 1
    fi
    
    # Install with verbose output
    pip install -r requirements.txt
    
    log_success "Python dependencies installed"
}

# Install Ollama
install_ollama() {
    log_info "Checking Ollama installation..."
    
    if command_exists ollama; then
        log_success "Ollama already installed"
        return
    fi
    
    log_info "Installing Ollama..."
    
    # Download and install Ollama
    if curl -fsSL https://ollama.com/install.sh | sh; then
        log_success "Ollama installed successfully"
    else
        log_error "Failed to install Ollama"
        log_info "You can install it manually later from https://ollama.com"
        return 1
    fi
    
    # Start Ollama service
    log_info "Starting Ollama service..."
    
    # Check if systemd is available
    if command_exists systemctl; then
        # Try to enable and start Ollama service
        if sudo systemctl enable ollama 2>/dev/null && sudo systemctl start ollama 2>/dev/null; then
            log_success "Ollama service started"
        else
            log_info "Starting Ollama manually..."
            nohup ollama serve > ollama.log 2>&1 &
            sleep 2
            if pgrep -f "ollama serve" > /dev/null; then
                log_success "Ollama started manually"
            else
                log_warning "Failed to start Ollama automatically"
                log_info "You can start it manually with: ollama serve"
            fi
        fi
    else
        log_info "Starting Ollama manually..."
        nohup ollama serve > ollama.log 2>&1 &
        sleep 2
        if pgrep -f "ollama serve" > /dev/null; then
            log_success "Ollama started manually"
        else
            log_warning "Failed to start Ollama"
            log_info "You can start it manually with: ollama serve"
        fi
    fi
}

# Download default model
download_model() {
    log_info "Downloading default model (llama3.1:8b)..."
    
    if ! command_exists ollama; then
        log_warning "Ollama not available, skipping model download"
        return
    fi
    
    # Wait for Ollama to be ready
    for i in {1..10}; do
        if ollama list >/dev/null 2>&1; then
            break
        fi
        log_info "Waiting for Ollama to be ready... ($i/10)"
        sleep 2
    done
    
    # Download model in background
    log_info "This may take several minutes depending on your internet connection..."
    if timeout 300 ollama pull llama3.1:8b; then
        log_success "Model downloaded successfully"
    else
        log_warning "Model download timed out or failed"
        log_info "You can download it later with: ollama pull llama3.1:8b"
    fi
}

# Create .env file
create_env_file() {
    log_info "Creating environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Environment file created from template"
        else
            cat > .env << EOF
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_GENERAL=llama3.1:8b
OLLAMA_MODEL_CODE=codellama:7b
OLLAMA_MODEL_ANALYSIS=mistral:7b

# Safety Configuration
MAX_EXECUTION_TIME=300
SANDBOX_MODE=True
EOF
            log_success "Environment file created"
        fi
    else
        log_info "Environment file already exists"
    fi
}

# Test installation
test_installation() {
    log_info "Testing installation..."
    
    # Test Python imports
    if python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import gradio
    print('✓ Gradio imported successfully')
except ImportError as e:
    print(f'✗ Gradio import failed: {e}')
    sys.exit(1)

try:
    import pydantic
    print('✓ Pydantic imported successfully')
except ImportError as e:
    print(f'✗ Pydantic import failed: {e}')
    sys.exit(1)

print('✓ Core dependencies working')
" 2>/dev/null; then
        log_success "Python dependencies test passed"
    else
        log_error "Python dependencies test failed"
        return 1
    fi
    
    # Test Ollama
    if command_exists ollama && ollama list >/dev/null 2>&1; then
        log_success "Ollama test passed"
    else
        log_warning "Ollama test failed - you may need to start it manually"
    fi
    
    log_success "Installation test completed"
}

# Print usage instructions
print_usage() {
    echo
    log_success "Installation completed successfully!"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo
    echo "2. Run the application:"
    echo "   # Web interface"
    echo "   python main.py --dev"
    echo
    echo "   # Command line"
    echo "   python main.py \"Your request here\""
    echo
    echo "3. If Ollama is not running, start it:"
    echo "   ollama serve"
    echo
    echo "4. Download additional models (optional):"
    echo "   ollama pull codellama:7b"
    echo "   ollama pull mistral:7b"
    echo
    echo -e "${BLUE}Access the web interface at:${NC} http://localhost:7860"
    echo
}

# Main installation function
main() {
    echo "=============================================="
    echo "Shepherd Installation Script"
    echo "By InfraWorks.io"
    echo "=============================================="
    echo
    
    check_root
    check_sudo
    detect_os
    update_packages
    install_python
    install_system_deps
    setup_venv
    install_python_deps
    install_ollama
    download_model
    create_env_file
    test_installation
    print_usage
}

# Handle script interruption
trap 'log_error "Installation interrupted"; exit 1' INT TERM

# Run main function
main "$@"