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
    
    # Check for API module (for new GUI)
    if [ ! -d "api" ] && [ "$MODE" = "api" -o "$MODE" = "gui" ]; then
        log_error "API module not found (required for new GUI)"
        log_info "The new GUI requires a FastAPI backend in the 'api/' directory"
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
    if python -c "
import sys
missing_deps = []

try:
    import fastapi
except ImportError:
    missing_deps.append('fastapi')

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
    MODE="gui"  # Default to GUI (launches both API and desktop app)
    REQUEST=""
    INTERACTIVE=false
    PORT=8000  # Changed to 8000 for FastAPI backend
    HOST="0.0.0.0"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cli)
                MODE="cli"
                shift
                ;;
            --api)
                MODE="api"
                shift
                ;;
            --gui)
                MODE="gui"
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
    echo "  --api                Run FastAPI backend server only"
    echo "  --gui                Launch the professional desktop GUI (default)"
    echo "  --interactive, -i    Run in interactive mode (CLI only)"
    echo "  --port, -p PORT      Specify port for API server (default: 8000)"
    echo "  --host, -h HOST      Specify host for API server (default: 0.0.0.0)"
    echo "  --help               Show this help message"
    echo
    echo -e "${YELLOW}New Professional GUI:${NC}"
    echo "  The GUI has been upgraded to a modern TypeScript/React application."
    echo "  To use the new GUI:"
    echo "    1. Start the backend: ./start.sh --api"
    echo "    2. In another terminal: cd shepherd-gui && npm run dev"
    echo "    3. Or build desktop app: cd shepherd-gui && npm run tauri:dev"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./start.sh                                    # Launch desktop GUI (default)"
    echo "  ./start.sh --api                             # Start FastAPI backend only"
    echo "  ./start.sh --gui                             # Launch desktop GUI explicitly"
    echo "  ./start.sh --api --port 8080                 # Start backend on port 8080"
    echo "  ./start.sh --cli \"Create a todo app\"         # Run CLI with request"
    echo "  ./start.sh --cli --interactive                # Run CLI in interactive mode"
    echo
}

# Start API server
start_api() {
    log_step "Starting FastAPI backend server..."
    
    log_info "API server will be available at: http://$HOST:$PORT"
    log_info "WebSocket endpoint: ws://$HOST:$PORT/ws"
    log_info "API documentation: http://$HOST:$PORT/docs"
    log_info "Press Ctrl+C to stop the server"
    echo
    
    # Set environment variables for the application
    export SHEPHERD_API_HOST="$HOST"
    export SHEPHERD_API_PORT="$PORT"
    
    # Start the FastAPI application
    if uvicorn api.main:app --host "$HOST" --port "$PORT" --reload; then
        log_success "API server started successfully"
    else
        log_error "Failed to start API server"
        log_info "Make sure the api/ module and dependencies are properly installed"
        exit 1
    fi
}

# Start GUI application
start_gui() {
    log_step "Starting professional desktop GUI..."
    
    # Check if GUI directory exists
    if [ ! -d "shepherd-gui" ]; then
        log_error "GUI directory 'shepherd-gui' not found"
        log_info "Please ensure the GUI has been properly set up"
        exit 1
    fi
    
    log_info "Launching modern TypeScript/React GUI..."
    log_info "This will start both the backend API and the GUI"
    echo
    
    # Start API server in background
    log_info "Starting backend API server..."
    uvicorn api.main:app --host "$HOST" --port "$PORT" --reload &
    API_PID=$!
    
    # Wait for API to be ready
    sleep 3
    
    # Start the GUI
    log_info "Starting GUI application..."
    cd shepherd-gui
    
    # Check if dependencies are installed
    if [ ! -d "node_modules" ]; then
        log_info "Installing GUI dependencies..."
        npm install
    fi
    
    # Source Rust environment if available
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
        log_info "Rust environment loaded"
    fi
    
    # Start Next.js dev server in background first
    log_info "Starting Next.js development server..."
    npm run dev &
    NEXTJS_PID=$!
    
    # Wait for Next.js to be ready
    log_info "Waiting for Next.js server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            log_success "Next.js server is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Next.js server failed to start"
            kill $API_PID $NEXTJS_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
    done
    
    # Now start Tauri desktop app
    log_info "Starting Tauri desktop application..."
    if npm run tauri:dev; then
        log_success "Desktop application started successfully"
    else
        log_warning "Tauri desktop app failed, keeping web version running..."
        log_success "Web GUI is available at http://localhost:3000"
        log_info "Backend API is running at http://localhost:8000"
        
        # Keep processes running
        wait $NEXTJS_PID
    fi
    
    # Clean up background processes
    kill $API_PID $NEXTJS_PID 2>/dev/null || true
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

# Kill processes using specific ports
kill_port_processes() {
    local port=$1
    local description=$2
    
    log_info "Checking for processes using port $port..."
    
    # Find processes using the port
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        log_warning "Found $description processes using port $port"
        for pid in $pids; do
            local process_name=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
            log_info "Terminating process $pid ($process_name)..."
            kill $pid 2>/dev/null || true
        done
        
        # Wait a moment for processes to terminate
        sleep 2
        
        # Force kill any remaining processes
        local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            log_warning "Force killing remaining processes on port $port"
            for pid in $remaining_pids; do
                kill -9 $pid 2>/dev/null || true
            done
            sleep 1
        fi
        
        log_success "Port $port cleared"
    else
        log_info "Port $port is available"
    fi
}

# Cleanup previous instances
cleanup_previous_instances() {
    log_step "Cleaning up previous instances..."
    
    # Kill processes on common ports
    kill_port_processes 3000 "Next.js development server"
    kill_port_processes 8000 "FastAPI backend server"
    
    # Kill any remaining Shepherd-related processes
    log_info "Checking for other Shepherd processes..."
    
    # Kill any running uvicorn processes
    pkill -f "uvicorn.*api.main:app" 2>/dev/null || true
    
    # Kill any npm dev processes in shepherd-gui directory
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "npm run tauri:dev" 2>/dev/null || true
    
    # Kill any Node.js processes running Next.js
    pkill -f "next-server" 2>/dev/null || true
    pkill -f ".next" 2>/dev/null || true
    
    # Kill any Tauri dev processes
    pkill -f "tauri dev" 2>/dev/null || true
    pkill -f "cargo run.*shepherd-gui" 2>/dev/null || true
    
    sleep 2
    log_success "Previous instances cleaned up"
}

# Handle script interruption
cleanup() {
    echo
    log_info "Shutting down..."
    
    # Kill background processes if any
    if [ -n "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null || true
    fi
    
    if [ -n "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    
    if [ -n "$NEXTJS_PID" ]; then
        kill $NEXTJS_PID 2>/dev/null || true
    fi
    
    # Clean up any remaining processes
    kill_port_processes 3000 "Next.js"
    kill_port_processes 8000 "FastAPI"
    
    log_success "Cleanup completed"
    exit 0
}

# Main function
main() {
    print_banner
    
    parse_args "$@"
    
    cleanup_previous_instances
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
        "api")
            start_api
            ;;
        "gui")
            start_gui
            ;;
        "cli")
            start_cli
            ;;
        *)
            log_error "Unknown mode: $MODE"
            show_help
            exit 1
            ;;
    esac
}

# Set up signal handlers
trap cleanup INT TERM

# Run main function with all arguments
main "$@"