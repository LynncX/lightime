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

### System Dependencies

Install the required system packages for your Linux distribution:

**Ubuntu/Debian:**
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
    libappindicator-gtk3 \
    xdotool
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip python-gobject \
    cairo pkgconf \
    libnotify libappindicator-gtk3 \
    xdotool
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Installation

```bash
# Install in development mode
pip install -e .

# Or run directly
python src/main.py
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

### Common Issues

1. **GTK3 Import Errors**
   ```bash
   # Install system dependencies (see Installation section)
   # Ensure libgirepository1.0-dev and python3-gi are installed
   ```

2. **Tray Icon Not Appearing**
   ```bash
   # Install appindicator3 support
   sudo apt install libappindicator3-dev gir1.2-appindicator3-0.1
   ```

3. **Screen Lock Not Working**
   ```bash
   # Install xdotool for key sending
   sudo apt install xdotool

   # Or ensure loginctl is available (systemd)
   sudo systemctl status systemd-logind
   ```

4. **Performance Issues**
   - Check performance limits in configuration
   - Export diagnostics: `python src/main.py --diagnostics debug.json`
   - Monitor resource usage with system tools

### Debugging

Enable debug logging for detailed output:
```bash
python src/main.py --debug
```

Check the error log file:
```bash
cat ~/.local/share/lightime/lightime_errors.log
```

Export diagnostic information:
```bash
python src/main.py --diagnostics full_diagnostics.json
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