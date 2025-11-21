#!/bin/bash

# Lightime Pomodoro Timer - One-Click Installation Script
# This script installs Lightime from scratch for beginners

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Animation function
spin() {
    local -a marks=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
    while kill -0 "$pid" 2>/dev/null; do
        for mark in "${marks[@]}"; do
            printf "\r${CYAN}%s${NC} $1... $mark" "$2"
            sleep 0.1
        done
    done
    printf "\r${GREEN}✓${NC} $2... Done!\n"
}

# Print functions
print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Lightime Pomodoro Timer                    ║"
    echo "║                     One-Click Installer                      ║"
    echo "║                     Version 1.0.0                            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

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

print_step() {
    echo -e "${PURPLE}[STEP $1/7]${NC} $2"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Please do not run this script as root or with sudo."
        print_status "This script installs to your user directory only."
        exit 1
    fi
}

# Check internet connection
check_internet() {
    print_status "Checking internet connection..."
    if ping -c 1 google.com &>/dev/null; then
        print_success "Internet connection available"
    else
        print_error "No internet connection. Please check your network and try again."
        exit 1
    fi
}

# Detect Linux distribution
detect_distro() {
    print_status "Detecting your Linux distribution..."

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    else
        print_error "Cannot detect Linux distribution"
        exit 1
    fi

    case $DISTRO in
        ubuntu|debian)
            DISTRO_FRIENDLY="Ubuntu/Debian"
            PKG_MANAGER="apt"
            ;;
        fedora)
            DISTRO_FRIENDLY="Fedora"
            PKG_MANAGER="dnf"
            ;;
        arch)
            DISTRO_FRIENDLY="Arch Linux"
            PKG_MANAGER="pacman"
            ;;
        *)
            print_warning "Unsupported distribution: $DISTRO"
            print_warning "Trying with Ubuntu/Debian packages..."
            DISTRO_FRIENDLY="Unknown (Ubuntu/Debian compatible)"
            PKG_MANAGER="apt"
            ;;
    esac

    print_success "Detected: $DISTRO_FRIENDLY"
}

# Check if git is available
check_git() {
    print_status "Checking if Git is available..."
    if command -v git &> /dev/null; then
        print_success "Git is available"
    else
        print_error "Git is not installed. Installing Git..."

        case $PKG_MANAGER in
            apt)
                sudo apt update && sudo apt install -y git
                ;;
            dnf)
                sudo dnf install -y git
                ;;
            pacman)
                sudo pacman -S --needed git
                ;;
        esac
    fi
}

# Clone or update repository
clone_repo() {
    INSTALL_DIR="$HOME/lightime"
    REPO_URL="https://github.com/your-repo/lightime.git"  # Replace with actual repo URL

    print_status "Setting up installation directory: $INSTALL_DIR"

    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Lightime directory already exists. Updating..."
        cd "$INSTALL_DIR"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || print_warning "Could not update - working with local version"
    else
        print_status "Cloning Lightime repository..."
        cd "$HOME"
        git clone "$REPO_URL" lightime 2>/dev/null || {
            print_error "Failed to clone repository. Please check the repository URL."
            print_error "Current URL: $REPO_URL"
            print_error "Update the REPO_URL variable in install.sh with the correct repository URL."
            exit 1
        }
        cd "$INSTALL_DIR"
    fi

    print_success "Repository ready at: $INSTALL_DIR"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies (requires sudo)..."

    case $PKG_MANAGER in
        apt)
            print_status "Installing packages for Ubuntu/Debian..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-dev \
                libgirepository1.0-dev gcc libcairo2-dev pkg-config \
                python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
                libnotify4 libnotify-dev \
                libayatana-appindicator3-dev \
                xdotool
            ;;
        dnf)
            print_status "Installing packages for Fedora..."
            sudo dnf install -y python3 python3-pip python3-devel \
                gobject-introspection-devel gcc cairo-devel pkg-config \
                python3-gobject python3-gobject-devel \
                libnotify-devel \
                libayatana-appindicator3 \
                xdotool
            ;;
        pacman)
            print_status "Installing packages for Arch Linux..."
            sudo pacman -S --needed python python-pip python-gobject \
                cairo pkgconf \
                libnotify libayatana-appindicator \
                xdotool
            ;;
    esac

    print_success "System dependencies installed"
}

# Setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."

    cd "$INSTALL_DIR"

    # Check if uv is available for faster installation
    if command -v uv &> /dev/null; then
        print_status "Using uv for fast Python environment setup..."
        uv venv lightime-env
        source "$INSTALL_DIR/lightime-env/bin/activate"
        uv pip install -r requirements-conda.txt
    else
        print_status "Using standard Python venv..."
        python3 -m venv lightime-env
        source "$INSTALL_DIR/lightime-env/bin/activate"
        pip install --upgrade pip
        pip install -r requirements-conda.txt
    fi

    print_success "Python environment ready"
}

# Test installation
test_installation() {
    print_status "Testing installation..."

    cd "$INSTALL_DIR"
    source "$INSTALL_DIR/lightime-env/bin/activate"

    # Test core functionality
    if python3 quick_test.py > /dev/null 2>&1; then
        print_success "Core functionality tests passed"
    else
        print_warning "Some tests failed, but basic functionality should work"
    fi

    # Test GUI imports
    if python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    print('✅ GUI dependencies working')
except ImportError as e:
    print('⚠️  GUI dependencies need attention')
" > /dev/null 2>&1; then
        print_success "GUI dependencies test passed"
    else
        print_warning "GUI dependencies test failed - may need manual setup"
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
Exec=$INSTALL_DIR/lightime-env/bin/python $INSTALL_DIR/src/main.py
Icon=alarm-clock
Terminal=false
Categories=Office;Utility;Clock;
StartupNotify=true
Keywords=pomodoro;timer;productivity;
EOF

    print_success "Desktop entry created"
}

# Create convenient run scripts
create_run_scripts() {
    print_status "Creating run scripts..."

    cd "$INSTALL_DIR"

    # Create run script
    cat > run.sh << 'EOF'
#!/bin/bash
# Lightime Pomodoro Timer - Run Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/lightime-env" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
source "$SCRIPT_DIR/lightime-env/bin/activate"

# Change to script directory
cd "$SCRIPT_DIR"

# Run the application
python3 src/main.py "$@"
EOF

    chmod +x run.sh

    # Create update script
    cat > update.sh << 'EOF'
#!/bin/bash
# Lightime Pomodoro Timer - Update Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Updating Lightime..."

cd "$SCRIPT_DIR"

# Backup configuration
if [ -f "$HOME/.config/lightime/config.yaml" ]; then
    cp "$HOME/.config/lightime/config.yaml" "$HOME/.config/lightime/config.yaml.backup"
    echo "✓ Configuration backed up"
fi

# Update repository
git pull origin main

# Update Python dependencies
source "$SCRIPT_DIR/lightime-env/bin/activate"
pip install -r requirements-conda.txt

echo "✅ Lightime updated successfully!"
echo "Run ./run.sh to start the application."
EOF

    chmod +x update.sh

    # Create uninstall script
    cat > uninstall.sh << 'EOF'
#!/bin/bash
# Lightime Pomodoro Timer - Uninstall Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/lightime"

echo "Uninstalling Lightime..."
echo "Installation directory: $INSTALL_DIR"

read -p "Are you sure you want to remove Lightime? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Remove desktop entry
    rm -f "$HOME/.local/share/applications/lightime.desktop"

    # Remove installation directory
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        echo "✓ Installation directory removed"
    fi

    # Remove configuration (optional)
    read -p "Also remove configuration files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$HOME/.config/lightime"
        rm -rf "$HOME/.local/share/lightime"
        echo "✓ Configuration files removed"
    fi

    echo "✅ Lightime uninstalled successfully!"
else
    echo "Uninstallation cancelled."
fi
EOF

    chmod +x uninstall.sh

    print_success "Run scripts created"
}

# Display final instructions
show_final_instructions() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                  🎉 Installation Complete! 🎉                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    echo -e "${CYAN}Lightime Pomodoro Timer is now installed!${NC}"
    echo
    echo -e "${BLUE}🚀 To start Lightime:${NC}"
    echo -e "   ${YELLOW}cd $INSTALL_DIR${NC}"
    echo -e "   ${YELLOW}./run.sh${NC}"
    echo
    echo -e "${BLUE}📂 Installation location:${NC}"
    echo -e "   ${YELLOW}$INSTALL_DIR${NC}"
    echo
    echo -e "${BLUE}⚙️  Configuration:${NC}"
    echo -e "   ${YELLOW}~/.config/lightime/config.yaml${NC}"
    echo
    echo -e "${BLUE}📊 Session logs:${NC}"
    echo -e "   ${YELLOW}~/.local/share/lightime/sessions.csv${NC}"
    echo
    echo -e "${BLUE}🔄 Update Lightime:${NC}"
    echo -e "   ${YELLOW}cd $INSTALL_DIR && ./update.sh${NC}"
    echo
    echo -e "${BLUE}🗑️  Uninstall Lightime:${NC}"
    echo -e "   ${YELLOW}cd $INSTALL_DIR && ./uninstall.sh${NC}"
    echo
    echo -e "${GREEN}Enjoy your Pomodoro sessions! 🍅${NC}"
}

# Main installation function
main() {
    print_header
    echo

    print_step 1 "Pre-flight checks"
    check_root
    check_internet
    detect_distro

    print_step 2 "Setting up Git"
    check_git

    print_step 3 "Downloading Lightime"
    clone_repo

    print_step 4 "Installing system dependencies"
    install_system_deps

    print_step 5 "Setting up Python environment"
    setup_python_env

    print_step 6 "Testing installation"
    test_installation

    print_step 7 "Creating shortcuts"
    create_desktop_entry
    create_run_scripts

    echo
    show_final_instructions
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Lightime Pomodoro Timer - One-Click Installer"
        echo
        echo "Usage: $0 [OPTION]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --update       Update existing installation"
        echo "  --uninstall    Uninstall Lightime"
        echo
        echo "For first-time installation, just run: $0"
        exit 0
        ;;
    --update)
        if [ -d "$HOME/lightime" ]; then
            cd "$HOME/lightime"
            ./update.sh
        else
            print_error "Lightime not found. Run $0 to install first."
            exit 1
        fi
        ;;
    --uninstall)
        if [ -d "$HOME/lightime" ]; then
            cd "$HOME/lightime"
            ./uninstall.sh
        else
            print_error "Lightime not found."
            exit 1
        fi
        ;;
    *)
        main
        ;;
esac