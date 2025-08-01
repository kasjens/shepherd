# Migration Guide: Old GUI to New Professional GUI

## Overview
The Shepherd project has migrated from a Gradio-based web interface to a modern, professional TypeScript/React GUI with desktop support.

## What Changed

### Old System (Removed)
- **Gradio-based web interface** (`app.py`)
- **Desktop wrapper scripts** (`desktop/` directory)
- **Start modes**: `--web`, `--desktop`, `--native-app`

### New System (Current)
- **FastAPI backend** (API server)
- **Next.js + TypeScript GUI** (`shepherd-gui/` directory)
- **Tauri desktop integration** (cross-platform native apps)
- **Start modes**: `--api`, `--gui`, `--cli`

## Quick Start

### For API Development
```bash
./start.sh --api
# API available at: http://localhost:8000
# Documentation: http://localhost:8000/docs
```

### For GUI Usage
```bash
# Option 1: Desktop app (recommended)
./start.sh --gui

# Option 2: Manual setup
./start.sh --api &                    # Start backend
cd shepherd-gui && npm run tauri:dev  # Start desktop GUI

# Option 3: Web version
./start.sh --api &                    # Start backend  
cd shepherd-gui && npm run dev        # Start web GUI at localhost:3000
```

### For CLI Usage (unchanged)
```bash
./start.sh --cli "Your request here"
./start.sh --cli --interactive
```

## New GUI Features

- **Modern Interface**: Terminal-inspired design with professional aesthetics
- **Real-time Communication**: WebSocket-based live updates
- **Cross-platform Desktop**: Native apps for Windows, macOS, and Linux
- **Responsive Design**: Works on multiple screen sizes
- **Theme Support**: Multiple color themes (dark, light, blue)
- **Panel Resizing**: Adjustable layout with drag handles
- **TypeScript**: Full type safety and better development experience

## Development Setup

### Prerequisites
- Node.js 18+ and npm
- Rust (for Tauri desktop builds)
- Python 3.9+ with FastAPI dependencies

### First-time Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install GUI dependencies
cd shepherd-gui
npm install
cd ..
```

### Development Workflow
```bash
# Terminal 1: Start API backend
./start.sh --api

# Terminal 2: Start GUI development server
cd shepherd-gui
npm run dev        # Web version
# OR
npm run tauri:dev  # Desktop version
```

## Configuration

### Environment Variables
- `SHEPHERD_API_HOST`: API server host (default: 0.0.0.0)
- `SHEPHERD_API_PORT`: API server port (default: 8000)

### GUI Configuration
GUI settings are stored in `shepherd-gui/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Common Issues

1. **"API module not found"**
   - Ensure you have the FastAPI backend set up in the `api/` directory
   - Run `pip install -r requirements.txt` to install FastAPI dependencies

2. **GUI won't start**
   - Check Node.js version: `node --version` (requires 18+)
   - Run `cd shepherd-gui && npm install` to install dependencies
   - For Tauri: ensure Rust is installed

3. **Connection errors**
   - Verify API server is running on the correct port
   - Check firewall settings for local connections

### Legacy Support
The old Gradio interface has been completely removed. If you need the old interface for any reason, it's available in the git history or the backup files in `shepherd-gui/old-gui-backup/`.

## Migration Benefits

- **Better Performance**: Faster loading and response times
- **Modern UX**: Professional interface with better usability
- **Desktop Integration**: True native desktop experience
- **Maintainability**: TypeScript provides better code quality
- **Extensibility**: Modern React ecosystem for future features
- **Cross-platform**: Single codebase for web and desktop