#!/bin/bash

# Quick fix for Ubuntu desktop dependencies
# Handles the specific webkit package issue

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

echo "🐑 Ubuntu Desktop Dependencies Fix"
echo "================================="
echo

# Check available webkit packages
log_info "Checking available WebKit packages..."
WEBKIT_PACKAGES=$(apt-cache search gir1.2-webkit | grep -E "gir1.2-webkit.*-" | awk '{print $1}')

if [ -n "$WEBKIT_PACKAGES" ]; then
    log_info "Found WebKit packages:"
    echo "$WEBKIT_PACKAGES" | while read pkg; do
        echo "  - $pkg"
    done
    
    # Try to install the first available one
    WEBKIT_PKG=$(echo "$WEBKIT_PACKAGES" | head -n1)
    log_info "Installing $WEBKIT_PKG..."
    
    if sudo apt install -y $WEBKIT_PKG; then
        log_success "Installed $WEBKIT_PKG"
    else
        log_warning "Failed to install $WEBKIT_PKG"
    fi
else
    log_warning "No WebKit packages found"
fi

# Install base GTK packages
log_info "Installing base GTK packages..."
sudo apt install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    libxcb-cursor0

# Check and install Qt6 packages
log_info "Checking available Qt6 packages..."
QT_PACKAGES_AVAILABLE=()

# Check which Qt6 packages are available
for pkg in libqt6gui6 libqt6gui6t64 libqt6widgets6 libqt6widgets6t64 libqt6webenginewidgets6 qt6-qpa-plugins; do
    if apt-cache show "$pkg" >/dev/null 2>&1; then
        QT_PACKAGES_AVAILABLE+=("$pkg")
    fi
done

if [ ${#QT_PACKAGES_AVAILABLE[@]} -gt 0 ]; then
    log_info "Installing available Qt6 packages:"
    for pkg in "${QT_PACKAGES_AVAILABLE[@]}"; do
        echo "  - $pkg"
    done
    
    sudo apt install -y "${QT_PACKAGES_AVAILABLE[@]}"
    log_success "Installed Qt6 packages"
else
    log_warning "No Qt6 packages found"
fi

echo
log_info "Now installing Python webview package..."

# Activate virtual environment if it exists
if [ -d "../venv" ]; then
    source ../venv/bin/activate
    log_info "Activated virtual environment"
elif [ -d "venv" ]; then
    source venv/bin/activate
    log_info "Activated virtual environment"
fi

# Try GTK backend first
if pip install 'pywebview[gtk]' 2>/dev/null; then
    log_success "Installed pywebview with GTK backend"
elif pip install 'pywebview[qt]' 2>/dev/null; then
    log_success "Installed pywebview with Qt backend"
elif pip install pywebview 2>/dev/null; then
    log_success "Installed basic pywebview"
else
    log_error "Failed to install pywebview"
    exit 1
fi

echo
log_info "Testing webview installation..."
if python -c "import webview; print('✓ Webview import successful')"; then
    log_success "Webview is working!"
    echo
    echo "You can now try: ./scripts/start.sh --native-app"
else
    log_warning "Webview test failed, but Chrome app mode will still work"
    echo
    echo "The native app mode will fall back to Chrome app mode automatically"
fi

echo
log_success "Setup completed!"