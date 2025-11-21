# Lightime API Contracts

**Version**: 1.0.0
**Last Updated**: 2025-01-21

## Configuration API

### Configuration Schema

```yaml
# File: ~/.config/lightime/config.yaml
version: "1.0.0"

# Core Timer Settings
default_duration: 25          # Default session length in minutes (1-240)
warning_minutes: 2            # Warning trigger time (1-10)
resume_threshold_minutes: 5   # Max interruption for auto-resume (1-60)

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
log_file_path: "~/.local/share/lightime/sessions.csv"  # Custom log location
auto_log_sessions: true       # Enable automatic session logging
```

### Configuration Validation Rules

```yaml
validation_schema:
  default_duration:
    type: integer
    min: 1
    max: 240
    required: true

  warning_minutes:
    type: integer
    min: 1
    max: 10
    required: true

  resume_threshold_minutes:
    type: integer
    min: 1
    max: 60
    required: true

  icon_size.width:
    type: integer
    min: 16
    max: 256
    required: true

  icon_size.height:
    type: integer
    min: 16
    max: 256
    required: true

  preset_durations:
    type: array
    min_items: 1
    max_items: 10
    items:
      type: integer
      min: 1
      max: 240
```

## Session Logging API

### CSV Log Format

```csv
session_id,start_time,planned_duration_minutes,actual_duration_minutes,completion_status,interruption_duration_seconds,warning_displayed,log_version
550e8400-e29b-41d4-a716-446655440000,2025-01-21T09:00:00Z,25,25.0,COMPLETED,0,true,1.0.0
```

### JSON Log Format

```json
{
  "log_version": "1.0.0",
  "metadata": {
    "created_at": "2025-01-21T00:00:00Z",
    "last_updated": "2025-01-21T09:25:00Z",
    "total_sessions": 1,
    "total_focus_minutes": 25.0
  },
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "start_time": "2025-01-21T09:00:00Z",
      "planned_duration_minutes": 25,
      "actual_duration_minutes": 25.0,
      "completion_status": "COMPLETED",
      "interruption_duration_seconds": 0,
      "warning_displayed": true,
      "end_time": "2025-01-21T09:25:00Z"
    }
  ]
}
```

### Log Field Definitions

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| session_id | String | UUID v4 for unique session identification | Must be valid UUID format |
| start_time | DateTime | ISO 8601 timestamp when session started | Must be valid ISO 8601 |
| planned_duration_minutes | Integer | Intended session length | 1-240 range |
| actual_duration_minutes | Float | Actual completed session time | Positive number |
| completion_status | Enum | How session ended | COMPLETED, MANUAL_STOP, INTERRUPTION |
| interruption_duration_seconds | Integer | Total pause time | Non-negative integer |
| warning_displayed | Boolean | Whether 2-minute warning was shown | true/false |
| end_time | DateTime | ISO 8601 timestamp when session ended | Must be valid ISO 8601 |
| log_version | String | Log format version | Must match current version |

## D-Bus Integration API

### Session Lock Service

```bash
# Method: lock_screen()
# Interface: org.freedesktop.login1.Manager
# Object Path: /org/freedesktop/login1
# Command: gdbus call --session --dest org.freedesktop.login1 --object-path /org/freedesktop/login1/session/auto --method org.freedesktop.login1.Session.Lock
```

### System Integration Commands

```bash
# Screen Lock (X11 fallback)
xdotool key Super+L

# System Notifications
notify-send "Lightime" "Session completed!" -u normal -i clock

# Desktop Entry Registration
# File: ~/.local/share/applications/lightime.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Lightime Timer
Comment=Lightweight Pomodoro Timer
Exec=lightime
Icon=lightime
Terminal=false
Categories=Office;Utility;
```

## Error Handling Contracts

### Configuration Errors

```yaml
configuration_errors:
  invalid_duration:
    code: "CONFIG_001"
    message: "Timer duration must be between 1 and 240 minutes"
    user_action: "Please enter a valid duration between 1 and 240"

  invalid_shortcut:
    code: "CONFIG_002"
    message: "Keyboard shortcut conflicts with system shortcut"
    user_action: "Please choose a different keyboard shortcut"

  corrupted_config:
    code: "CONFIG_003"
    message: "Configuration file is corrupted or invalid"
    user_action: "Configuration reset to defaults. Please reconfigure as needed."
```

### Runtime Errors

```yaml
runtime_errors:
  screen_lock_failed:
    code: "RUNTIME_001"
    message: "Unable to lock screen"
    user_action: "Please check screen lock settings"

  tray_icon_failed:
    code: "RUNTIME_002"
    message: "System tray not available"
    user_action: "Timer will run in window mode only"

  log_write_failed:
    code: "RUNTIME_003"
    message: "Unable to write to log file"
    user_action: "Session data will be cached and written later"
```

## Performance Contracts

### Resource Usage Limits

```yaml
performance_requirements:
  memory_usage:
    maximum: "50MB"
    typical: "20-30MB"
    measurement: "RSS memory"

  cpu_usage:
    maximum: "1%"
    typical: "<0.1%"
    measurement: "During active timer"

  startup_time:
    maximum: "2 seconds"
    typical: "<1 second"
    measurement: "From launch to icon display"

  timer_accuracy:
    drift: "±1 second"
    measurement: "Over 25-minute standard session"
```

### File I/O Requirements

```yaml
file_operations:
  config_read:
    frequency: "On startup and configuration reload"
    timeout: "100ms"
    error_handling: "Fallback to defaults"

  config_write:
    frequency: "On configuration changes"
    timeout: "50ms"
    backup: "Automatic backup before major changes"

  log_append:
    frequency: "After each completed session"
    timeout: "200ms"
    retry_policy: "3 attempts with exponential backoff"
```

## Integration Test Contracts

### Test Scenarios

```yaml
integration_tests:
  timer_operations:
    - name: "Start 25-minute session"
      input: { duration: 25 }
      expected: { state: "RUNNING", remaining: 1500 }

    - name: "2-minute warning trigger"
      input: { initial_remaining: 120 }
      expected: { warning_displayed: true }

    - name: "Session completion"
      input: { remaining: 0 }
      expected: { state: "COMPLETED", screen_locked: true }

  configuration_management:
    - name: "Invalid duration rejection"
      input: { duration: 300 }
      expected: { error: "CONFIG_001" }

    - name: "Hot configuration reload"
      input: { config_change: "icon_size.width: 128" }
      expected: { icon_resized: true }

  system_integration:
    - name: "System tray availability"
      environment: ["GNOME", "KDE", "XFCE"]
      expected: { tray_icon_visible: true }

    - name: "Keyboard shortcut registration"
      input: { shortcut: "Ctrl+Alt+P" }
      expected: { shortcut_registered: true }
```

These contracts define the formal interfaces and expected behaviors for Lightime components, ensuring consistent implementation across different platforms and environments.