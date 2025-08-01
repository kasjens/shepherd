#!/bin/bash

# Setup script for native desktop support on Linux
# This installs the required system dependencies for pywebview

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
        OS=$ID
    else
        log_error "Cannot detect operating system"
        exit 1
    fi
    
    log_info "Detected OS: $OS"
}

# Install system dependencies for webview
install_system_deps() {
    log_info "Installing system dependencies for native desktop support..."
    
    case "$OS" in
        ubuntu|debian)
            log_info "Installing GTK and Qt dependencies for Ubuntu/Debian..."
            sudo apt update
            
            # Base GTK packages
            sudo apt install -y \
                python3-gi \
                python3-gi-cairo \
                gir1.2-gtk-3.0 \
                libxcb-cursor0
            
            # Try to install WebKit (different package names in different Ubuntu versions)
            log_info "Installing WebKit packages..."
            if sudo apt install -y gir1.2-webkit2-4.1 2>/dev/null; then
                log_success "Installed WebKit 4.1"
            elif sudo apt install -y gir1.2-webkit2-4.0 2>/dev/null; then
                log_success "Installed WebKit 4.0"
            elif sudo apt install -y gir1.2-webkit-3.0 2>/dev/null; then
                log_success "Installed WebKit 3.0"
            else
                log_warning "Could not install WebKit - GTK backend may not work"
            fi
            
            # Try to install Qt6 packages (with fallback package names)
            log_info "Installing Qt6 packages..."
            if sudo apt install -y \
                libqt6gui6 \
                libqt6widgets6 \
                libqt6webenginewidgets6 \
                qt6-qpa-plugins 2>/dev/null; then
                log_success "Installed Qt6 packages"
            elif sudo apt install -y \
                libqt6gui6t64 \
                libqt6widgets6t64 \
                libqt6webenginewidgets6 \
                qt6-qpa-plugins 2>/dev/null; then
                log_success "Installed Qt6 packages (t64 variant)"
            else
                log_warning "Could not install all Qt6 packages - Qt backend may not work fully"
                # Install what we can
                sudo apt install -y qt6-qpa-plugins || true
            fi
            ;;
        fedora|centos|rhel)
            log_info "Installing GTK and Qt dependencies for Fedora/RHEL..."
            sudo dnf install -y \
                python3-gobject \
                python3-gobject-devel \
                gtk3-devel \
                webkit2gtk4.0-devel \
                qt6-qtbase-gui \
                qt6-qtwebengine
            ;;
        arch|manjaro)
            log_info "Installing GTK and Qt dependencies for Arch Linux..."
            sudo pacman -S --noconfirm \
                python-gobject \
                gtk3 \
                webkit2gtk \
                qt6-base \
                qt6-webengine
            ;;
        *)
            log_warning "Unsupported OS: $OS"
            log_info "Please install GTK3 and Qt6 development packages manually"
            ;;
    esac
}

# Install Python webview package
install_webview() {
    log_info "Installing Python webview package..."
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Try GTK backend first (more reliable on Linux)
    if pip install 'pywebview[gtk]'; then
        log_success "Installed pywebview with GTK backend"
        return 0
    fi
    
    # Fallback to Qt backend
    if pip install 'pywebview[qt]'; then
        log_success "Installed pywebview with Qt backend"
        return 0
    fi
    
    # Last resort - basic webview
    if pip install pywebview; then
        log_warning "Installed basic pywebview (limited functionality)"
        return 0
    fi
    
    log_error "Failed to install pywebview"
    return 1
}

# Test the installation
test_webview() {
    log_info "Testing webview installation..."
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    if python -c "import webview; print('✓ Webview import successful')"; then
        log_success "Webview is working correctly"
        return 0
    else
        log_error "Webview test failed"
        return 1
    fi
}

main() {
    echo "🐑 Shepherd Desktop Setup"
    echo "========================="
    echo
    
    detect_os
    
    log_info "This will install system dependencies for native desktop support"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Setup cancelled"
        exit 0
    fi
    
    install_system_deps
    install_webview
    test_webview
    
    echo
    log_success "Desktop setup completed!"
    echo
    echo "You can now run:"
    echo "  ./start.sh --native-app"
    echo
}

main "$@"