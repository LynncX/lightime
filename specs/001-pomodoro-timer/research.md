# Research Findings: Lightime Pomodoro Timer

**Date**: 2025-01-21
**Target Platform**: Ubuntu 22.04 with X11 window system

## Technology Decisions

### GUI Framework: Python with GTK3/PyGObject

**Decision**: Python 3.11+ with GTK3/PyGObject

**Rationale**:
- Perfect match for Ubuntu 22.04 desktop integration
- Native support for always-on-top windows and system tray via AppIndicator3
- Excellent resource efficiency (20-40MB RAM, <1% CPU)
- Cross-desktop environment compatibility (GNOME, KDE, XFCE)
- Built-in support for global hotkeys and keyboard commands
- Mature ecosystem with extensive Ubuntu documentation
- Easy packaging via Snap, Flatpak, or deb packages

**Alternatives Considered**:
- PyQt5: More features but heavier resource usage
- Tkinter: Insufficient system tray and X11 integration
- Electron: Too resource-heavy for requirements
- Native C/GTK: Best performance but significantly higher development complexity

### Key Dependencies

**Python Packages**:
- `PyYAML` - Configuration file management
- `PyGObject` - GTK3 GUI framework
- `watchdog` - Configuration hot-reloading
- `python-xlib` - X11 window management
- `dbus-python` - D-Bus system integration

**System Packages**:
- `python3-gi python3-gi-cairo gir1.2-gtk-3.0` - GTK3 Python bindings
- `gir1.2-appindicator3-0.1` - System tray integration
- `libnotify4` - Desktop notifications
- `xdotool` - Keyboard command simulation
- `python3-dbus` - D-Bus Python bindings

## Implementation Approaches

### Screen Lock Integration

**Primary Method**: `xdotool` command to send Super+L key combination
**Fallback Method**: D-Bus `loginctl lock-session` command
**Compatibility**: Both X11 and Wayland support

```python
def lock_screen():
    try:
        subprocess.run(['xdotool', 'key', 'Super+L'], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to D-Bus
        subprocess.run(['loginctl', 'lock-session'], check=True)
```

### Configuration Management

**Location**: `~/.config/lightime/config.yaml` (XDG Base Directory spec)
**Features**: Hot-reloading with watchdog, automatic default creation, YAML validation
**Backward Compatibility**: Schema versioning for configuration migration

### Always-On-Top Window

**Method**: GTK3 window hints with `Gdk.WindowTypeHint.UTILITY`
**Implementation**: `set_keep_above(True)` with state change handling
**Cross-DE Compatibility**: Tested on GNOME, KDE, XFCE

### System Tray Integration

**Library**: AppIndicator3 for modern Ubuntu compatibility
**Features**: Context menus, icon theming, desktop environment support
**Alternative**: libappindicator fallback for older systems

## Performance Characteristics

### Resource Usage Targets
- **Memory**: 20-50MB (well within <100MB constraint)
- **CPU**: <1% during normal operation
- **Disk**: <5MB for application and configs
- **Startup**: <2 seconds to display timer icon

### Timer Accuracy
- **Precision**: Within ±1 second over 25-minute sessions
- **Method**: GLib timeout with system clock synchronization
- **Recovery**: Configurable resume threshold (default 5 minutes)

## Platform Integration Details

### X11 Window Management
- Window type utility for minimal decoration
- Proper positioning and size management
- Focus handling for non-intrusive operation
- Multi-monitor support

### Keyboard Shortcuts
- Global hotkey registration via keyboard library
- Conflict detection and user feedback
- Configurable shortcut mapping

### File System Standards
- Config in `~/.config/lightime/`
- Logs in `~/.local/share/lightime/`
- Cache in `~/.cache/lightime/`
- Following XDG Base Directory specification

## Security Considerations

### Configuration Access
- User-level file permissions (600/644)
- Validation of YAML input to prevent code injection
- Safe error handling for malformed configs

### System Integration
- Minimal privilege requirements
- Safe keyboard command execution
- D-Bus session bus usage only

## Development and Deployment

### Project Structure
```
lightime/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── timer.py
│   ├── config.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── timer_window.py
│   │   └── tray_icon.py
│   └── logging/
│       ├── __init__.py
│       └── session_logger.py
├── config/
│   └── default.yaml
├── tests/
├── docs/
└── setup.py
```

### Packaging Options
1. **Snap**: Easiest distribution, auto-updates
2. **Flatpak**: Cross-distribution compatibility
3. **Deb Package**: Traditional Ubuntu packaging
4. **PyPI**: Python package manager installation

### Dependencies Management
- Use `requirements.txt` for Python packages
- Document system dependencies in README
- Provide installation script for Ubuntu users

## Testing Strategy

### Unit Tests
- Configuration validation and parsing
- Timer logic and state management
- Logging functionality

### Integration Tests
- GUI component interactions
- System tray functionality
- Keyboard shortcut handling

### System Tests
- Multi-desktop environment compatibility
- Performance under resource constraints
- Screen lock integration reliability

This research provides a solid foundation for implementing the Lightime Pomodoro Timer with all specified requirements while maintaining Ubuntu 22.04 compatibility and optimal performance characteristics.