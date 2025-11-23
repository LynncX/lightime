#!/bin/bash
# Lightime Pomodoro Timer - Run Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to check if running in recording environment
is_recording_environment() {
    [[ -n "$ASCIINEMA_REC" ]] || [[ -n "$RECORD" ]] || pgrep -f "asciinema" >/dev/null 2>&1
}

# Function to detect terminal type and capabilities
detect_terminal_capabilities() {
    # Check if we have interactive terminal
    if [[ ! -t 0 || ! -t 1 ]]; then
        return 1
    fi

    # Check if we have display for GUI
    if [[ -z "$DISPLAY" ]]; then
        echo "⚠️  Warning: No DISPLAY environment variable detected. GUI may not work."
        return 1
    fi

    return 0
}

# Function to provide fallback mode for recording environments
fallback_mode() {
    echo "🔧 Running in fallback mode (recording/no-GUI environment detected)"
    echo
    echo "Available options:"
    echo "1. Run diagnostics test"
    echo "2. Run integration tests"
    echo "3. Export configuration information"
    echo "4. Try to start anyway (may fail)"
    echo "5. Exit"
    echo
    read -p "Choose an option (1-5): " choice

    case $choice in
        1)
            echo "Running diagnostics..."
            "$SCRIPT_DIR/lightime-env/bin/python" "$SCRIPT_DIR/src/main.py" --diagnostics "/tmp/lightime_diagnostics.json"
            ;;
        2)
            echo "Running integration tests..."
            "$SCRIPT_DIR/lightime-env/bin/python" "$SCRIPT_DIR/src/main.py" --test
            ;;
        3)
            echo "Exporting configuration..."
            "$SCRIPT_DIR/lightime-env/bin/python" "$SCRIPT_DIR/src/main.py" --diagnostics "/tmp/lightime_config.json"
            ;;
        4)
            echo "Attempting to start anyway..."
            "$SCRIPT_DIR/lightime-env/bin/python" "$SCRIPT_DIR/src/main.py" "$@"
            ;;
        5)
            echo "Exiting."
            exit 0
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
}

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/lightime-env" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Check if main.py exists
if [ ! -f "$SCRIPT_DIR/src/main.py" ]; then
    echo "❌ Lightime source code not found. Please ensure installation completed successfully."
    exit 1
fi

# Activate virtual environment
source "$SCRIPT_DIR/lightime-env/bin/activate"

# Change to script directory
cd "$SCRIPT_DIR"

# Set environment variables for better recording compatibility
export PYTHONUNBUFFERED=1
export LIGHTIME_DEBUG=${LIGHTIME_DEBUG:-0}

# Check terminal capabilities
if ! detect_terminal_capabilities; then
    echo "⚠️  Limited terminal capabilities detected"
    if is_recording_environment; then
        fallback_mode "$@"
        exit $?
    fi
fi

# Check if we're in a recording environment
if is_recording_environment; then
    echo "🔴 Recording environment detected (asciinema or similar)"
    echo "💡 Lightime GUI may not work properly in recording mode"
    echo

    read -p "Continue with GUI mode? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        fallback_mode "$@"
        exit $?
    fi
fi

# Check for common issues before starting
echo "🔍 Pre-flight checks..."

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✓ Python version: $python_version"

# Check for required GUI libraries
if python3 -c "import gi; gi.require_version('Gtk', '3.0')" 2>/dev/null; then
    echo "✓ GTK 3.0 available"
else
    echo "⚠️  GTK 3.0 not available - GUI may not work"
    echo "  Try: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
fi

# Check for display server
if pgrep -f "Xwayland\|Xorg" >/dev/null 2>&1 || [[ -n "$WAYLAND_DISPLAY" ]]; then
    echo "✓ Display server detected"
else
    echo "⚠️  No display server detected"
fi

echo "🚀 Starting Lightime Pomodoro Timer..."
echo

# Run the application with proper error handling
if "$SCRIPT_DIR/lightime-env/bin/python" "$SCRIPT_DIR/src/main.py" "$@"; then
    echo "✅ Lightime finished successfully"
else
    exit_code=$?
    echo "❌ Lightime exited with code: $exit_code"

    # Provide helpful troubleshooting info
    echo
    echo "🔧 Troubleshooting:"
    echo "1. Check if all dependencies are installed: pip install -r requirements.txt"
    echo "2. Verify your display server is running (echo \$DISPLAY)"
    echo "3. Try running with --debug flag for more information"
    echo "4. Run diagnostics: ./run.sh --diagnostics debug.json"

    exit $exit_code
fi