"""
General utility functions for Lightime Pomodoro Timer
"""

import os
import sys
import signal
import time
import math
from datetime import datetime, timedelta
from typing import Union, Optional, List, Dict, Any
from pathlib import Path
import tempfile
import json


def format_time_display(
    seconds: Union[int, float],
    format_type: str = "MINUTES_SECONDS",
    show_hours: bool = False
) -> str:
    """Format time display according to specified format"""
    if not isinstance(seconds, (int, float)):
        return "00:00"

    # Handle negative seconds
    if seconds < 0:
        seconds = abs(seconds)

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if format_type == "MINUTES_SECONDS":
        if show_hours and hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            total_minutes = minutes + (hours * 60)
            return f"{total_minutes:02d}:{secs:02d}"
    elif format_type == "MINUTES_ONLY":
        total_minutes = minutes + (hours * 60)
        if secs >= 30:  # Round up
            total_minutes += 1
        return f"{total_minutes}m"
    elif format_type == "SECONDS_ONLY":
        return f"{int(seconds)}s"
    else:
        # Default to MINUTES_SECONDS
        total_minutes = minutes + (hours * 60)
        return f"{total_minutes:02d}:{secs:02d}"


def parse_duration_string(duration_str: str) -> Optional[int]:
    """Parse duration string and return minutes"""
    if not duration_str or not isinstance(duration_str, str):
        return None

    duration_str = duration_str.strip().lower()

    # Try to parse as pure number first
    try:
        minutes = int(duration_str)
        if 1 <= minutes <= 240:
            return minutes
    except ValueError:
        pass

    # Parse with suffixes
    suffixes = {
        'm': 1,
        'min': 1,
        'mins': 1,
        'minutes': 1,
        'h': 60,
        'hr': 60,
        'hour': 60,
        'hours': 60,
        's': 1/60,
        'sec': 1/60,
        'secs': 1/60,
        'seconds': 1/60
    }

    for suffix, multiplier in suffixes.items():
        if duration_str.endswith(suffix):
            try:
                number_part = duration_str[:-len(suffix)].strip()
                value = float(number_part)
                minutes = int(value * multiplier)
                if 1 <= minutes <= 240:
                    return minutes
            except ValueError:
                pass

    return None


def calculate_session_progress(
    elapsed_seconds: Union[int, float],
    total_seconds: Union[int, float]
) -> float:
    """Calculate session progress as percentage (0.0 to 1.0)"""
    try:
        if total_seconds <= 0:
            return 0.0

        progress = elapsed_seconds / total_seconds
        return max(0.0, min(1.0, progress))
    except (ValueError, TypeError):
        return 0.0


def get_time_until_warning(
    elapsed_seconds: Union[int, float],
    total_seconds: Union[int, float],
    warning_minutes: int
) -> Optional[int]:
    """Get seconds until warning threshold is reached"""
    try:
        warning_seconds = warning_minutes * 60
        warning_point = total_seconds - warning_seconds

        if elapsed_seconds >= warning_point:
            return 0  # Already at or past warning

        return int(warning_point - elapsed_seconds)
    except (ValueError, TypeError):
        return None


def ensure_directory_exists(dir_path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if necessary"""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(filename: str) -> str:
    """Create a safe filename by removing/replacing problematic characters"""
    if not isinstance(filename, str):
        filename = str(filename)

    # Replace problematic characters
    replacements = {
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '_',
        '<': '_',
        '>': '_',
        '|': '_',
        '\n': '_',
        '\r': '_',
        '\t': '_'
    }

    for old, new in replacements.items():
        filename = filename.replace(old, new)

    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')

    # Ensure not empty
    if not filename:
        filename = "unnamed"

    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        max_name_len = 255 - len(ext)
        filename = name[:max_name_len] + ext

    return filename


def create_backup_file(file_path: Union[str, Path]) -> Path:
    """Create a backup of the specified file"""
    source = Path(file_path)
    if not source.exists():
        raise FileNotFoundError(f"Source file does not exist: {file_path}")

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source.stem}_backup_{timestamp}{source.suffix}"
    backup_path = source.parent / backup_name

    import shutil
    shutil.copy2(source, backup_path)
    return backup_path


def validate_rgb_color(color_str: str) -> bool:
    """Validate RGB color string in hex format"""
    if not isinstance(color_str, str):
        return False

    color_str = color_str.strip()
    if not color_str.startswith('#'):
        return False

    hex_part = color_str[1:]
    if len(hex_part) not in (3, 6):
        return False

    # Check if all characters are valid hex
    try:
        int(hex_part, 16)
        return True
    except ValueError:
        return False


def parse_rgb_color(color_str: str) -> Optional[tuple]:
    """Parse RGB color string to (r, g, b) tuple"""
    if not validate_rgb_color(color_str):
        return None

    hex_part = color_str[1:]

    if len(hex_part) == 3:
        # Short format: #RGB -> #RRGGBB
        hex_part = ''.join([c*2 for c in hex_part])

    try:
        r = int(hex_part[0:2], 16)
        g = int(hex_part[2:4], 16)
        b = int(hex_part[4:6], 16)
        return (r, g, b)
    except ValueError:
        return None


def is_weekend(dt: Optional[datetime] = None) -> bool:
    """Check if given datetime is a weekend"""
    if dt is None:
        dt = datetime.now()
    return dt.weekday() >= 5  # Saturday=5, Sunday=6


def is_business_hours(dt: Optional[datetime] = None, start_hour: int = 9, end_hour: int = 17) -> bool:
    """Check if given datetime is within business hours"""
    if dt is None:
        dt = datetime.now()

    return start_hour <= dt.hour < end_hour


def get_time_of_day() -> str:
    """Get descriptive time of day"""
    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def calculate_workday_completion() -> float:
    """Calculate percentage of workday completed (0.0 to 1.0)"""
    now = datetime.now()
    work_start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    work_end = now.replace(hour=17, minute=0, second=0, microsecond=0)

    if now < work_start:
        return 0.0
    if now > work_end:
        return 1.0

    work_duration = (work_end - work_start).total_seconds()
    elapsed = (now - work_start).total_seconds()

    return elapsed / work_duration


def debounce(func, wait_seconds: float = 0.3):
    """Decorator to debounce function calls"""
    import threading

    last_called = [0]
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        with lock:
            current_time = time.time()
            if current_time - last_called[0] < wait_seconds:
                return None
            last_called[0] = current_time
            return func(*args, **kwargs)

    return wrapper


def throttle(func, wait_seconds: float = 1.0):
    """Decorator to throttle function calls"""
    import threading

    last_called = [0]
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        with lock:
            current_time = time.time()
            if current_time - last_called[0] >= wait_seconds:
                last_called[0] = current_time
                return func(*args, **kwargs)
            return None

    return wrapper


def retry_on_exception(max_attempts: int = 3, delay_seconds: float = 1.0):
    """Decorator to retry function on exception"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay_seconds)
                    continue

            # Re-raise the last exception
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def get_memory_usage_mb() -> float:
    """Get current process memory usage in MB"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        # Fallback: try to read from /proc/self/status on Linux
        try:
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        # Extract memory in KB and convert to MB
                        kb = int(line.split()[1])
                        return kb / 1024
        except (FileNotFoundError, ValueError):
            pass
    except Exception:
        pass

    return 0.0


def setup_signal_handlers(cleanup_callback):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        if cleanup_callback:
            cleanup_callback()
        sys.exit(0)

    # Register common signals
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, signal_handler)


def create_temp_file(content: str, suffix: str = ".tmp") -> Path:
    """Create temporary file with content"""
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return Path(f.name)


def load_json_file(file_path: Union[str, Path], default: Any = None) -> Any:
    """Load JSON file with error handling"""
    try:
        path = Path(file_path)
        if not path.exists():
            return default

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return default


def save_json_file(file_path: Union[str, Path], data: Any, indent: int = 2) -> bool:
    """Save data to JSON file with error handling"""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except (TypeError, PermissionError) as e:
        print(f"Error saving JSON file {file_path}: {e}")
        return False


def clamp_value(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Union[int, float]:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(start: Union[int, float], end: Union[int, float], t: float) -> float:
    """Linear interpolation between start and end"""
    return start + (end - start) * clamp_value(t, 0.0, 1.0)


def ease_in_out(t: float) -> float:
    """Ease-in-out easing function"""
    return t * t * (3.0 - 2.0 * t)


def generate_session_id() -> str:
    """Generate unique session ID"""
    import uuid
    return str(uuid.uuid4())[:8].upper()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"