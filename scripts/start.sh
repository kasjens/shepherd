#!/bin/bash

# Shepherd - Intelligent Workflow Orchestrator
# Start Script with Error Handling
# By InfraWorks.io

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "=============================================="
    echo "🐑 Shepherd - Intelligent Workflow Orchestrator"
    echo "   By InfraWorks.io"
    echo "=============================================="
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    local errors=0
    
    # Check Python
    if ! command_exists python3; then
        log_error "Python 3 is not installed"
        errors=$((errors + 1))
    else
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
            log_error "Python 3.9+ is required (found $PYTHON_VERSION)"
            errors=$((errors + 1))
        else
            log_success "Python $PYTHON_VERSION detected"
        fi
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_error "Virtual environment not found"
        log_info "Run ./install.sh to set up the environment"
        errors=$((errors + 1))
    else
        log_success "Virtual environment found"
    fi
    
    # Check requirements.txt
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found"
        errors=$((errors + 1))
    fi
    
    # Check main application files
    if [ ! -f "main.py" ]; then
        log_error "main.py not found"
        errors=$((errors + 1))
    fi
    
    if [ ! -f "app.py" ]; then
        log_error "app.py not found"
        errors=$((errors + 1))
    fi
    
    if [ $errors -gt 0 ]; then
        log_error "Prerequisites check failed with $errors errors"
        log_info "Please run ./install.sh to install dependencies"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Activate virtual environment
activate_venv() {
    log_step "Activating virtual environment..."
    
    if [ ! -f "venv/bin/activate" ]; then
        log_error "Virtual environment activation script not found"
        log_info "Run ./install.sh to recreate the virtual environment"
        exit 1
    fi
    
    source venv/bin/activate
    log_success "Virtual environment activated"
}

# Check Python dependencies
check_python_deps() {
    log_step "Checking Python dependencies..."
    
    # Test critical imports
    if ! python -c "
import sys
missing_deps = []

try:
    import gradio
except ImportError:
    missing_deps.append('gradio')

try:
    import pydantic
except ImportError:
    missing_deps.append('pydantic')

try:
    import crewai
except ImportError:
    missing_deps.append('crewai')

if missing_deps:
    print(f'Missing dependencies: {missing_deps}')
    sys.exit(1)
" 2>/dev/null; then
        log_success "Python dependencies verified"
    else
        log_error "Missing Python dependencies"
        log_info "Attempting to install missing dependencies..."
        
        if pip install -r requirements.txt; then
            log_success "Dependencies installed successfully"
        else
            log_error "Failed to install dependencies"
            log_info "Please run ./install.sh to reinstall all dependencies"
            exit 1
        fi
    fi
}

# Check Ollama status
check_ollama() {
    log_step "Checking Ollama status..."
    
    if ! command_exists ollama; then
        log_warning "Ollama not found"
        log_info "The application will work with simulated responses"
        log_info "Install Ollama for full LLM functionality: curl -fsSL https://ollama.com/install.sh | sh"
        return
    fi
    
    # Check if Ollama is running
    if ! ollama list >/dev/null 2>&1; then
        log_warning "Ollama is not running"
        log_info "Attempting to start Ollama..."
        
        # Try to start Ollama
        if command_exists systemctl && systemctl is-active --quiet ollama 2>/dev/null; then
            log_success "Ollama service is running"
        elif pgrep -f "ollama serve" > /dev/null; then
            log_success "Ollama is already running"
        else
            log_info "Starting Ollama in background..."
            nohup ollama serve >/dev/null 2>&1 &
            
            # Wait for Ollama to start
            for i in {1..10}; do
                if ollama list >/dev/null 2>&1; then
                    log_success "Ollama started successfully"
                    break
                fi
                if [ $i -eq 10 ]; then
                    log_warning "Failed to start Ollama automatically"
                    log_info "You can start it manually: ollama serve"
                    log_info "The application will work with simulated responses"
                else
                    sleep 1
                fi
            done
        fi
    else
        log_success "Ollama is running"
        
        # Check for available models
        MODELS=$(ollama list 2>/dev/null | grep -v "NAME" | wc -l)
        if [ "$MODELS" -gt 0 ]; then
            log_success "Found $MODELS Ollama model(s)"
        else
            log_warning "No Ollama models found"
            log_info "You can download models with: ollama pull llama3.1:8b"
        fi
    fi
}

# Create environment file if missing
setup_env() {
    log_step "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Environment file created from template"
        else
            log_warning ".env file not found, creating default"
            cat > .env << 'EOF'
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_GENERAL=llama3.1:8b
OLLAMA_MODEL_CODE=codellama:7b
OLLAMA_MODEL_ANALYSIS=mistral:7b

# Safety Configuration
MAX_EXECUTION_TIME=300
SANDBOX_MODE=True
EOF
            log_success "Default environment file created"
        fi
    else
        log_success "Environment file found"
    fi
}

# Parse command line arguments
parse_args() {
    MODE="web"
    REQUEST=""
    INTERACTIVE=false
    PORT=7860
    HOST="0.0.0.0"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cli)
                MODE="cli"
                shift
                ;;
            --desktop)
                MODE="desktop"
                shift
                ;;
            --native-app)
                MODE="native_app"
                shift
                ;;
            --interactive|-i)
                INTERACTIVE=true
                shift
                ;;
            --port|-p)
                PORT="$2"
                shift 2
                ;;
            --host|-h)
                HOST="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                REQUEST="$1"
                shift
                ;;
        esac
    done
}

# Show help
show_help() {
    echo -e "${CYAN}Shepherd Start Script Usage:${NC}"
    echo
    echo "  ./start.sh [OPTIONS] [REQUEST]"
    echo
    echo -e "${YELLOW}Options:${NC}"
    echo "  --cli                Run in command-line mode"
    echo "  --desktop            Run as desktop app (opens in browser without server UI)"
    echo "  --native-app         Run as true native desktop application"
    echo "  --interactive, -i    Run in interactive mode (CLI only)"
    echo "  --port, -p PORT      Specify port for web interface (default: 7860)"
    echo "  --host, -h HOST      Specify host for web interface (default: 0.0.0.0)"
    echo "  --help               Show this help message"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./start.sh                                    # Start web interface"
    echo "  ./start.sh --desktop                         # Start as desktop app (browser-based)"
    echo "  ./start.sh --native-app                      # Start as native desktop application"
    echo "  ./start.sh --port 8080                       # Start web interface on port 8080"
    echo "  ./start.sh --cli \"Create a todo app\"         # Run CLI with request"
    echo "  ./start.sh --cli --interactive                # Run CLI in interactive mode"
    echo
}

# Start web interface
start_web() {
    log_step "Starting web interface..."
    
    log_info "Web interface will be available at: http://localhost:$PORT"
    log_info "Press Ctrl+C to stop the server"
    echo
    
    # Set environment variables for the application
    export GRADIO_SERVER_NAME="$HOST"
    export GRADIO_SERVER_PORT="$PORT"
    
    # Start the application
    if python app.py; then
        log_success "Application started successfully"
    else
        log_error "Failed to start web interface"
        exit 1
    fi
}

# Start desktop app
start_desktop() {
    log_step "Starting desktop application..."
    
    log_info "Opening Shepherd as desktop app..."
    log_info "Press Ctrl+C to stop the application"
    echo
    
    # Set environment variable for desktop mode
    export SHEPHERD_DESKTOP_MODE="true"
    
    # Start the application
    if python app.py --desktop; then
        log_success "Desktop application started successfully"
    else
        log_error "Failed to start desktop application"
        exit 1
    fi
}

# Start native desktop app
start_native_app() {
    log_step "Starting native desktop application..."
    
    log_info "Launching Shepherd as native desktop app..."
    log_info "This provides a true desktop experience (not browser-based)"
    log_info "Press Ctrl+C to stop the application"
    echo
    
    # Check if webview is available
    if ! python -c "import webview" 2>/dev/null; then
        log_warning "Native desktop support (webview) not installed"
        log_info "For the best desktop experience, run: ./desktop/setup_desktop.sh"
        log_info "This will install system dependencies and webview properly"
        echo
        log_info "Attempting automatic webview installation..."
        
        if python desktop/desktop_app.py --install-webview; then
            log_success "Webview installed successfully"
        else
            log_warning "Automatic installation failed"
            log_info "Please run: ./desktop/setup_desktop.sh for proper setup"
        fi
    fi
    
    # Try native desktop first, then fall back to Chrome app mode
    if python desktop/desktop_app.py 2>/dev/null; then
        log_success "Native desktop application started successfully"
    else
        log_warning "Native webview failed, using Chrome app mode"
        if python desktop/app_mode.py; then
            log_success "Chrome app mode started successfully"
        else
            log_error "Failed to start desktop application"
            exit 1
        fi
    fi
}

# Start CLI mode
start_cli() {
    log_step "Starting CLI mode..."
    
    local args=()
    
    if [ "$INTERACTIVE" = true ]; then
        args+=("--interactive")
    fi
    
    if [ -n "$REQUEST" ]; then
        args+=("$REQUEST")
    fi
    
    # Start the application
    if python main.py "${args[@]}"; then
        log_success "CLI execution completed"
    else
        log_error "CLI execution failed"
        exit 1
    fi
}

# Handle script interruption
cleanup() {
    echo
    log_info "Shutting down..."
    
    # Kill background processes if any
    if [ -n "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null || true
    fi
    
    log_success "Cleanup completed"
    exit 0
}

# Main function
main() {
    print_banner
    
    parse_args "$@"
    
    check_prerequisites
    activate_venv
    check_python_deps
    setup_env
    check_ollama
    
    echo
    log_success "All checks passed - starting application..."
    
    # Show logging information
    log_info "Application logs will be written to:"
    log_info "  • logs/shepherd.log (main log with rotation)"  
    log_info "  • logs/shepherd_errors.log (errors only)"
    log_info "  • logs/shepherd_structured.log (JSON format)"
    log_info "  • logs/shepherd_YYYYMMDD.log (daily logs)"
    echo
    log_info "For log analysis, use: ./tools/analyze_logs.py --all"
    echo
    
    case "$MODE" in
        "web")
            start_web
            ;;
        "desktop")
            start_desktop
            ;;
        "native_app")
            start_native_app
            ;;
        "cli")
            start_cli
            ;;
        *)
            log_error "Unknown mode: $MODE"
            exit 1
            ;;
    esac
}

# Set up signal handlers
trap cleanup INT TERM

# Run main function with all arguments
main "$@"