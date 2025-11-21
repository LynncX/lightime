# Feature Specification: Lightime Pomodoro Timer

**Feature Branch**: `001-pomodoro-timer`
**Created**: 2025-01-21
**Status**: Draft
**Input**: User description: "I would like you to make a pomodoro named "lightime" on my ubuntu22.04, featuring tiny icon always on top, warning me when the left time is about two minutes, and automatically locked the screen at the end of the pomodoro. i wish the pomodoro time can be set freely by user, and wish the tiny icon is simple but delicate, and the screen lock can be achieved by sending Super+L to lock the screen.as for the warning, just flash or resize the icon will be good, i think."

## Clarifications

### Session 2025-01-21

- Q: How should system handle attempts to start timer when one is already running? → A: Disallow concurrent sessions, show error message when timer already running
- Q: What timer duration validation rules should be enforced? → A: 1-240 minutes, reject negative/zero, show error for >240
- Q: How should visual warning behavior be configured? → A: User-configurable through config.yaml with multiple warning modes (flash, resize, color change) and timing controls
- Q: How should system recover from interruptions (sleep, restart)? → A: User-configurable resume threshold through config.yaml (default 5 minutes), restart if interruption exceeds threshold
- Q: Where should config.yaml be located? → A: ~/.config/lightime/config.yaml, fallback to application directory
- Q: What log file format should be used for Pomodoro sessions? → A: Configurable through config.yaml with CSV as default format (supports JSON and plain text alternatives)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start Timer Session (Priority: P1)

User starts a Pomodoro session with their preferred duration and sees a tiny timer icon that stays visible on top of all other windows.

**Why this priority**: Core functionality that enables the entire Pomodoro workflow - without this feature, the application serves no purpose.

**Independent Test**: Can be fully tested by starting a timer session and verifying the icon appears and counts down, delivering immediate time tracking value to users.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** the user sets a timer duration and clicks start, **Then** a tiny icon appears and begins counting down from the specified duration
2. **Given** a timer is running, **When** other windows are opened or maximized, **Then** the timer icon remains visible on top of all other windows
3. **Given** no timer is running, **When** the user launches the application, **Then** they can input a custom duration and start a new session

---

### User Story 2 - Receive End-of-Session Warning (Priority: P2)

User receives a visual warning when 2 minutes remain in their Pomodoro session through icon flashing or resizing.

**Why this priority**: Provides users with transition time to complete thoughts and prepare for break, enhancing productivity and session completion rates.

**Independent Test**: Can be fully tested by running a timer and waiting for the 2-minute mark, then observing the visual warning behavior.

**Acceptance Scenarios**:

1. **Given** a timer is running with more than 2 minutes remaining, **When** exactly 2 minutes remain, **Then** the timer icon flashes or resizes to alert the user
2. **Given** the warning is active, **When** the timer continues counting down, **Then** the visual warning continues until the session ends
3. **Given** a timer is started with less than 2 minutes duration, **When** the timer starts, **Then** no warning is displayed since the 2-minute threshold won't be reached

---

### User Story 3 - Automatic Screen Lock Completion (Priority: P1)

When the timer reaches zero, the system automatically locks the screen to enforce the break period.

**Why this priority**: Ensures users take proper breaks, which is essential for the Pomodoro technique's effectiveness in preventing burnout and maintaining productivity.

**Independent Test**: Can be fully tested by running a timer to completion and verifying the screen locks automatically.

**Acceptance Scenarios**:

1. **Given** a timer is running, **When** the countdown reaches zero, **Then** the system automatically locks the screen
2. **Given** the screen locks at session end, **When** the user unlocks the screen, **Then** they can start a new timer session
3. **Given** a timer is running, **When** the user manually stops the timer before completion, **Then** the screen does not lock

---

### User Story 4 - Quick Access Timer Controls (Priority: P2)

User can quickly start timer sessions using either keyboard shortcuts or by hovering over the timer icon to access a context menu with preset duration options.

**Why this priority**: Provides efficient access to common timer durations without interrupting workflow, improving productivity and user experience.

**Independent Test**: Can be fully tested by configuring shortcuts and testing both keyboard and hover menu interactions.

**Acceptance Scenarios**:

1. **Given** keyboard shortcuts are configured, **When** the user presses the configured shortcut, **Then** a timer session starts immediately with the preset duration
2. **Given** the timer icon is visible, **When** the user moves mouse over the icon, **Then** a context menu appears showing available preset durations
3. **Given** the context menu is displayed, **When** the user clicks on a preset duration option, **Then** a timer session starts with the selected duration
4. **Given** no shortcuts are configured in config.yaml, **When** the user tries to use shortcuts, **Then** the default shortcuts are used or shortcuts are disabled

---

### User Story 5 - Pomodoro Session Logging (Priority: P2)

User can automatically record every completed Pomodoro session to a log file with timestamps and duration data for productivity analysis and visualization.

**Why this priority**: Enables users to track their productivity patterns, analyze focus time, and create visualizations for self-improvement and progress monitoring.

**Independent Test**: Can be fully tested by completing timer sessions and verifying log file creation with accurate timestamp and duration data.

**Acceptance Scenarios**:

1. **Given** a timer session completes successfully, **When** the session ends, **Then** a new entry is created in the log file with start timestamp and duration
2. **Given** multiple timer sessions are completed, **When** the user views the log file, **Then** all sessions are recorded in chronological order with complete data
3. **Given** the user wants to analyze their productivity, **When** they access the log file, **Then** the data format supports easy import into visualization tools for plots, tables, and heatmaps
4. **Given** no log file exists, **When** the first timer session completes, **Then** a new log file is created with appropriate headers and format

---

### User Story 6 - Configure Timer Duration (Priority: P2)

User can freely set any Pomodoro duration according to their preference and workflow needs through configurable preset buttons and custom input.

**Why this priority**: Allows personalization of the Pomodoro technique to match individual focus spans and work patterns, increasing adoption and effectiveness.

**Independent Test**: Can be fully tested by setting various timer durations and verifying the timer counts down from the exact specified duration.

**Acceptance Scenarios**:

1. **Given** no timer is running, **When** the user inputs a duration and starts the timer, **Then** the timer counts down from exactly the specified duration
2. **Given** the user wants to set a duration, **When** they access timer settings, **Then** they can input any positive number of minutes
3. **Given** a previous timer session ended, **When** starting a new session, **Then** they can choose to use the same duration or set a new one
4. **Given** the user wants to customize presets, **When** they edit config.yaml, **Then** the preset buttons are updated on next application start

---

### Edge Cases

- What happens when the system restarts or shuts down during an active timer session?
- How does system handle timer duration inputs outside 1-240 minute range?
- What happens when multiple monitor configurations change during a timer session?
- How does system behave when system resources are extremely low or memory is constrained?
- How should system notify users when they attempt to start a timer while one is already running?
- What specific error message should be displayed when concurrent session attempt is blocked?
- How should system handle logging when timer sessions are manually stopped before completion?
- What happens if log file becomes corrupted or unreadable?
- How should system handle log file when disk space is limited?
- What log file format preferences should be supported through config.yaml configuration?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a tiny, simple, and delicate timer icon that remains always on top of other windows
- **FR-002**: Users MUST be able to set custom timer durations in minutes before starting a session
- **FR-003**: System MUST provide configurable visual warning modes (flash, resize, color change) with user-defined timing through config.yaml
- **FR-018**: System MUST allow users to configure icon size, warning timing, and menu options through config.yaml
- **FR-019**: System MUST provide brief, non-annoying warnings that alert users without continuous disruption, with maximum flash duration of 0.5 seconds and maximum frequency of 1 flash per second
- **FR-004**: System MUST automatically lock the screen when the timer reaches zero by sending Super+L key combination
- **FR-005**: System MUST count down in real-time and display the remaining time accurately
- **FR-006**: Users MUST be able to start, stop, and restart timer sessions
- **FR-007**: System MUST handle timer state persistence with user-configurable resume threshold (default 5 minutes); sessions MUST restart if interruption duration exceeds threshold and resume automatically if within threshold
- **FR-021**: System MUST provide default values for all configurable settings when config.yaml is missing or incomplete
- **FR-008**: Users MUST be able to input timer duration through preset buttons and custom text input
- **FR-009**: System MUST validate timer duration inputs to enforce 1-240 minute range
- **FR-017**: System MUST reject negative, zero, and >240 minute duration inputs with clear error messages
- **FR-010**: System MUST display remaining time in user-configurable format (minutes:seconds or minutes only)
- **FR-011**: Users MUST be able to configure preset buttons, display format, and keyboard shortcuts through config.yaml file
- **FR-012**: System MUST read configuration from ~/.config/lightime/config.yaml, fallback to application directory
- **FR-022**: System MUST create user config directory and default config if neither location exists
- **FR-013**: Users MUST be able to start timer sessions using configurable keyboard shortcuts
- **FR-014**: Users MUST be able to access timer options menu by moving mouse over the timer icon
- **FR-015**: System MUST prevent starting concurrent timer sessions and display clear error message
- **FR-016**: System MUST provide user-friendly notification when timer start attempt is blocked due to active session
- **FR-023**: System MUST automatically log every completed Pomodoro session with start timestamp and duration
- **FR-024**: System MUST store log data in structured format convenient for data analysis and visualization
- **FR-025**: System MUST create log file if it doesn't exist when first session is completed
- **FR-026**: System MUST ensure log file format supports easy import into plotting and analysis tools
- **FR-027**: System MUST support configurable log file formats (CSV, JSON, plain text) through config.yaml with CSV as default
- **FR-028**: System MUST handle log file creation errors gracefully and provide user feedback

### Key Entities *(include if feature involves data)*

- **Timer Session**: Represents a single Pomodoro session with start time, duration, current state (running/paused/stopped), and remaining time
- **User Preferences**: Stores user's preferred timer duration, visual warning preferences, display settings, and keyboard shortcuts
- **Timer State**: Current countdown state including remaining time, warning status, and session completion flag
- **Configuration File**: User-editable config.yaml that defines preset durations, time display format, keyboard shortcuts, visual warning modes, icon sizes, warning timing, and logging preferences
- **Context Menu**: Dynamic menu that appears on hover showing available preset timer durations for quick access
- **Session Log**: Structured log file containing completed Pomodoro session data with timestamps, durations, and completion status for productivity analysis
- **Log Entry**: Individual record in session log containing start time (date + time), duration in minutes, and session completion status

### Dependencies and Assumptions

**Platform Dependencies**:
- Ubuntu 22.04 operating system
- Desktop environment that supports "always on top" window behavior
- Screen lock functionality accessible via Super+L keyboard shortcut

**System Requirements**:
- Graphical desktop environment with system tray or notification area support
- Ability to send keyboard commands (Super+L) to system
- File system access for reading config.yaml configuration file
- Permission to run applications that can stay on top of other windows

**Assumptions**:
- User has desktop environment configured to respond to Super+L for screen lock
- User has necessary permissions to install/run applications with window management capabilities
- Config.yaml file will be located at ~/.config/lightime/config.yaml with fallback to application directory
- System will create default config if user or application config doesn't exist
- System clock maintains accurate time for countdown functionality
- User has basic familiarity with YAML file format for configuration

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can start a timer session in under 10 seconds from application launch
- **SC-002**: Timer icon remains visible 100% of time during active sessions regardless of other application usage
- **SC-003**: Visual warning appears within 1 second of the 2-minute mark with 99% accuracy
- **SC-004**: Screen locks automatically within 2 seconds of timer reaching zero in 95% of sessions
- **SC-005**: Users can set any timer duration between 1 minute and 240 minutes (4 hours) with 100% accuracy
- **SC-006**: Timer countdown accuracy maintains within ±1 second over a 25-minute standard session
- **SC-007**: Application uses minimal system resources (<1% CPU, <50MB memory) during timer operation
- **SC-008**: 90% of users successfully complete timer sessions without manual intervention in first week of use
- **SC-009**: 100% of completed Pomodoro sessions are accurately logged with correct timestamps and duration
- **SC-010**: Log file data format can be imported into common data analysis tools without transformation
- **SC-011**: Log entries are created within 1 second of session completion
