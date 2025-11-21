"""
Configuration models for Lightime Pomodoro Timer
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import os


class TimeDisplayFormat(Enum):
    """Time display format options"""
    MINUTES_SECONDS = "MINUTES_SECONDS"
    MINUTES_ONLY = "MINUTES_ONLY"


class VisualWarningMode(Enum):
    """Visual warning mode options"""
    FLASH = "FLASH"
    RESIZE = "RESIZE"
    COLOR_CHANGE = "COLOR_CHANGE"


class LogFileFormat(Enum):
    """Log file format options"""
    CSV = "CSV"
    JSON = "JSON"
    PLAIN_TEXT = "PLAIN_TEXT"


@dataclass
class IconSize:
    """Icon size configuration"""
    width: int = 64
    height: int = 64

    def __post_init__(self):
        """Validate icon size dimensions"""
        if not (16 <= self.width <= 256):
            raise ValueError(f"Icon width must be between 16 and 256 pixels, got {self.width}")
        if not (16 <= self.height <= 256):
            raise ValueError(f"Icon height must be between 16 and 256 pixels, got {self.height}")


@dataclass
class VisualWarnings:
    """Visual warning configuration"""
    mode: VisualWarningMode = VisualWarningMode.FLASH
    flash_interval_ms: int = 500
    resize_factor: float = 1.2
    warning_color: str = "#FFA500"

    def __post_init__(self):
        """Validate visual warning settings"""
        if not (100 <= self.flash_interval_ms <= 2000):
            raise ValueError(f"Flash interval must be between 100 and 2000ms, got {self.flash_interval_ms}")
        if not (1.1 <= self.resize_factor <= 2.0):
            raise ValueError(f"Resize factor must be between 1.1 and 2.0, got {self.resize_factor}")
        if not self.warning_color.startswith("#") or len(self.warning_color) != 7:
            raise ValueError(f"Warning color must be in hex format #RRGGBB, got {self.warning_color}")


@dataclass
class KeyboardShortcuts:
    """Keyboard shortcuts configuration"""
    start_25min: str = "Ctrl+Alt+P"
    start_custom: str = "Ctrl+Alt+O"
    stop_session: str = "Escape"


@dataclass
class PerformanceSettings:
    """Performance constraints configuration"""
    max_cpu_usage: float = 1.0
    max_memory_mb: int = 50
    startup_timeout_seconds: int = 2

    def __post_init__(self):
        """Validate performance settings"""
        if not (0.1 <= self.max_cpu_usage <= 100.0):
            raise ValueError(f"Max CPU usage must be between 0.1 and 100.0, got {self.max_cpu_usage}")
        if not (10 <= self.max_memory_mb <= 500):
            raise ValueError(f"Max memory must be between 10 and 500MB, got {self.max_memory_mb}")
        if not (1 <= self.startup_timeout_seconds <= 30):
            raise ValueError(f"Startup timeout must be between 1 and 30 seconds, got {self.startup_timeout_seconds}")


@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_file_format: LogFileFormat = LogFileFormat.CSV
    log_file_path: str = "~/.local/share/lightime/sessions.csv"
    auto_log_sessions: bool = True

    def get_expanded_path(self) -> Path:
        """Get the log file path with user directory expanded"""
        return Path(self.log_file_path).expanduser()

    def __post_init__(self):
        """Validate logging configuration"""
        valid_formats = {LogFileFormat.CSV, LogFileFormat.JSON, LogFileFormat.PLAIN_TEXT}
        if self.log_file_format not in valid_formats:
            raise ValueError(f"Invalid log file format: {self.log_file_format}")


@dataclass
class LightimeConfig:
    """Main configuration class for Lightime"""

    # Core timer settings
    config_version: str = "1.0.0"
    default_duration: int = 25
    warning_minutes: int = 2
    resume_threshold_minutes: int = 5

    # Display settings
    time_display_format: TimeDisplayFormat = TimeDisplayFormat.MINUTES_SECONDS
    icon_size: IconSize = field(default_factory=IconSize)

    # Warning behavior
    visual_warnings: VisualWarnings = field(default_factory=VisualWarnings)

    # Keyboard shortcuts
    keyboard_shortcuts: KeyboardShortcuts = field(default_factory=KeyboardShortcuts)

    # Preset durations (in minutes)
    preset_durations: List[int] = field(default_factory=lambda: [15, 25, 45, 60])

    # Logging configuration
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Performance settings
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)

    def __post_init__(self):
        """Validate all configuration settings"""
        if not (1 <= self.default_duration <= 240):
            raise ValueError(f"Default duration must be between 1 and 240 minutes, got {self.default_duration}")
        if not (1 <= self.warning_minutes <= 10):
            raise ValueError(f"Warning minutes must be between 1 and 10, got {self.warning_minutes}")
        if not (1 <= self.resume_threshold_minutes <= 60):
            raise ValueError(f"Resume threshold must be between 1 and 60 minutes, got {self.resume_threshold_minutes}")
        if not (1 <= len(self.preset_durations) <= 10):
            raise ValueError(f"Preset durations must have 1-10 items, got {len(self.preset_durations)}")
        if any(duration < 1 or duration > 240 for duration in self.preset_durations):
            raise ValueError("All preset durations must be between 1 and 240 minutes")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LightimeConfig':
        """Create configuration from dictionary"""
        config = cls()

        # Update core settings
        if 'config_version' in data:
            config.config_version = data['config_version']
        if 'default_duration' in data:
            config.default_duration = int(data['default_duration'])
        if 'warning_minutes' in data:
            config.warning_minutes = int(data['warning_minutes'])
        if 'resume_threshold_minutes' in data:
            config.resume_threshold_minutes = int(data['resume_threshold_minutes'])

        # Update display settings
        if 'time_display_format' in data:
            config.time_display_format = TimeDisplayFormat(data['time_display_format'])
        if 'icon_size' in data:
            icon_data = data['icon_size']
            config.icon_size = IconSize(
                width=icon_data.get('width', 64),
                height=icon_data.get('height', 64)
            )

        # Update warning settings
        if 'visual_warnings' in data:
            warning_data = data['visual_warnings']
            config.visual_warnings = VisualWarnings(
                mode=VisualWarningMode(warning_data.get('mode', 'FLASH')),
                flash_interval_ms=warning_data.get('flash_interval_ms', 500),
                resize_factor=warning_data.get('resize_factor', 1.2),
                warning_color=warning_data.get('warning_color', '#FFA500')
            )

        # Update keyboard shortcuts
        if 'keyboard_shortcuts' in data:
            kb_data = data['keyboard_shortcuts']
            config.keyboard_shortcuts = KeyboardShortcuts(
                start_25min=kb_data.get('start_25min', 'Ctrl+Alt+P'),
                start_custom=kb_data.get('start_custom', 'Ctrl+Alt+O'),
                stop_session=kb_data.get('stop_session', 'Escape')
            )

        # Update preset durations
        if 'preset_durations' in data:
            config.preset_durations = [int(d) for d in data['preset_durations']]

        # Update logging config
        if 'log_file_format' in data:
            config.logging.log_file_format = LogFileFormat(data['log_file_format'])
        if 'log_file_path' in data:
            config.logging.log_file_path = data['log_file_path']
        if 'auto_log_sessions' in data:
            config.logging.auto_log_sessions = bool(data['auto_log_sessions'])

        # Update performance settings
        if 'max_cpu_usage' in data:
            config.performance.max_cpu_usage = float(data['max_cpu_usage'])
        if 'max_memory_mb' in data:
            config.performance.max_memory_mb = int(data['max_memory_mb'])
        if 'startup_timeout_seconds' in data:
            config.performance.startup_timeout_seconds = int(data['startup_timeout_seconds'])

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'config_version': self.config_version,
            'default_duration': self.default_duration,
            'warning_minutes': self.warning_minutes,
            'resume_threshold_minutes': self.resume_threshold_minutes,
            'time_display_format': self.time_display_format.value,
            'icon_size': {
                'width': self.icon_size.width,
                'height': self.icon_size.height
            },
            'visual_warnings': {
                'mode': self.visual_warnings.mode.value,
                'flash_interval_ms': self.visual_warnings.flash_interval_ms,
                'resize_factor': self.visual_warnings.resize_factor,
                'warning_color': self.visual_warnings.warning_color
            },
            'keyboard_shortcuts': {
                'start_25min': self.keyboard_shortcuts.start_25min,
                'start_custom': self.keyboard_shortcuts.start_custom,
                'stop_session': self.keyboard_shortcuts.stop_session
            },
            'preset_durations': self.preset_durations,
            'log_file_format': self.logging.log_file_format.value,
            'log_file_path': self.logging.log_file_path,
            'auto_log_sessions': self.logging.auto_log_sessions,
            'max_cpu_usage': self.performance.max_cpu_usage,
            'max_memory_mb': self.performance.max_memory_mb,
            'startup_timeout_seconds': self.performance.startup_timeout_seconds
        }


class ConfigPaths:
    """Configuration file paths management"""

    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        self.config_dir = Path(config_dir) if config_dir else self._get_default_config_dir()

    def _get_default_config_dir(self) -> Path:
        """Get default configuration directory"""
        # Try XDG_CONFIG_HOME first, then fallback to ~/.config
        xdg_config = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config:
            return Path(xdg_config) / "lightime"
        return Path.home() / ".config" / "lightime"

    @property
    def default_config_file(self) -> Path:
        """Path to default configuration file"""
        return self.config_dir / "default.yaml"

    @property
    def user_config_file(self) -> Path:
        """Path to user configuration file"""
        return self.config_dir / "config.yaml"

    @property
    def local_config_file(self) -> Path:
        """Path to local configuration file"""
        return self.config_dir / "local.yaml"

    def get_config_files(self) -> List[Path]:
        """Get list of configuration files in order of precedence"""
        files = []
        if self.default_config_file.exists():
            files.append(self.default_config_file)
        if self.user_config_file.exists():
            files.append(self.user_config_file)
        if self.local_config_file.exists():
            files.append(self.local_config_file)
        return files