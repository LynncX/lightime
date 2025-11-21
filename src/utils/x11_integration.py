"""
X11 integration utilities for Lightime Pomodoro Timer
"""

import os
import subprocess
import tempfile
from typing import Optional, Tuple, List
from pathlib import Path


class X11Integration:
    """X11 system integration utilities"""

    def __init__(self):
        self._display_server = self._detect_display_server()
        self._xdotool_available = self._check_xdotool()
        self._dbus_available = self._check_dbus()

    def _detect_display_server(self) -> str:
        """Detect the current display server (X11 or Wayland)"""
        # Check XDG_SESSION_TYPE
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        if session_type in ['wayland', 'x11']:
            return session_type

        # Check WAYLAND_DISPLAY
        if os.environ.get('WAYLAND_DISPLAY'):
            return 'wayland'

        # Check DISPLAY
        if os.environ.get('DISPLAY'):
            return 'x11'

        # Fallback to X11
        return 'x11'

    def _check_xdotool(self) -> bool:
        """Check if xdotool is available"""
        try:
            result = subprocess.run(
                ['which', 'xdotool'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_dbus(self) -> bool:
        """Check if D-Bus is available"""
        try:
            result = subprocess.run(
                ['which', 'dbus-send'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @property
    def is_x11(self) -> bool:
        """Check if running on X11"""
        return self._display_server == 'x11'

    @property
    def is_wayland(self) -> bool:
        """Check if running on Wayland"""
        return self._display_server == 'wayland'

    @property
    def can_send_keys(self) -> bool:
        """Check if key sending is supported"""
        return self._xdotool_available and (self.is_x11 or self._xdotool_available)

    def lock_screen(self) -> bool:
        """Lock the screen using Super+L"""
        try:
            if self._xdotool_available:
                # Try xdotool first (works on both X11 and Wayland with xdotool)
                result = subprocess.run(
                    ['xdotool', 'key', 'Super+L'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return True

            # Fallback: Try loginctl (systemd)
            try:
                result = subprocess.run(
                    ['loginctl', 'lock-session'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return True
            except FileNotFoundError:
                pass

            # Fallback: Try gnome-screensaver
            try:
                result = subprocess.run(
                    ['gnome-screensaver-command', '-l'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return True
            except FileNotFoundError:
                pass

            return False

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error locking screen: {e}")
            return False

    def send_keys(self, keys: str) -> bool:
        """Send key combination using xdotool"""
        if not self._xdotool_available:
            return False

        try:
            result = subprocess.run(
                ['xdotool', 'key', keys],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error sending keys '{keys}': {e}")
            return False

    def get_active_window_info(self) -> Optional[dict]:
        """Get information about the currently active window"""
        if not self._xdotool_available or not self.is_x11:
            return None

        try:
            # Get active window ID
            result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return None

            window_id = result.stdout.strip()

            # Get window name
            result = subprocess.run(
                ['xdotool', 'getwindowname', window_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            window_name = result.stdout.strip() if result.returncode == 0 else ""

            # Get window class (requires xprop)
            window_class = ""
            try:
                result = subprocess.run(
                    ['xprop', '-id', window_id, 'WM_CLASS'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Parse WM_CLASS output
                    for line in result.stdout.split('\n'):
                        if 'WM_CLASS' in line:
                            # Extract class name from format: WM_CLASS(STRING) = "class", "class"
                            if '=' in line:
                                class_part = line.split('=')[1].strip()
                                parts = [p.strip().strip('"') for p in class_part.split(',')]
                                window_class = parts[0] if parts else ""
                                break
            except FileNotFoundError:
                pass  # xprop not available

            return {
                'window_id': window_id,
                'window_name': window_name,
                'window_class': window_class
            }

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error getting active window info: {e}")
            return None

    def set_window_above(self, window_id: Optional[str] = None) -> bool:
        """Set window to stay always on top"""
        if not self.is_x11:
            return False

        try:
            if window_id is None:
                # Get current active window
                result = subprocess.run(
                    ['xdotool', 'getactivewindow'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False
                window_id = result.stdout.strip()

            # Set window above all others
            result = subprocess.run(
                ['xdotool', 'windowraise', window_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error setting window above: {e}")
            return False

    def get_screen_resolution(self) -> Optional[Tuple[int, int]]:
        """Get screen resolution"""
        try:
            if self.is_x11 and self._xdotool_available:
                # Try xdotool to get screen geometry
                result = subprocess.run(
                    ['xdotool', 'getdisplaygeometry'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    parts = result.stdout.strip().split()
                    if len(parts) == 2:
                        return int(parts[0]), int(parts[1])

            # Fallback: Try xrandr
            result = subprocess.run(
                ['xrandr'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse xrandr output for current resolution
                for line in result.stdout.split('\n'):
                    if '*' in line and 'connected' in line:
                        # Extract resolution from line like: "1920x1080+0+0     1920x1080"
                        parts = line.split()
                        for part in parts:
                            if 'x' in part and '+' in part:
                                resolution = part.split('+')[0]
                                width_height = resolution.split('x')
                                if len(width_height) == 2:
                                    return int(width_height[0]), int(width_height[1])

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error getting screen resolution: {e}")

        return None

    def show_desktop_notification(
        self,
        title: str,
        message: str,
        urgency: str = "normal",
        timeout: int = 5000
    ) -> bool:
        """Show desktop notification"""
        try:
            # Try notify-send first
            try:
                cmd = ['notify-send', '-u', urgency, '-t', str(timeout), title, message]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return True
            except FileNotFoundError:
                pass

            # Fallback: Try D-Bus directly
            if self._dbus_available:
                notification_script = f"""
                dbus-send --session --dest=org.freedesktop.Notifications \\
                    --type=method_call --print-reply \\
                    /org/freedesktop/Notifications \\
                    org.freedesktop.Notifications.Notify \\
                    string:"Lightime" uint32:0 string:"{title}" \\
                    string:"" string:"{message}" array:string:"" \\
                    dict:string:string:"" int32:{timeout}
                """
                result = subprocess.run(
                    ['bash', '-c', notification_script],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.returncode == 0

            return False

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error showing notification: {e}")
            return False

    def get_system_info(self) -> dict:
        """Get system information relevant to Lightime"""
        info = {
            'display_server': self._display_server,
            'xdotool_available': self._xdotool_available,
            'dbus_available': self._dbus_available,
            'can_send_keys': self.can_send_keys,
            'environment_variables': {
                'DISPLAY': os.environ.get('DISPLAY'),
                'WAYLAND_DISPLAY': os.environ.get('WAYLAND_DISPLAY'),
                'XDG_SESSION_TYPE': os.environ.get('XDG_SESSION_TYPE'),
                'XDG_CURRENT_DESKTOP': os.environ.get('XDG_CURRENT_DESKTOP'),
            }
        }

        # Get screen resolution if possible
        resolution = self.get_screen_resolution()
        if resolution:
            info['screen_resolution'] = {
                'width': resolution[0],
                'height': resolution[1]
            }

        # Get active window info if possible
        if self.is_x11:
            active_window = self.get_active_window_info()
            if active_window:
                info['active_window'] = active_window

        return info

    def test_functionality(self) -> dict:
        """Test various X11 integration features"""
        results = {
            'display_server': self._display_server,
            'xdotool_available': self._xdotool_available,
            'dbus_available': self._dbus_available,
            'screen_resolution': self.get_screen_resolution() is not None,
            'active_window_info': self.get_active_window_info() is not None,
            'notifications': False,
            'key_sending': False
        }

        # Test notifications
        results['notifications'] = self.show_desktop_notification(
            "Lightime Test",
            "Testing X11 integration functionality",
            urgency="low",
            timeout=2000
        )

        # Test key sending (with a harmless key)
        if self._xdotool_available:
            results['key_sending'] = self.send_keys('F15')  # F15 is typically unused

        return results
