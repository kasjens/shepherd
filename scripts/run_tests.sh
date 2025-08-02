#!/bin/bash

# Test runner script for Shepherd
# Usage: ./scripts/run_tests.sh [options]

set -e

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

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "🧪 Shepherd Test Runner"
    echo "=============================================="
    echo -e "${NC}"
}

# Help function
show_help() {
    cat << EOF
Shepherd Test Runner

Usage: ./scripts/run_tests.sh [OPTIONS]

OPTIONS:
    --backend-only      Run only backend Python tests
    --frontend-only     Run only frontend TypeScript tests
    --unit             Run only unit tests
    --integration      Run only integration tests
    --coverage         Generate coverage report
    --fast             Skip slow tests
    --verbose          Verbose output
    --help             Show this help message

Examples:
    ./scripts/run_tests.sh                    # Run all tests
    ./scripts/run_tests.sh --backend-only     # Python tests only
    ./scripts/run_tests.sh --unit --fast      # Fast unit tests only
    ./scripts/run_tests.sh --coverage         # With coverage report

EOF
}

# Parse command line arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false
UNIT_ONLY=false
INTEGRATION_ONLY=false
COVERAGE=false
FAST=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --unit)
            UNIT_ONLY=true
            shift
            ;;
        --integration)
            INTEGRATION_ONLY=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --fast)
            FAST=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_banner
    
    # Check if virtual environment is activated
    if [[ -z "$VIRTUAL_ENV" ]]; then
        log_warning "Virtual environment not detected"
        log_info "Activating virtual environment..."
        if [[ -f "venv/bin/activate" ]]; then
            source venv/bin/activate
        else
            log_error "Virtual environment not found. Run ./scripts/install.sh first."
            exit 1
        fi
    fi
    
    # Install test dependencies if needed
    log_info "Checking test dependencies..."
    if ! python -c "import pytest" 2>/dev/null; then
        log_info "Installing test dependencies..."
        pip install -r requirements-test.txt
    fi
    
    # Backend tests
    if [[ "$FRONTEND_ONLY" != true ]]; then
        log_info "Running backend tests..."
        
        # Build pytest command
        PYTEST_CMD="pytest"
        
        if [[ "$VERBOSE" == true ]]; then
            PYTEST_CMD="$PYTEST_CMD -v"
        fi
        
        if [[ "$COVERAGE" == true ]]; then
            PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=html --cov-report=term"
        fi
        
        if [[ "$FAST" == true ]]; then
            PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
        fi
        
        if [[ "$UNIT_ONLY" == true ]]; then
            PYTEST_CMD="$PYTEST_CMD -m unit"
        elif [[ "$INTEGRATION_ONLY" == true ]]; then
            PYTEST_CMD="$PYTEST_CMD -m integration"
        fi
        
        # Run backend tests
        if $PYTEST_CMD tests/; then
            log_success "Backend tests passed!"
        else
            log_error "Backend tests failed!"
            exit 1
        fi
    fi
    
    # Frontend tests
    if [[ "$BACKEND_ONLY" != true ]]; then
        log_info "Running frontend tests..."
        
        cd shepherd-gui
        
        # Check if node_modules exists
        if [[ ! -d "node_modules" ]]; then
            log_info "Installing frontend dependencies..."
            npm install
        fi
        
        # Check if test dependencies are installed
        if [[ ! -d "node_modules/@testing-library" ]]; then
            log_info "Installing test dependencies..."
            npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event @types/jest jest jest-environment-jsdom
        fi
        
        # Build jest command
        JEST_CMD="npm test"
        
        if [[ "$COVERAGE" == true ]]; then
            JEST_CMD="npm run test:coverage"
        fi
        
        # Run frontend tests
        if $JEST_CMD -- --watchAll=false; then
            log_success "Frontend tests passed!"
            cd ..
        else
            log_error "Frontend tests failed!"
            cd ..
            exit 1
        fi
    fi
    
    # Generate coverage report if requested
    if [[ "$COVERAGE" == true ]]; then
        log_info "Coverage reports generated:"
        if [[ "$BACKEND_ONLY" != true ]]; then
            log_info "  Backend: htmlcov/index.html"
        fi
        if [[ "$FRONTEND_ONLY" != true ]]; then
            log_info "  Frontend: shepherd-gui/coverage/index.html"
        fi
    fi
    
    log_success "All tests completed successfully! 🎉"
}

# Run main function
main "$@"