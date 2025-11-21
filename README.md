# Lightime Pomodoro Timer

A lightweight, always-on-top Pomodoro timer for Linux desktops with session logging and system integration.

## Features

- **Tiny always-on-top window** that stays above other applications
- **Configurable timer durations** with preset buttons and custom input
- **Visual warnings** when time is running out (flash, resize, or color change)
- **Automatic screen lock** at session completion via Super+L
- **Session logging** with timestamps and duration for productivity analysis
- **System tray integration** with context menu controls
- **Multi-format logging** (CSV, JSON, plain text)
- **Performance monitoring** with configurable limits
- **Cross-distribution support** for Ubuntu, Debian, Fedora, Arch, and other GTK3-based systems

## Installation

### 🚀 Super Easy Installation (Recommended for Beginners)

**One command to install everything:**

```bash
curl -fsSL https://raw.githubusercontent.com/your-username/lightime/main/install.sh | bash
```

That's it! The installer will:
- ✅ Detect your Linux distribution automatically
- ✅ Install all required system dependencies
- ✅ Download and setup Lightime
- ✅ Create desktop menu entry
- ✅ Test everything works

### 📋 Alternative Installation Options

**Option 1: Download and Install**
```bash
wget https://raw.githubusercontent.com/your-username/lightime/main/install.sh
chmod +x install.sh
./install.sh
```

**Option 2: Git Clone**
```bash
git clone https://github.com/your-username/lightime.git
cd lightime
chmod +x install.sh
./install.sh
```

**Option 3: Manual Installation**
See [QUICK_INSTALL.md](QUICK_INSTALL.md) for detailed manual instructions.

### 🏃‍♂️ After Installation

Once installed, start Lightime with:
```bash
cd ~/lightime
./run.sh
```

Or find it in your application menu: **Applications → Office → Lightime**

### Manual Installation

#### System Dependencies

Install the required system packages for your Linux distribution:

**Ubuntu/Debian (22.04+):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-dev \
    libgirepository1.0-dev gcc libcairo2-dev pkg-config \
    python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    libnotify4 libnotify-dev \
    libayatana-appindicator3-dev \
    xdotool
```

**Ubuntu/Debian (older systems):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-dev \
    libgirepository1.0-dev gcc libcairo2-dev pkg-config \
    python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    libnotify4 libnotify-dev \
    libappindicator3-dev \
    xdotool
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip python3-devel \
    gobject-introspection-devel gcc cairo-devel pkg-config \
    python3-gobject python3-gobject-devel \
    libnotify-devel \
    libayatana-appindicator3 \
    xdotool
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip python-gobject \
    cairo pkgconf \
    libnotify libayatana-appindicator \
    xdotool
```

#### Python Dependencies

**Core dependencies (no GUI):**
```bash
pip install -r requirements-core.txt
```

**Full dependencies (with GUI):**
```bash
# Note: PyGObject and pycairo usually installed system-wide
pip install -r requirements.txt
```

### Verify Installation

Test your setup with the quick test script:

```bash
python quick_test.py
```

Expected output:
```
✅ PyYAML available
✅ Watchdog available
✅ psutil available
✅ GTK3 available
✅ AyatanaAppIndicator3 available
✅ Configuration system working
✅ Session management working

🎉 Lightime core functionality is working!
🖥️  GUI should work too - try: python src/main.py
```

## Usage

### Basic Usage

```bash
# Start the application
python src/main.py

# Run with debug logging
python src/main.py --debug

# Use custom configuration directory
python src/main.py --config /path/to/config

# Run integration tests
python src/main.py --test

# Export diagnostic information
python src/main.py --diagnostics diagnostics.json
```

### Application Controls

- **Timer Window**:
  - Start/Pause/Stop buttons for timer control
  - Preset buttons (15, 25, 45, 60 minutes)
  - Time display with configurable format
  - Progress bar showing session completion
  - Visual warnings when time is running out

- **System Tray Icon**:
  - Quick start/stop timer controls
  - Preset timer menu
  - Show/hide timer window
  - Settings and session history (when implemented)

- **Keyboard Shortcuts** (configurable):
  - `Ctrl+Alt+P`: Start 25-minute timer
  - `Ctrl+Alt+O`: Open custom timer dialog
  - `Escape`: Stop current session (when focused)

## Configuration

The application uses YAML configuration files that support hot-reloading.

### Configuration Files

Configuration is loaded from these locations (in order of precedence):
1. `config/default.yaml` - Default settings
2. `~/.config/lightime/config.yaml` - User configuration
3. `~/.config/lightime/local.yaml` - Local overrides

### Default Configuration

```yaml
# Core Timer Settings
default_duration: 25          # Default session length in minutes (1-240)
warning_minutes: 2            # Warning trigger time (1-10)
resume_threshold_minutes: 5   # Max interruption duration for auto-resume (1-60)

# Display Settings
time_display_format: "MINUTES_SECONDS"  # MINUTES_SECONDS | MINUTES_ONLY
icon_size:
  width: 64                   # Icon width in pixels (16-256)
  height: 64                  # Icon height in pixels (16-256)

# Warning Behavior
visual_warnings:
  mode: "FLASH"               # FLASH | RESIZE | COLOR_CHANGE
  flash_interval_ms: 500      # Flash interval in milliseconds (100-2000)
  resize_factor: 1.2          # Size multiplier for resize mode (1.1-2.0)
  warning_color: "#FFA500"    # Color for color change mode (hex format)

# Keyboard Shortcuts
keyboard_shortcuts:
  start_25min: "Ctrl+Alt+P"   # Quick 25-minute timer
  start_custom: "Ctrl+Alt+O"  # Open custom timer dialog
  stop_session: "Escape"      # Stop current session (when focused)

# Preset Durations (in minutes)
preset_durations: [15, 25, 45, 60]  # Quick access options (max 10 items)

# Logging Configuration
log_file_format: "CSV"        # CSV | JSON | PLAIN_TEXT
log_file_path: "~/.local/share/lightime/sessions.csv"
auto_log_sessions: true       # Enable automatic session logging

# Performance Settings
max_cpu_usage: 1.0           # Maximum CPU usage percentage
max_memory_mb: 50            # Maximum memory usage in MB
startup_timeout_seconds: 2   # Maximum startup time in seconds
```

## Session Logging

The application automatically logs completed Pomodoro sessions for productivity analysis. Logs are stored in the configured format:

### CSV Format
```csv
id,session_type,start_time,end_time,duration_minutes,status,interruptions_count,total_interruption_seconds,warning_triggered,actual_duration_minutes,effective_work_minutes,metadata
```

### JSON Format
```json
{
  "version": "1.0.0",
  "generated_at": "2025-11-21T14:30:00",
  "sessions": [
    {
      "id": "abc123",
      "session_type": "work",
      "start_time": "2025-11-21T14:00:00",
      "end_time": "2025-11-21T14:25:00",
      "duration_minutes": 25,
      "status": "completed",
      "interruptions_count": 0,
      "total_interruption_seconds": 0,
      "warning_triggered": true,
      "actual_duration_minutes": 25.0,
      "effective_work_minutes": 25.0,
      "metadata": {}
    }
  ]
}
```

## Development

### Project Structure

```
lightime/
├── src/
│   ├── gui/                 # GTK3 GUI components
│   │   ├── application.py   # Main GTK application
│   │   ├── timer_window.py  # Timer display window
│   │   └── tray_icon.py     # System tray icon
│   ├── models/              # Data models
│   │   ├── config.py        # Configuration models
│   │   └── session.py       # Session data models
│   ├── timer/               # Timer engine
│   │   └── engine.py        # Core timer functionality
│   ├── logging/             # Session logging
│   │   └── session_logger.py
│   ├── utils/               # Utilities
│   │   ├── config.py        # Configuration management
│   │   ├── performance.py   # Performance monitoring
│   │   ├── error_handling.py # Error management
│   │   ├── system_integration.py # System integration
│   │   ├── x11_integration.py # X11-specific integration
│   │   └── helpers.py       # General helper functions
│   ├── app_context.py       # Application context/orchestrator
│   └── main.py              # Main entry point
├── config/
│   └── default.yaml         # Default configuration
├── tests/                   # Test suite
└── requirements.txt         # Python dependencies
```

### Testing

```bash
# Run integration tests
python src/main.py --test

# Test system integration
python -c "
from src.app_context import initialize_app
app = initialize_app()
print('Integration test results:', app.test_integration())
"

# Export diagnostics for debugging
python src/main.py --diagnostics debug_output.json
```

### Performance Monitoring

The application includes built-in performance monitoring with configurable limits:

- CPU usage monitoring
- Memory usage tracking
- File handle leak detection
- Startup time validation
- Performance alerts when limits are exceeded

## Troubleshooting

### Quick Setup Verification

First, verify your installation:
```bash
python quick_test.py
```

If you see ✅ for all items, your setup is working correctly!

### Common Issues

#### 1. Package Installation Errors

**"No matching distribution found for cairo"**
```bash
# Use the correct package name
pip install pycairo  # NOT "cairo"

# Or use the requirements file
pip install -r requirements.txt
```

**"Unmet dependencies" with AppIndicator**
```bash
# Ubuntu 22.04+:
sudo apt install libayatana-appindicator3-dev

# Older Ubuntu/Debian:
sudo apt install libappindicator3-dev
```

#### 2. GTK3 Import Errors

```bash
# Install system dependencies
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Verify installation
python -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK3 working')"
```

#### 3. Tray Icon Not Appearing

```bash
# Install correct AppIndicator library for your system
# Ubuntu 22.04+:
sudo apt install libayatana-appindicator3-dev

# Older systems:
sudo apt install libappindicator3-dev gir1.2-appindicator3-0.1

# Verify installation
python -c "
import gi
try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3
    print('✅ AyatanaAppIndicator3 working')
except:
    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3
        print('✅ AppIndicator3 working (legacy)')
    except:
        print('❌ No AppIndicator available')
"
```

#### 4. Screen Lock Not Working

```bash
# Install xdotool for key sending
sudo apt install xdotool

# Test xdotool
xdotool key Super+L

# Alternative: Use loginctl (systemd systems)
loginctl lock-session
```

#### 5. Core Functionality Issues

```bash
# Test core components separately
python test_models_only.py

# Check basic imports
python -c "
from models.config import LightimeConfig
from models.session import SessionManager
print('✅ Core models working')
"
```

#### 6. Performance Issues

- Check performance limits in `~/.config/lightime/config.yaml`
- Export diagnostics: `python src/main.py --diagnostics debug.json`
- Monitor resource usage:
  ```bash
  htop  # For CPU/memory usage
  lsof -p <lightime_pid>  # For file handles
  ```

### Debug Mode

Enable detailed logging:
```bash
python src/main.py --debug
```

### Error Logs

Check the application error log:
```bash
cat ~/.local/share/lightime/lightime_errors.log
```

### Export Diagnostics

For comprehensive debugging information:
```bash
python src/main.py --diagnostics full_diagnostics.json

# View the diagnostics file
cat full_diagnostics.json | jq .  # If jq is installed
```

### Getting Help

If you encounter issues:

1. **Run the quick test**: `python quick_test.py`
2. **Check the error log**: `cat ~/.local/share/lightime/lightime_errors.log`
3. **Export diagnostics**: `python src/main.py --diagnostics debug.json`
4. **Try minimal installation**: Use `requirements-core.txt` for basic functionality

### Fallback: GUI-less Mode

If GUI issues persist, Lightime still works as a command-line tool:

```bash
# Run tests
python src/main.py --test

# Get help
python src/main.py --help

# Core functionality works without GUI
```

## System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Debian 10+, Fedora 34+, Arch Linux)
- **Python**: 3.11 or higher
- **GTK3**: 3.24 or higher
- **Memory**: < 50MB typical usage
- **CPU**: < 1% typical usage

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please ensure:

1. Code follows the project's coding standards
2. Tests pass for new functionality
3. Documentation is updated as needed
4. Performance limits are respected

## Roadmap

- [ ] Settings dialog for user-friendly configuration
- [ ] Session history viewer and statistics
- [ ] Custom timer duration dialog
- [ ] Additional visual themes and customization
- [ ] Integration with task management systems
- [ ] Mobile app companion (future)
- [ ] Web dashboard (future)