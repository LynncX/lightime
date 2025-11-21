# Implementation Plan: Lightime Pomodoro Timer

**Branch**: `001-pomodoro-timer` | **Date**: 2025-01-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-pomodoro-timer/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Lightime is a lightweight Pomodoro timer application for Linux desktop environments that provides a non-intrusive always-on-top timer icon, configurable visual warnings, automatic screen locking, and comprehensive session logging. The application uses Python with GTK3 for cross-desktop compatibility and minimal resource usage, supporting Ubuntu 22.04+, Debian, and other Linux distributions with GNOME, KDE, XFCE, and other GTK3-based desktop environments.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyYAML, PyGObject (GTK3), watchdog, python-xlib, dbus-python
**Storage**: YAML configuration files, CSV/JSON session logs
**Testing**: pytest, python-xdoctest (for GUI testing)
**Target Platform**: Linux (Ubuntu 22.04+, Debian 11+, Fedora 37+, Arch Linux, compatible distributions)
**Project Type**: Single desktop application with configuration and logging
**Performance Goals**: <1% CPU, <50MB memory, ±1 second timer accuracy, <2 second startup time
**Constraints**: Must work on X11 and Wayland, cross-desktop environment compatibility, minimal system dependencies
**Scale/Scope**: Single user desktop application with local data storage only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Verification

✅ **User-First Experience Design**: All features prioritize non-intrusive operation with simple, functional interface elements

✅ **Configuration-Driven Flexibility**: Complete config.yaml support with hot-reloading and user-friendly editing

✅ **Platform-Specific Integration**: Full Ubuntu 22.04 and Linux desktop environment integration with minimal dependencies

✅ **Data Integrity & Observability**: Comprehensive session logging in multiple formats with user data ownership

✅ **Continuous Performance & Reliability**: Resource constraints and accuracy requirements clearly defined and achievable

**GATE STATUS**: ✅ PASS - All constitutional requirements met

## Project Structure

### Documentation (this feature)

```text
specs/001-pomodoro-timer/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api.md          # API contracts and schemas
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
lightime/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── timer.py                   # Core timer logic and state management
│   ├── config.py                  # Configuration management and validation
│   ├── logging/
│   │   ├── __init__.py
│   │   └── session_logger.py      # Session logging functionality
│   └── gui/
│       ├── __init__.py
│       ├── timer_window.py        # Always-on-top timer display
│       └── tray_icon.py           # System tray integration
├── config/
│   └── default.yaml               # Default configuration template
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── docs/
├── requirements.txt
├── setup.py
└── README.md
```

### Data Directories (User Home)

```text
~/.config/lightime/
├── config.yaml                   # User configuration
└── config.yaml.backup           # Automatic configuration backup

~/.local/share/lightime/
├── sessions.csv                  # Primary session log (CSV format)
├── sessions.json                 # Alternative session log (JSON format)
└── sessions_2025-01.csv          # Monthly archived logs

~/.cache/lightime/
└── session_state.json            # Temporary state for interruption recovery
```

## Phase 0: Research & Technology Decisions ✅

### Completed Research Tasks

- ✅ GUI Framework Selection: Python with GTK3/PyGObject chosen for optimal Ubuntu/Linux integration
- ✅ System Integration Methods: xdotool and D-Bus approaches for screen locking and keyboard shortcuts
- ✅ Configuration Management: XDG Base Directory specification compliance with hot-reloading
- ✅ Cross-Platform Compatibility: Support for Ubuntu, Debian, Fedora, Arch, and other distributions
- ✅ Performance Optimization: Resource usage targets and implementation strategies

**Output**: [research.md](research.md) with comprehensive technology decisions and implementation strategies

## Phase 1: Design & Contracts ✅

### Data Model Design

**Output**: [data-model.md](data-model.md) with complete entity definitions:
- TimerSession with state transitions and validation rules
- UserConfiguration with comprehensive schema
- SessionLog with multiple format support
- Error handling and performance considerations

### API Contracts

**Output**: [contracts/api.md](contracts/api.md) containing:
- Configuration schema and validation rules
- Session logging formats (CSV/JSON)
- D-Bus integration specifications
- Performance and error handling contracts

### Quick Start Guide

**Output**: [quickstart.md](quickstart.md) with:
- Multi-distribution installation instructions
- Configuration examples and options
- Troubleshooting guides for different desktop environments
- Platform-specific compatibility notes

## Implementation Phases

### Phase 2: Core Timer Logic (P1 - MVP)

**Goal**: Basic timer functionality with always-on-top display

**Key Components**:
- Timer session state management
- GTK3 always-on-top window implementation
- Basic configuration loading
- Manual start/stop controls

**Independent Test**: Can start timer, see countdown, and manually stop without crashes

### Phase 3: System Integration (P1)

**Goal**: Full desktop environment integration

**Key Components**:
- System tray integration with AppIndicator3
- Keyboard shortcut handling
- Screen lock functionality (xdotool + D-Bus)
- Cross-desktop compatibility

**Independent Test**: System tray icon appears, shortcuts work, screen locks on completion

### Phase 4: Configuration & Warnings (P2)

**Goal**: User customization and visual warnings

**Key Components**:
- Configuration hot-reloading with watchdog
- Visual warning system (flash/resize/color)
- Custom timer duration input
- Preset duration buttons

**Independent Test**: Configuration changes take effect, warnings display at 2 minutes

### Phase 5: Logging & Analytics (P2)

**Goal**: Session data collection and user insights

**Key Components**:
- Session logging in multiple formats
- Configuration-driven log file location
- Log rotation and archiving
- Data analysis examples

**Independent Test**: Sessions logged correctly, data can be imported for analysis

## Constitution Re-Check

After Phase 1 design completion:

✅ **User-First Experience**: All interface elements designed for simplicity and non-intrusion
✅ **Configuration Flexibility**: Comprehensive YAML-based configuration with hot-reloading
✅ **Platform Integration**: Full Linux desktop environment compatibility validated
✅ **Data Integrity**: Multi-format logging with user ownership and access
✅ **Performance Standards**: Resource usage and accuracy requirements specified and achievable

**FINAL GATE STATUS**: ✅ PASS - Ready for implementation

## Dependencies & Installation

### Python Dependencies

```text
PyYAML>=6.0              # Configuration file parsing
PyGObject>=3.42.0        # GTK3 GUI framework
watchdog>=3.0.0          # Configuration file monitoring
python-xlib>=0.33        # X11 window management
dbus-python>=1.3.2       # D-Bus system integration
```

### System Dependencies (Ubuntu/Debian)

```bash
python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 libnotify4 xdotool python3-dbus
```

### Package Distribution

- **Snap**: Ubuntu Software Center distribution
- **Flatpak**: Cross-distribution compatibility
- **PyPI**: Python package manager installation
- **Deb**: Traditional Ubuntu packaging

## Testing Strategy

### Unit Tests
- Configuration validation and parsing
- Timer state transitions
- Session logging functionality

### Integration Tests
- GTK3 window management
- System tray functionality
- Keyboard shortcut registration
- Screen lock integration

### System Tests
- Multi-desktop environment compatibility (GNOME, KDE, XFCE)
- Cross-distribution compatibility (Ubuntu, Debian, Fedora, Arch)
- Performance under resource constraints
- Timer accuracy over extended periods

### User Acceptance Tests
- Configuration hot-reloading
- Visual warning effectiveness
- Data export and analysis workflows
- Error handling and recovery

## Risk Mitigation

### Technical Risks

**System Integration Issues**:
- Mitigation: Multiple fallback methods for screen lock and shortcuts
- Testing: Comprehensive desktop environment compatibility testing

**Performance Concerns**:
- Mitigation: Conservative resource usage targets and monitoring
- Testing: Load testing with extended timer sessions

**Configuration Complexity**:
- Mitigation: Sensible defaults with comprehensive validation
- Testing: Configuration edge case and corruption handling

### Platform Risks

**Desktop Environment Diversity**:
- Mitigation: Standard GTK3 and AppIndicator3 usage with fallbacks
- Testing: Multi-distribution and desktop environment testing

**Wayland Compatibility**:
- Mitigation: D-Bus primary integration with X11 fallbacks
- Testing: Both X11 and Wayland environment validation

## Success Metrics

### Functional Metrics
- Timer accuracy within ±1 second over 25-minute sessions
- Configuration changes apply within 1 second
- Screen lock activation within 2 seconds of session completion
- Session logging accuracy of 100% for completed sessions

### Performance Metrics
- Memory usage under 50MB during normal operation
- CPU usage under 1% during active timer sessions
- Application startup time under 2 seconds
- System resource impact minimal during extended operation

### User Experience Metrics
- All user stories independently testable and functional
- Configuration changes effective without application restart
- Cross-desktop environment consistent behavior
- Error handling provides clear user guidance

---

## Next Steps

This implementation plan provides a comprehensive foundation for developing Lightime with all specified requirements while maintaining constitutional compliance and cross-platform compatibility.

**Ready for Phase 2**: Execute `/speckit.tasks` to generate detailed implementation tasks based on this plan.