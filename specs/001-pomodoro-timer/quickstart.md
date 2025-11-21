# Lightime Quick Start Guide

**Version**: 1.0.0
**Platform**: Linux (Debian/Ubuntu-based and compatible distributions)
**Last Updated**: 2025-01-21

## Overview

Lightime is a lightweight Pomodoro timer for Linux desktop environments that helps you maintain focus during work sessions. It features a tiny always-on-top timer icon, configurable warnings, automatic screen locking, and comprehensive session logging.

## System Requirements

### Supported Platforms

- **Ubuntu**: 22.04 LTS, 24.04 LTS, and later versions
- **Debian**: 11 (Bullseye) and later versions
- **Linux Mint**: 20.x and later versions
- **Pop!_OS**: 22.04 and later versions
- **Other Debian-based distributions** with GTK3 support
- **Fedora**: 37+ (with minor dependency adjustments)
- **Arch Linux**: (with AUR or manual compilation)

### Desktop Environment Compatibility

- **GNOME**: 40+ (Ubuntu/Fedora default)
- **KDE Plasma**: 5.20+ (Kubuntu/Fedora KDE)
- **XFCE**: 4.16+ (Xubuntu)
- **Cinnamon**: 5.0+ (Linux Mint)
- **MATE**: 1.26+ (Ubuntu MATE)
- **Other GTK3-based desktop environments**

### Window System

- **X11**: Fully supported (primary target)
- **Wayland**: Supported with some limitations on global hotkeys

## Installation

### Prerequisites

- Linux distribution with GTK3 support
- Python 3.11 or later
- Basic familiarity with command line
- System tray/notification area support

### Ubuntu/Debian-based Systems

```bash
# Update package lists
sudo apt update

# Install required system packages
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
gir1.2-appindicator3-0.1 libnotify4 xdotool python3-dbus python3-pip
```

### Fedora/RHEL-based Systems

```bash
# Install required packages (adjust for your version)
sudo dnf install python3-gobject python3-cairo gtk3 \
libappindicator-gtk3 libnotify xdotool python3-dbus python3-pip
```

### Arch Linux

```bash
# Install from repositories
sudo pacman -S python-gobject python-cairo gtk3 \
libappindicator-gtk3 libnotify xdotool python-dbus

# Additional Python packages via pip
pip install PyYAML watchdog
```

### Install Lightime

```bash
# Clone the repository
git clone https://github.com/your-username/lightime.git
cd lightime

# Install Python dependencies
pip install -r requirements.txt

# Install the application system-wide
sudo python setup.py install

# Or install locally (recommended for testing)
pip install -e .
```

## Getting Started

### Launch Lightime

```bash
# From command line
lightime

# Or from application menu (if installed via package)
# Look for "Lightime Timer" in your applications
```

### First Run

On first launch, Lightime will:
1. Create `~/.config/lightime/config.yaml` with default settings
2. Create `~/.local/share/lightime/sessions.csv` for logging
3. Add icon to system tray/notification area
4. Display the timer icon on your desktop

### Basic Usage

1. **Start a Timer**: Right-click the timer icon and select a duration
2. **Quick Start**: Use keyboard shortcut `Ctrl+Alt+P` for 25-minute session
3. **Custom Duration**: Right-click → "Custom Timer" → enter minutes
4. **Stop Timer**: Right-click → "Stop Session"

## Configuration

### Edit Configuration File

Open `~/.config/lightime/config.yaml` in your favorite editor:

```yaml
# Basic settings
default_duration: 25
warning_minutes: 2
time_display_format: "MINUTES_SECONDS"

# Visual preferences
icon_size:
  width: 64
  height: 64

# Warning behavior
visual_warnings:
  mode: "FLASH"          # FLASH, RESIZE, COLOR_CHANGE
  flash_interval_ms: 500
  resize_factor: 1.2

# Keyboard shortcuts
keyboard_shortcuts:
  start_25min: "Ctrl+Alt+P"
  start_custom: "Ctrl+Alt+O"

# Quick access durations
preset_durations: [15, 25, 45, 60]
```

### Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `default_duration` | 25 | Default session length in minutes |
| `warning_minutes` | 2 | Minutes before end to show warning |
| `time_display_format` | MINUTES_SECONDS | How to show remaining time |
| `resume_threshold_minutes` | 5 | Max interruption to auto-resume |
| `log_file_format` | CSV | Format for session logging |

### Hot Configuration Changes

Most configuration changes take effect immediately without restarting Lightime. However, some changes require a restart:
- Keyboard shortcut modifications
- Log file format changes
- Icon size changes

## Features

### Always-On-Top Timer

- Tiny timer icon stays above all other windows
- Minimal distraction design
- Displays remaining time continuously
- Position it anywhere on your screen
- Works across all supported desktop environments

### Visual Warnings

When 2 minutes remain, you'll see:
- **Flash Mode**: Icon flashes briefly every second
- **Resize Mode**: Icon grows 20% larger
- **Color Change Mode**: Icon changes to warning color

Configure the warning type in `config.yaml` under `visual_warnings.mode`.

### System Tray Integration

Right-click the timer icon for:
- Start timer with preset durations
- Custom timer input
- Stop current session
- View session statistics

Compatibility across desktop environments:
- **GNOME**: Native AppIndicator3 support
- **KDE**: System tray integration
- **XFCE**: Panel plugin compatibility
- **Others**: Standard status notifier protocol

### Keyboard Shortcuts

- `Ctrl+Alt+P`: Start 25-minute timer
- `Ctrl+Alt+O`: Open custom timer dialog
- `Escape`: Stop current timer (when timer window has focus)

**Note**: Global hotkeys work best on X11. On Wayland, some shortcuts may require system configuration.

### Automatic Screen Lock

When your Pomodoro session ends, Lightime automatically locks your screen using system-appropriate methods:

- **X11**: Super+L key combination via `xdotool`
- **Wayland**: D-Bus session lock via `loginctl lock-session`
- **Fallback**: System-specific screen lock commands

### Session Logging

Lightime automatically logs every completed session to:
- **Location**: `~/.local/share/lightime/sessions.csv`
- **Format**: CSV (configurable to JSON or plain text)
- **Data**: Start time, duration, completion status

#### Sample Log Entry

```csv
session_id,start_time,planned_duration_minutes,actual_duration_minutes,completion_status,interruption_duration_seconds,warning_displayed
550e8400-e29b-41d4-a716-446655440000,2025-01-21T09:00:00Z,25,25.0,COMPLETED,0,true
```

### Data Analysis

Your session data can be imported into spreadsheet applications for analysis:

1. **LibreOffice Calc**: File → Open → Select `sessions.csv`
2. **Google Sheets**: File → Import → Upload CSV file
3. **Microsoft Excel**: Data → From Text/CSV
4. **Python Analysis**: Use pandas for custom analytics

```python
import pandas as pd
df = pd.read_csv('~/.local/share/lightime/sessions.csv')
print(f"Total focus time: {df['actual_duration_minutes'].sum()} minutes")
print(f"Average session duration: {df['actual_duration_minutes'].mean():.1f} minutes")
```

## Troubleshooting

### Common Issues

**Timer icon not showing**:
```bash
# Check if system tray is running (varies by desktop)
ps aux | grep -E "(indicator|tray|status)"
# Restart session services (GNOME example)
killall gnome-shell
# KDE panel restart
kquitapp5 plasmashell && kstart5 plasmashell
```

**Keyboard shortcuts not working**:
```bash
# Check for conflicting shortcuts (GNOME)
gsettings get org.gnome.desktop.wm.keybindings panel-main-menu
# KDE
kwriteconfig5 --file kglobalshortcutsrc --group "kwin" --key "Show Desktop" "Ctrl+Alt+D"
# Try alternative shortcuts in config
```

**Screen lock not working**:
```bash
# Test xdotool (X11)
xdotool key Super+L
# Test D-Bus method (Wayland)
loginctl lock-session
# Install missing tools
sudo apt install xdotool  # Debian/Ubuntu
sudo dnf install xdotool  # Fedora
sudo pacman -S xdotool    # Arch
```

**Dependencies not found** (non-Debian systems):
```bash
# For non-Debian systems, use your package manager:
# Fedora: dnf install
# openSUSE: zypper install
# Arch: pacman -S
# Look for packages containing: python3-gobject, gtk3, appindicator, libnotify
```

**Configuration file corrupted**:
```bash
# Remove and recreate
rm ~/.config/lightime/config.yaml
lightime  # Will create with defaults
```

### Platform-Specific Notes

**Ubuntu 24.04 LTS**:
- Fully supported with Wayland and X11
- Use default package names from installation section

**Fedora**:
- Package names differ slightly (see Fedora installation section)
- Some features may require additional GNOME/KDE packages

**Arch Linux**:
- Install via AUR: `yay -S lightime` (when available)
- Manual installation may be required for latest versions

**Wayland Notes**:
- Global hotkeys may require additional configuration
- Screen locking uses D-Bus method by default
- Some desktop environments have different tray implementations

### Getting Help

1. **Check Logs**: Look at `~/.local/share/lightime/` for error logs
2. **System Monitor**: Ensure Lightime isn't using excessive resources
3. **Distribution Forums**: Search for issues specific to your Linux distribution
4. **GitHub Issues**: Report problems with your system details

### Uninstall

```bash
# If installed via setup.py
sudo python setup.py uninstall

# Remove configuration and data
rm -rf ~/.config/lightime
rm -rf ~/.local/share/lightime
rm -rf ~/.cache/lightime

# For pip installations
pip uninstall lightime
```

## Tips and Best Practices

### Productivity Tips

1. **Customize Presets**: Adjust `preset_durations` in config to match your work style
2. **Interruption Recovery**: Set `resume_threshold_minutes` based on your typical interruptions
3. **Data Review**: Weekly review your session logs to identify patterns
4. **Break Enforcement**: Don't disable automatic screen lock - it ensures proper breaks

### Performance Tips

1. **Minimal Setup**: The default configuration is optimized for low resource usage
2. **Log Rotation**: Lightime automatically archives old logs monthly
3. **Configuration**: Keep the config file simple for best performance

### Distribution-Specific Tips

**Ubuntu/Debian**: Use official repositories for best compatibility
**Fedora**: Enable RPM Fusion for additional packages if needed
**Arch**: Keep system updated for latest GTK3 and Python versions
**Others**: Ensure GTK3 development packages are available

### Privacy

- All data is stored locally on your machine
- No network connections required
- Full ownership of your productivity data
- Configurable data retention policies

## Next Steps

1. **Customize Your Experience**: Edit `~/.config/lightime/config.yaml`
2. **Set Up Keyboard Shortcuts**: Configure hotkeys that don't conflict with your desktop
3. **Import Existing Data**: If migrating from another timer, check the data migration guide
4. **Share Feedback**: Report issues or suggest features on GitHub with your Linux distribution details

Enjoy your productive focus sessions with Lightime! 🍅

---

**Supported Distributions**: Ubuntu 22.04+, Debian 11+, Linux Mint 20+, Fedora 37+, Arch Linux, and most GTK3-based Linux distributions.