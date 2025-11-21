"""
Main GUI application for Lightime Pomodoro Timer
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gio', '2.0')

import threading
from typing import Optional

from gi.repository import Gtk, Gdk, Gio

from ..app_context import ApplicationContext
from ..utils.error_handling import handle_error, ErrorSeverity, ErrorCategory
from .timer_window import TimerWindow
from .tray_icon import TrayIcon


class LightimeApplication(Gtk.Application):
    """Main GTK application for Lightime"""

    def __init__(self, app_context: ApplicationContext):
        super().__init__(
            application_id="com.lightime.timer",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        self.app_context = app_context
        self.config = app_context.config

        # GUI components
        self.timer_window: Optional[TimerWindow] = None
        self.tray_icon: Optional[TrayIcon] = None

        # Application state
        self._initialized = False

        # Setup signal handlers
        self.connect("activate", self._on_activate)
        self.connect("shutdown", self._on_shutdown)

    def do_activate(self) -> None:
        """Handle application activation"""
        self._on_activate()

    def _on_activate(self, *args) -> None:
        """Initialize GUI components"""
        if self._initialized:
            return

        try:
            # Create tray icon first (may fail on some systems)
            self.tray_icon = TrayIcon(self.app_context)

            # Create main timer window
            self.timer_window = TimerWindow(self.app_context)
            self.timer_window.connect("delete-event", self._on_window_delete)

            # Show window initially (can be hidden via tray)
            self.timer_window.show_all()

            # Update tray icon with window visibility
            if self.tray_icon.is_available:
                self.tray_icon.update_window_visibility(True)

            self._initialized = True

            # Log successful GUI initialization
            print("Lightime GUI application initialized successfully")

        except Exception as e:
            handle_error(
                exception=e,
                message="Failed to initialize GUI application",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.GUI
            )
            self._quit_application()

    def _on_window_delete(self, window, event) -> bool:
        """Handle window close event"""
        # Hide window instead of closing if tray is available
        if self.tray_icon and self.tray_icon.is_available:
            window.hide()
            if self.tray_icon:
                self.tray_icon.update_window_visibility(False)
            return True  # Prevent window destruction
        else:
            # No tray available, so quit application
            self._quit_application()
            return False

    def _on_shutdown(self, application) -> None:
        """Handle application shutdown"""
        self._cleanup()

    def _cleanup(self) -> None:
        """Cleanup GUI components"""
        try:
            # Cleanup timer window
            if self.timer_window:
                self.timer_window.cleanup()
                self.timer_window.destroy()
                self.timer_window = None

            # Cleanup tray icon
            if self.tray_icon:
                self.tray_icon.cleanup()
                self.tray_icon = None

            print("GUI application cleanup completed")

        except Exception as e:
            handle_error(
                exception=e,
                message="Error during GUI cleanup",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.GUI
            )

    def _quit_application(self) -> None:
        """Quit the application"""
        try:
            # Cancel any active session
            timer_engine = self.app_context.timer_engine
            if timer_engine.has_active_session:
                timer_engine.cancel_session()

            # Shutdown application context
            from ..app_context import shutdown_app
            shutdown_app()

            # Quit application
            self.quit()

        except Exception as e:
            handle_error(
                exception=e,
                message="Error quitting application",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def show_window(self) -> None:
        """Show the timer window"""
        if self.timer_window:
            self.timer_window.show()
            self.timer_window.present()
            if self.tray_icon:
                self.tray_icon.update_window_visibility(True)

    def hide_window(self) -> None:
        """Hide the timer window"""
        if self.timer_window:
            self.timer_window.hide()
            if self.tray_icon:
                self.tray_icon.update_window_visibility(False)

    def toggle_window_visibility(self) -> None:
        """Toggle timer window visibility"""
        if self.timer_window:
            if self.timer_window.get_visible():
                self.hide_window()
            else:
                self.show_window()

    def run_gui(self) -> int:
        """Run the GUI application"""
        try:
            # Start the application context
            if not self.app_context.start():
                return 1

            # Run GTK main loop
            return self.run()

        except Exception as e:
            handle_error(
                exception=e,
                message="Error running GUI application",
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.GUI
            )
            return 1
        finally:
            # Ensure cleanup
            self._cleanup()


class GUIManager:
    """High-level GUI manager"""

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context
        self.application: Optional[LightimeApplication] = None

    def initialize(self) -> bool:
        """Initialize GUI manager"""
        try:
            self.application = LightimeApplication(self.app_context)
            return True

        except Exception as e:
            handle_error(
                exception=e,
                message="Failed to initialize GUI manager",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.GUI
            )
            return False

    def run(self) -> int:
        """Run the GUI application"""
        if not self.application:
            if not self.initialize():
                return 1

        return self.application.run_gui()

    def show_window(self) -> None:
        """Show the timer window"""
        if self.application:
            self.application.show_window()

    def hide_window(self) -> None:
        """Hide the timer window"""
        if self.application:
            self.application.hide_window()

    def toggle_window(self) -> None:
        """Toggle timer window visibility"""
        if self.application:
            self.application.toggle_window_visibility()

    def cleanup(self) -> None:
        """Cleanup GUI manager"""
        if self.application:
            self.application._cleanup()
            self.application = None

    @property
    def is_running(self) -> bool:
        """Check if GUI is running"""
        return self.application is not None and self.application._initialized
