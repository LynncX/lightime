!/bin/bash

# Lightime Pomodoro Timer - One-Click Installation Script
# This script installs Lightime from scratch for beginners

set -e

# Trap Ctrl+C and other signals for clean exit
trap 'print_warning "\nInstallation interrupted by user. Cleaning up..."; cleanup; exit 130' INT TERM

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Animation function with signal checking
spin() {
    local -a marks=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
    while kill -0 "$pid" 2>/dev/null; do
        for mark in "${marks[@]}"; do
            # Check if we've been interrupted
            if ! kill -0 "$pid" 2>/dev/null; then
                printf "\r${YELLOW}⚠${NC} $2... Interrupted!\n"
                return 1
            fi
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

# Cleanup function for interrupted operations
cleanup() {
    # Kill any background processes
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null || true
    fi

    # Clean up any temporary files
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR" 2>/dev/null || true
    fi

    # Reset any changed terminal settings
    stty sane 2>/dev/null || true

    print_status "Cleanup completed"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Please do not run this script as root or with sudo."
        print_status "This script installs to your user directory only."
        exit 1
    fi
}

# Check internet connection with China-friendly fallbacks
check_internet() {
    print_status "Checking internet connection..."

    # Test different sites based on region accessibility
    local international_hosts=("google.com" "cloudflare.com" "github.com")
    local china_hosts=("baidu.com" "qq.com" "163.com")
    local accessible=false

    # Try international hosts first
    for host in "${international_hosts[@]}"; do
        print_status "Trying to connect to $host..."
        if ping -c 1 -W 3 "$host" &>/dev/null; then
            print_success "Internet connection available via $host"
            accessible=true
            INTERNET_REGION="international"
            break
        fi
    done

    # If international fails, try China hosts
    if [ "$accessible" = false ]; then
        for host in "${china_hosts[@]}"; do
            print_status "Trying to connect to $host..."
            if ping -c 1 -W 3 "$host" &>/dev/null; then
                print_success "Internet connection available via $host"
                print_warning "International sites may be inaccessible, will use China-friendly mirrors"
                accessible=true
                INTERNET_REGION="china"
                break
            fi
        done
    fi

    # HTTP fallback test
    if [ "$accessible" = false ]; then
        print_status "Ping failed, trying HTTP connections..."
        local test_urls=("https://httpbin.org/get" "https://www.baidu.com")

        for url in "${test_urls[@]}"; do
            if command -v curl &> /dev/null; then
                if curl -s --connect-timeout 5 --max-time 10 "$url" > /dev/null 2>&1; then
                    if [[ "$url" == *"baidu"* ]]; then
                        print_success "Internet connection available via China site"
                        INTERNET_REGION="china"
                    else
                        print_success "Internet connection available via international site"
                        INTERNET_REGION="international"
                    fi
                    accessible=true
                    break
                fi
            elif command -v wget &> /dev/null; then
                if wget -q --timeout=10 --tries=1 "$url" -O /dev/null 2>&1; then
                    if [[ "$url" == *"baidu"* ]]; then
                        print_success "Internet connection available via China site"
                        INTERNET_REGION="china"
                    else
                        print_success "Internet connection available via international site"
                        INTERNET_REGION="international"
                    fi
                    accessible=true
                    break
                fi
            fi
        done
    fi

    if [ "$accessible" = true ]; then
        return 0
    else
        print_warning "Cannot verify internet connection"
        echo "This could be due to network issues or firewall restrictions"

        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Continuing without verified internet connection..."
            INTERNET_REGION="unknown"
            return 0
        else
            print_error "Installation cancelled due to no internet connection."
            exit 1
        fi
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

# Clone or update repository with mirror support
clone_repo() {
    INSTALL_DIR="$HOME/lightime"

    print_status "Setting up installation directory: $INSTALL_DIR"

    # Define repository URLs based on region accessibility
    # Set REPO_URL environment variable to override default
    DEFAULT_GITHUB_REPO="${REPO_URL:-https://github.com/lynncx/lightime.git}"

    case "$INTERNET_REGION" in
        "china")
            # Always try GitHub first, then China-friendly mirrors as fallbacks
            REPO_URLS=(
                "$DEFAULT_GITHUB_REPO"
                "${REPO_URL:-https://gitee.com/lynncx/lightime.git}"
                "https://hub.fastgit.xyz/lynncx/lightime.git"
            )
            print_status "Will try GitHub first, then China-friendly mirrors as fallbacks..."
            ;;
        "international"|"unknown"|*)
            # International repositories - GitHub first, then alternatives
            REPO_URLS=(
                "$DEFAULT_GITHUB_REPO"
                "https://gitlab.com/lynncx/lightime.git"
                "${REPO_URL:-https://gitee.com/lynncx/lightime.git}"
            )
            print_status "Using GitHub as primary repository with fallbacks..."
            ;;
    esac

    # Show the repository URL being used
    print_status "Primary repository: ${REPO_URLS[0]}"
    if [ -n "$REPO_URL" ]; then
        print_status "Using custom repository: $REPO_URL"
    fi

    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Lightime directory already exists. Updating..."
        cd "$INSTALL_DIR"

        # Try updating with current remote first
        if git pull origin main 2>/dev/null || git pull origin master 2>/dev/null; then
            print_success "Repository updated successfully"
        else
            print_warning "Could not update from current remote - trying alternative mirrors..."

            # Try alternative remotes
            for url in "${REPO_URLS[@]}"; do
                print_status "Trying mirror: $url"
                if git remote set-url origin "$url" 2>/dev/null && git pull origin main 2>/dev/null; then
                    print_success "Successfully updated from: $url"
                    break
                fi
            done
        fi
    else
        print_status "Cloning Lightime repository..."
        cd "$HOME"

        clone_success=false
        for url in "${REPO_URLS[@]}"; do
            print_status "Attempting to clone from: $url"
            if timeout 60 git clone "$url" lightime 2>/dev/null; then
                print_success "Successfully cloned from: $url"
                clone_success=true
                cd "$INSTALL_DIR"

                # Set the successful URL as origin
                git remote set-url origin "$url"
                break
            else
                print_warning "Failed to clone from: $url"
            fi
        done

        if [ "$clone_success" = false ]; then
            print_error "Failed to clone from all mirrors."
            print_error "Please check your internet connection or repository availability."
            print_error "You can also try downloading the repository manually:"
            print_error "1. Download ZIP file from your browser"
            print_error "2. Extract to $HOME/lightime"
            print_error "3. Run the install script again with --offline flag"

            # Check if user wants to try offline installation
            echo
            read -p "Try offline installation with local files? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                setup_offline_installation
                return $?
            else
                exit 1
            fi
        fi
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

# Setup Python environment with China-friendly mirrors
setup_python_env() {
    print_status "Setting up Python environment..."

    cd "$INSTALL_DIR"

    # Check if uv is available for faster installation
    if command -v uv &> /dev/null; then
        print_status "Using uv for fast Python environment setup..."
        uv venv lightime-env
        source "$INSTALL_DIR/lightime-env/bin/activate"

        # Use region-specific pip mirrors
        case "$INTERNET_REGION" in
            "china")
                print_status "Using China pip mirrors for faster downloads..."
                uv pip install -r requirements-conda.txt \
                    --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ \
                    --extra-index-url https://pypi.org/simple/ || \
                uv pip install -r requirements-conda.txt
                ;;
            *)
                uv pip install -r requirements-conda.txt
                ;;
        esac
    else
        print_status "Using standard Python venv..."
        python3 -m venv lightime-env
        source "$INSTALL_DIR/lightime-env/bin/activate"

        # Upgrade pip with region-specific mirrors
        case "$INTERNET_REGION" in
            "china")
                print_status "Using China pip mirrors for faster downloads..."
                pip install --upgrade pip \
                    -i https://pypi.tuna.tsinghua.edu.cn/simple/ || \
                pip install --upgrade pip

                # Install dependencies with China mirrors
                pip install -r requirements-conda.txt \
                    -i https://pypi.tuna.tsinghua.edu.cn/simple/ || \
                pip install -r requirements-conda.txt \
                    -i https://mirrors.aliyun.com/pypi/simple/ || \
                pip install -r requirements-conda.txt
                ;;
            *)
                pip install --upgrade pip
                pip install -r requirements-conda.txt
                ;;
        esac
    fi

    print_success "Python environment ready"
}

# Setup offline installation (for when git cloning fails)
setup_offline_installation() {
    print_status "Setting up offline installation..."

    # Check if lightime directory exists with source files
    if [ ! -d "$INSTALL_DIR" ]; then
        print_error "Lightime directory not found at $INSTALL_DIR"
        print_error "Please download and extract the repository manually first:"
        print_error "1. Download from: https://github.com/lynncx/lightime/releases"
        print_error "2. Extract to: $HOME/lightime"
        print_error "3. Run this script again"
        exit 1
    fi

    cd "$INSTALL_DIR"

    # Check for essential files
    local required_files=("src/main.py" "requirements-conda.txt")
    local missing_files=()

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done

    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "Missing required files for offline installation:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi

    print_success "Local source files found, proceeding with offline installation"
    INTERNET_REGION="offline"
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
        echo "  --offline      Offline installation (requires downloaded source)"
        echo
        echo "For first-time installation, just run: $0"
        echo
        echo "China/Mirror Support:"
        echo "  This script automatically detects your network region and uses"
        echo "  appropriate mirrors for GitHub, PyPI, and package repositories."
        echo "  For China users, it uses Tsinghua/Alibaba mirrors for faster downloads."
        exit 0
        ;;
    --offline)
        print_status "Offline installation mode"
        INTERNET_REGION="offline"
        setup_offline_installation

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
