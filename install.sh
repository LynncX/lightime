#!/bin/bash

# Lightime Pomodoro Timer - Installation Script
# This script installs all dependencies and sets up the application

set -e

echo "=== Lightime Pomodoro Timer Installation ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for user-level installation"
   exit 1
fi

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        print_error "Cannot detect Linux distribution"
        exit 1
    fi

    print_status "Detected distribution: $DISTRO $VERSION"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."

    case $DISTRO in
        ubuntu|debian)
            print_status "Installing dependencies for Ubuntu/Debian..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-dev \
                libgirepository1.0-dev gcc libcairo2-dev pkg-config \
                python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
                libnotify4 libnotify-dev \
                libappindicator3-dev \
                xdotool \
                libdbus-1-dev libdbus-glib-1-dev
            ;;
        fedora)
            print_status "Installing dependencies for Fedora..."
            sudo dnf install -y python3 python3-pip python3-devel \
                gobject-introspection-devel gcc cairo-devel pkg-config \
                python3-gobject python3-gobject-devel \
                libnotify-devel \
                libappindicator-gtk3 \
                xdotool \
                dbus-devel dbus-glib-devel
            ;;
        arch)
            print_status "Installing dependencies for Arch Linux..."
            sudo pacman -S --needed python python-pip python-gobject \
                cairo pkgconf \
                libnotify libappindicator-gtk3 \
                xdotool \
                dbus
            ;;
        *)
            print_error "Unsupported distribution: $DISTRO"
            print_error "Please install dependencies manually according to the README"
            exit 1
            ;;
    esac

    print_success "System dependencies installed"
}

# Setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."

    # Check if uv is available
    if command -v uv &> /dev/null; then
        print_status "Using uv for fast Python environment setup..."
        uv venv lightime-env
        source lightime-env/bin/activate
        uv pip install -r requirements.txt
    elif command -v python3-venv &> /dev/null; then
        print_status "Using python3-venv..."
        python3 -m venv lightime-env
        source lightime-env/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        print_error "Neither uv nor python3-venv is available"
        exit 1
    fi

    print_success "Python environment setup completed"
}

# Test installation
test_installation() {
    print_status "Testing installation..."

    source lightime-env/bin/activate

    # Test basic functionality
    if python3 test_models_only.py > /dev/null 2>&1; then
        print_success "Core functionality tests passed"
    else
        print_error "Core functionality tests failed"
        exit 1
    fi

    # Test GUI imports
    if python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from gi.repository import Gtk
    print('GTK3 import successful')
except ImportError as e:
    print(f'GTK3 import failed: {e}')
    sys.exit(1)
" > /dev/null 2>&1; then
        print_success "GUI dependencies test passed"
    else
        print_warning "GUI dependencies test failed - GUI may not work"
        print_warning "Please ensure GTK3 and PyGObject are properly installed"
    fi
}

# Create desktop entry
create_desktop_entry() {
    print_status "Creating desktop entry..."

    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"

    cat > "$DESKTOP_DIR/lightime.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Lightime
Comment=Lightweight Pomodoro Timer
Exec=$(pwd)/lightime-env/bin/python $(pwd)/src/main.py
Icon=alarm-clock
Terminal=false
Categories=Office;Utility;Clock;
StartupNotify=true
Keywords=pomodoro;timer;productivity;
EOF

    print_success "Desktop entry created"
}

# Create run script
create_run_script() {
    print_status "Creating run script..."

    cat > run.sh << 'EOF'
#!/bin/bash
# Lightime Pomodoro Timer - Run Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
if [ -d "$SCRIPT_DIR/lightime-env" ]; then
    source "$SCRIPT_DIR/lightime-env/bin/activate"
else
    echo "Error: Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Run the application
cd "$SCRIPT_DIR"
python3 src/main.py "$@"
EOF

    chmod +x run.sh
    print_success "Run script created"
}

# Main installation flow
main() {
    detect_distro

    print_status "Starting Lightime installation..."
    echo

    install_system_deps
    echo

    setup_python_env
    echo

    test_installation
    echo

    create_desktop_entry
    echo

    create_run_script
    echo

    print_success "Lightime installation completed successfully!"
    echo
    print_status "To run the application:"
    echo "  • Using run script: ./run.sh"
    echo "  • Directly: ./lightime-env/bin/python src/main.py"
    echo "  • From desktop menu (Lightime)"
    echo
    print_status "For configuration: ~/.config/lightime/"
    print_status "For logs: ~/.local/share/lightime/"
    echo
    print_status "Thank you for installing Lightime! 🍅"
}

# Handle script arguments
case "${1:-}" in
    --system-deps-only)
        detect_distro
        install_system_deps
        ;;
    --python-only)
        setup_python_env
        ;;
    --test-only)
        test_installation
        ;;
    *)
        main
        ;;
esac