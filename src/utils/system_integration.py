"""
System integration utilities for Lightime Pomodoro Timer
"""

import os
import subprocess
import tempfile
import platform
import logging
from typing import Optional, Dict, List, Any, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .x11_integration import X11Integration
from ..models.config import LightimeConfig


class DesktopEnvironment(Enum):
    """Supported desktop environments"""
    GNOME = "gnome"
    KDE = "kde"
    XFCE = "xfce"
    MATE = "mate"
    CINNAMON = "cinnamon"
    UNITY = "unity"
    LXDE = "lxde"
    LXQT = "lxqt"
    UNKNOWN = "unknown"


class NotificationLevel(Enum):
    """Notification urgency levels"""
    LOW = "low"
    NORMAL = "normal"
    CRITICAL = "critical"


@dataclass
class SystemInfo:
    """System information"""
    platform: str
    platform_release: str
    platform_version: str
    architecture: str
    hostname: str
    processor: str
    desktop_environment: DesktopEnvironment
    x11_integration: bool
    wayland_support: bool
    python_version: str


class SystemIntegration:
    """System integration utilities for Lightime"""

    def __init__(self):
        self.x11_integration = X11Integration()
        self.logger = logging.getLogger(__name__)
        self._system_info = self._gather_system_info()
        self._notification_methods = self._detect_notification_methods()
        self._lock_methods = self._detect_lock_methods()

    @property
    def system_info(self) -> SystemInfo:
        """Get system information"""
        return self._system_info

    def _gather_system_info(self) -> SystemInfo:
        """Gather comprehensive system information"""
        import socket

        # Basic platform info
        platform_system = platform.system()
        platform_release = platform.release()
        platform_version = platform.version()
        architecture = platform.machine()
        hostname = socket.gethostname()
        processor = platform.processor()

        # Desktop environment detection
        desktop_env = self._detect_desktop_environment()

        # X11/Wayland support
        x11_available = self.x11_integration.is_x11
        wayland_available = self.x11_integration.is_wayland

        # Python version
        python_version = platform.python_version()

        return SystemInfo(
            platform=platform_system,
            platform_release=platform_release,
            platform_version=platform_version,
            architecture=architecture,
            hostname=hostname,
            processor=processor,
            desktop_environment=desktop_env,
            x11_integration=x11_available,
            wayland_support=wayland_available,
            python_version=python_version
        )

    def _detect_desktop_environment(self) -> DesktopEnvironment:
        """Detect the current desktop environment"""
        # Check XDG_CURRENT_DESKTOP
        xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        if xdg_desktop:
            for env in DesktopEnvironment:
                if env.value in xdg_desktop:
                    return env

        # Check other environment variables
        if os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            return DesktopEnvironment.GNOME
        if os.environ.get('KDE_FULL_SESSION'):
            return DesktopEnvironment.KDE
        if os.environ.get('XFCE4_SESSION'):
            return DesktopEnvironment.XFCE
        if os.environ.get('MATE_DESKTOP_SESSION_ID'):
            return DesktopEnvironment.MATE

        return DesktopEnvironment.UNKNOWN

    def _detect_notification_methods(self) -> List[str]:
        """Detect available notification methods"""
        methods = []

        # Check for notify-send
        try:
            subprocess.run(
                ['which', 'notify-send'],
                capture_output=True,
                check=True,
                timeout=5
            )
            methods.append('notify-send')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Check for D-Bus
        if self.x11_integration._dbus_available:
            methods.append('dbus')

        # Check for libnotify
        try:
            import gi
            gi.require_version('Notify', '0.7')
            from gi.repository import Notify
            methods.append('libnotify')
        except (ImportError, ValueError):
            pass

        return methods

    def _detect_lock_methods(self) -> List[str]:
        """Detect available screen lock methods"""
        methods = []

        # Check for loginctl (systemd)
        try:
            subprocess.run(
                ['which', 'loginctl'],
                capture_output=True,
                check=True,
                timeout=5
            )
            methods.append('loginctl')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Check for gnome-screensaver
        try:
            subprocess.run(
                ['which', 'gnome-screensaver-command'],
                capture_output=True,
                check=True,
                timeout=5
            )
            methods.append('gnome-screensaver')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Check for xscreensaver
        try:
            subprocess.run(
                ['which', 'xscreensaver-command'],
                capture_output=True,
                check=True,
                timeout=5
            )
            methods.append('xscreensaver')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # xdotool (works for keyboard-based locking)
        if self.x11_integration.can_send_keys:
            methods.append('xdotool')

        return methods

    def show_notification(
        self,
        title: str,
        message: str,
        level: NotificationLevel = NotificationLevel.NORMAL,
        timeout: int = 5000,
        icon_path: Optional[str] = None
    ) -> bool:
        """Show desktop notification"""
        # Try different notification methods in order of preference
        for method in self._notification_methods:
            try:
                if method == 'libnotify':
                    return self._notify_libnotify(title, message, level, timeout, icon_path)
                elif method == 'notify-send':
                    return self._notify_send(title, message, level, timeout, icon_path)
                elif method == 'dbus':
                    return self._notify_dbus(title, message, level, timeout)
            except Exception as e:
                self.logger.warning(f"Notification method {method} failed: {e}")
                continue

        return False

    def _notify_libnotify(
        self,
        title: str,
        message: str,
        level: NotificationLevel,
        timeout: int,
        icon_path: Optional[str]
    ) -> bool:
        """Show notification using libnotify"""
        try:
            import gi
            gi.require_version('Notify', '0.7')
            from gi.repository import Notify

            # Initialize notification system
            Notify.init("Lightime")

            notification = Notify.Notification.new(title, message, icon_path or "")
            notification.set_urgency(level.value)

            if timeout > 0:
                notification.set_timeout(timeout)

            return notification.show()

        except Exception as e:
            self.logger.error(f"Libnotify error: {e}")
            return False

    def _notify_send(
        self,
        title: str,
        message: str,
        level: NotificationLevel,
        timeout: int,
        icon_path: Optional[str]
    ) -> bool:
        """Show notification using notify-send"""
        cmd = ['notify-send', '-u', level.value, '-t', str(timeout)]

        if icon_path:
            cmd.extend(['-i', icon_path])

        cmd.extend([title, message])

        try:
            subprocess.run(cmd, check=True, timeout=10)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"notify-send error: {e}")
            return False

    def _notify_dbus(
        self,
        title: str,
        message: str,
        level: NotificationLevel,
        timeout: int
    ) -> bool:
        """Show notification using D-Bus"""
        urgency_map = {
            NotificationLevel.LOW: 0,
            NotificationLevel.NORMAL: 1,
            NotificationLevel.CRITICAL: 2
        }

        notification_script = f"""
        dbus-send --session --dest=org.freedesktop.Notifications \\
            --type=method_call --print-reply \\
            /org/freedesktop/Notifications \\
            org.freedesktop.Notifications.Notify \\
            string:"Lightime" uint32:0 string:"{title}" \\
            string:"" string:"{message}" array:string:"" \\
            dict:string:string:"urgency":"byte:{urgency_map[level]}" \\
            int32:{timeout}
        """

        try:
            subprocess.run(['bash', '-c', notification_script], check=True, timeout=10)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"D-Bus notification error: {e}")
            return False

    def lock_screen(self) -> bool:
        """Lock the screen using available method"""
        # Try different lock methods in order of preference
        for method in self._lock_methods:
            try:
                if method == 'loginctl':
                    return subprocess.run(
                        ['loginctl', 'lock-session'],
                        check=True,
                        timeout=10
                    ).returncode == 0
                elif method == 'gnome-screensaver':
                    return subprocess.run(
                        ['gnome-screensaver-command', '-l'],
                        check=True,
                        timeout=10
                    ).returncode == 0
                elif method == 'xscreensaver':
                    return subprocess.run(
                        ['xscreensaver-command', '-lock'],
                        check=True,
                        timeout=10
                    ).returncode == 0
                elif method == 'xdotool':
                    return self.x11_integration.lock_screen()

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                self.logger.warning(f"Lock method {method} failed: {e}")
                continue

        return False

    def send_key_combination(self, keys: str) -> bool:
        """Send key combination using available method"""
        return self.x11_integration.send_keys(keys)

    def set_window_properties(
        self,
        window_id: Optional[str] = None,
        always_on_top: bool = False,
        skip_taskbar: bool = False,
        sticky: bool = False
    ) -> bool:
        """Set window properties (X11 only)"""
        if not self.x11_integration.is_x11:
            return False

        try:
            if window_id is None:
                result = subprocess.run(
                    ['xdotool', 'getactivewindow'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False
                window_id = result.stdout.strip()

            # Set always on top
            if always_on_top:
                self.x11_integration.set_window_above(window_id)

            # Additional window properties would require wmctrl or similar
            # This is a basic implementation

            return True

        except Exception as e:
            self.logger.error(f"Error setting window properties: {e}")
            return False

    def get_application_info(self) -> Dict[str, Any]:
        """Get application and integration information"""
        return {
            'system_info': {
                'platform': self._system_info.platform,
                'desktop_environment': self._system_info.desktop_environment.value,
                'x11_available': self._system_info.x11_integration,
                'wayland_available': self._system_info.wayland_support,
                'python_version': self._system_info.python_version
            },
            'integration_features': {
                'notifications_available': len(self._notification_methods) > 0,
                'notification_methods': self._notification_methods,
                'screen_lock_available': len(self._lock_methods) > 0,
                'lock_methods': self._lock_methods,
                'key_sending_available': self.x11_integration.can_send_keys
            },
            'x11_details': self.x11_integration.get_system_info()
        }

    def test_integration(self) -> Dict[str, bool]:
        """Test system integration features"""
        results = {
            'notifications': self.show_notification(
                "Lightime Test",
                "Testing system integration",
                level=NotificationLevel.LOW,
                timeout=2000
            ),
            'screen_lock': False,  # Don't actually lock screen during test
            'key_sending': False,  # Don't send keys during test
            'x11_integration': self.x11_integration.is_x11,
            'wayland_support': self.x11_integration.is_wayland
        }

        # Test key sending with a harmless key
        if self.x11_integration.can_send_keys:
            results['key_sending'] = self.x11_integration.send_keys('F15')

        return results

    def create_desktop_entry(self, install_path: Optional[Path] = None) -> bool:
        """Create desktop entry for application"""
        try:
            desktop_dir = Path.home() / ".local" / "share" / "applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)

            desktop_file = desktop_dir / "lightime.desktop"

            # Determine executable path
            if install_path and (install_path / "src" / "main.py").exists():
                exec_path = f"{install_path}/src/main.py"
            else:
                exec_path = "lightime"  # Assume it's in PATH

            desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Lightime
Comment=Lightweight Pomodoro Timer
Exec=python3 {exec_path}
Icon=alarm-clock
Terminal=false
Categories=Office;Utility;Clock;
StartupNotify=true
Keywords=pomodoro;timer;productivity;
"""

            with open(desktop_file, 'w', encoding='utf-8') as f:
                f.write(desktop_content)

            # Make executable
            desktop_file.chmod(0o644)

            self.logger.info(f"Created desktop entry: {desktop_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating desktop entry: {e}")
            return False

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from system"""
        preferences = {}

        # Get user's preferred language
        language = os.environ.get('LANG', 'en_US.UTF-8').split('.')[0]
        preferences['language'] = language

        # Get theme information (GTK)
        try:
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                theme = result.stdout.strip().strip("'\"")
                preferences['gtk_theme'] = theme
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Get icon theme
        try:
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'icon-theme'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                icon_theme = result.stdout.strip().strip("'\"")
                preferences['icon_theme'] = icon_theme
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return preferences