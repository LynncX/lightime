"""
System tray icon for Lightime Pomodoro Timer
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from typing import Optional
from gi.repository import Gtk, GdkPixbuf

try:
    from gi.repository import AppIndicator3
    APPINDICATOR_AVAILABLE = True
except ImportError:
    APPINDICATOR_AVAILABLE = False

from ..app_context import ApplicationContext
from ..models.session import SessionStatus, SessionType
from ..utils.error_handling import handle_error, ErrorSeverity, ErrorCategory


class TrayIcon:
    """System tray icon for Lightime"""

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context
        self.config = app_context.config

        # Initialize indicator
        self.indicator = None
        self.menu = None
        self.initialized = False

        # Try to initialize tray icon
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the tray icon"""
        if not APPINDICATOR_AVAILABLE:
            print("AppIndicator3 not available, tray icon disabled")
            return

        try:
            # Create app indicator
            self.indicator = AppIndicator3.Indicator.new(
                "lightime",
                "alarm-clock",  # Default icon theme name
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )

            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_attention_icon("alarm-clock-symbolic")

            # Create context menu
            self._create_menu()

            # Subscribe to timer events
            self._setup_event_handlers()

            self.initialized = True

        except Exception as e:
            handle_error(
                exception=e,
                message="Error initializing tray icon",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _create_menu(self) -> None:
        """Create context menu for tray icon"""
        self.menu = Gtk.Menu()

        # Timer status item
        self.status_item = Gtk.MenuItem(label="Ready")
        self.status_item.set_sensitive(False)
        self.menu.append(self.status_item)

        # Separator
        separator1 = Gtk.SeparatorMenuItem()
        self.menu.append(separator1)

        # Timer control items
        self.start_item = Gtk.MenuItem(label="Start Timer")
        self.start_item.connect("activate", self._on_start_clicked)
        self.menu.append(self.start_item)

        self.pause_item = Gtk.MenuItem(label="Pause Timer")
        self.pause_item.connect("activate", self._on_pause_clicked)
        self.pause_item.set_sensitive(False)
        self.menu.append(self.pause_item)

        self.stop_item = Gtk.MenuItem(label="Stop Timer")
        self.stop_item.connect("activate", self._on_stop_clicked)
        self.stop_item.set_sensitive(False)
        self.menu.append(self.stop_item)

        # Separator
        separator2 = Gtk.SeparatorMenuItem()
        self.menu.append(separator2)

        # Quick preset timers
        self._create_preset_items()

        # Separator
        separator3 = Gtk.SeparatorMenuItem()
        self.menu.append(separator3)

        # Show/Hide window
        self.show_window_item = Gtk.MenuItem(label="Show Timer")
        self.show_window_item.connect("activate", self._on_show_window_clicked)
        self.menu.append(self.show_window_item)

        # Separator
        separator4 = Gtk.SeparatorMenuItem()
        self.menu.append(separator4)

        # Settings
        settings_item = Gtk.MenuItem(label="Settings")
        settings_item.connect("activate", self._on_settings_clicked)
        self.menu.append(settings_item)

        # Session history
        history_item = Gtk.MenuItem(label="Session History")
        history_item.connect("activate", self._on_history_clicked)
        self.menu.append(history_item)

        # Separator
        separator5 = Gtk.SeparatorMenuItem()
        self.menu.append(separator5)

        # Quit
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self._on_quit_clicked)
        self.menu.append(quit_item)

        self.menu.show_all()

        # Set menu for indicator
        if self.indicator:
            self.indicator.set_menu(self.menu)

    def _create_preset_items(self) -> None:
        """Create preset timer menu items"""
        preset_submenu = Gtk.Menu()

        for duration in self.config.preset_durations:
            item = Gtk.MenuItem(label=f"{duration} minutes")
            item.connect("activate", self._on_preset_clicked, duration)
            preset_submenu.append(item)

        preset_submenu.show_all()

        preset_item = Gtk.MenuItem(label="Quick Timers")
        preset_item.set_submenu(preset_submenu)
        self.menu.append(preset_item)

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for timer engine events"""
        timer_engine = self.app_context.timer_engine

        # Subscribe to timer events
        from ..timer.engine import TimerEvent

        timer_engine.add_event_handler(TimerEvent.SESSION_STARTED, self._on_session_started)
        timer_engine.add_event_handler(TimerEvent.SESSION_PAUSED, self._on_session_paused)
        timer_engine.add_event_handler(TimerEvent.SESSION_RESUMED, self._on_session_resumed)
        timer_engine.add_event_handler(TimerEvent.SESSION_COMPLETED, self._on_session_completed)
        timer_engine.add_event_handler(TimerEvent.SESSION_CANCELLED, self._on_session_cancelled)
        timer_engine.add_event_handler(TimerEvent.WARNING_TRIGGERED, self._on_warning_triggered)
        timer_engine.add_event_handler(TimerEvent.TIME_UPDATED, self._on_time_updated)

    def _on_start_clicked(self, menu_item) -> None:
        """Handle start menu item click"""
        try:
            timer_engine = self.app_context.timer_engine

            if timer_engine.has_active_session:
                # Resume paused session
                timer_engine.resume_session()
            else:
                # Start new session
                timer_engine.start_session(
                    duration_minutes=self.config.default_duration,
                    session_type=SessionType.WORK
                )
        except Exception as e:
            handle_error(
                exception=e,
                message="Error starting timer from tray",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _on_pause_clicked(self, menu_item) -> None:
        """Handle pause menu item click"""
        try:
            self.app_context.timer_engine.pause_session()
        except Exception as e:
            handle_error(
                exception=e,
                message="Error pausing timer from tray",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _on_stop_clicked(self, menu_item) -> None:
        """Handle stop menu item click"""
        try:
            self.app_context.timer_engine.cancel_session()
        except Exception as e:
            handle_error(
                exception=e,
                message="Error stopping timer from tray",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _on_preset_clicked(self, menu_item, duration: int) -> None:
        """Handle preset menu item click"""
        try:
            timer_engine = self.app_context.timer_engine

            # Cancel existing session if any
            if timer_engine.has_active_session:
                timer_engine.cancel_session()

            # Start new session with preset duration
            timer_engine.start_session(
                duration_minutes=duration,
                session_type=SessionType.WORK
            )
        except Exception as e:
            handle_error(
                exception=e,
                message="Error starting preset timer from tray",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _on_show_window_clicked(self, menu_item) -> None:
        """Handle show window menu item click"""
        try:
            # Get or create timer window
            timer_window = getattr(self.app_context, 'timer_window', None)
            if timer_window:
                if timer_window.get_visible():
                    timer_window.hide()
                    self.show_window_item.set_label("Show Timer")
                else:
                    timer_window.show()
                    timer_window.present()
                    self.show_window_item.set_label("Hide Timer")
            else:
                self.show_window_item.set_label("Show Timer")
        except Exception as e:
            handle_error(
                exception=e,
                message="Error showing timer window",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.GUI
            )

    def _on_settings_clicked(self, menu_item) -> None:
        """Handle settings menu item click"""
        try:
            # TODO: Implement settings dialog
            print("Settings dialog not implemented yet")
        except Exception as e:
            handle_error(
                exception=e,
                message="Error opening settings",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.GUI
            )

    def _on_history_clicked(self, menu_item) -> None:
        """Handle history menu item click"""
        try:
            # TODO: Implement history dialog
            print("History dialog not implemented yet")
        except Exception as e:
            handle_error(
                exception=e,
                message="Error opening history",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.GUI
            )

    def _on_quit_clicked(self, menu_item) -> None:
        """Handle quit menu item click"""
        try:
            # Cancel any active session
            timer_engine = self.app_context.timer_engine
            if timer_engine.has_active_session:
                timer_engine.cancel_session()

            # Shutdown application
            from ..app_context import shutdown_app
            shutdown_app()

            # Quit GTK main loop if running
            Gtk.main_quit()

        except Exception as e:
            handle_error(
                exception=e,
                message="Error quitting application",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _on_session_started(self, data: dict) -> None:
        """Handle session started event"""
        import GLib
        GLib.idle_add(self._update_status)

    def _on_session_paused(self, data: dict) -> None:
        """Handle session paused event"""
        import GLib
        GLib.idle_add(self._update_status)

    def _on_session_resumed(self, data: dict) -> None:
        """Handle session resumed event"""
        import GLib
        GLib.idle_add(self._update_status)

    def _on_session_completed(self, data: dict) -> None:
        """Handle session completed event"""
        import GLib
        GLib.idle_add(self._update_status)
        GLib.idle_add(self._reset_indicator)

    def _on_session_cancelled(self, data: dict) -> None:
        """Handle session cancelled event"""
        import GLib
        GLib.idle_add(self._update_status)
        GLib.idle_add(self._reset_indicator)

    def _on_warning_triggered(self, data: dict) -> None:
        """Handle warning triggered event"""
        import GLib
        GLib.idle_add(self._set_attention_indicator)

    def _on_time_updated(self, data: dict) -> None:
        """Handle time update event"""
        # Update status periodically (not every second to avoid overwhelming)
        pass

    def _update_status(self) -> None:
        """Update tray icon status and menu items"""
        if not self.initialized:
            return

        timer_engine = self.app_context.timer_engine

        if timer_engine.has_active_session:
            session = timer_engine.active_session

            # Update status text
            if session.is_paused:
                status_text = "Paused"
            elif session.record.warning_triggered:
                status_text = "Warning!"
            else:
                remaining_minutes = int(session.remaining_time.total_seconds() / 60)
                remaining_seconds = int(session.remaining_time.total_seconds() % 60)
                status_text = f"{remaining_minutes:02d}:{remaining_seconds:02d}"

            self.status_item.set_label(f"Timer: {status_text}")

            # Update menu item states
            self.start_item.set_sensitive(session.is_paused)
            self.start_item.set_label("Resume" if session.is_paused else "Running")
            self.pause_item.set_sensitive(not session.is_paused)
            self.stop_item.set_sensitive(True)

            # Update tooltip
            if self.indicator:
                progress_percent = (session.elapsed_time.total_seconds() / (session.record.duration_minutes * 60)) * 100
                tooltip = f"Lightime - {session.record.session_type.value.title()}: {status_text} ({progress_percent:.0f}%)"
                self.indicator.set_title(tooltip)

        else:
            # No active session
            self.status_item.set_label("Ready")

            # Update menu item states
            self.start_item.set_sensitive(True)
            self.start_item.set_label("Start Timer")
            self.pause_item.set_sensitive(False)
            self.stop_item.set_sensitive(False)

            # Update tooltip
            if self.indicator:
                self.indicator.set_title("Lightime - Ready")

    def _set_attention_indicator(self) -> None:
        """Set indicator to attention state"""
        if self.initialized and self.indicator:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ATTENTION)

    def _reset_indicator(self) -> None:
        """Reset indicator to active state"""
        if self.initialized and self.indicator:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

    def update_window_visibility(self, visible: bool) -> None:
        """Update show/hide window menu item"""
        if self.initialized and self.show_window_item:
            self.show_window_item.set_label("Hide Timer" if visible else "Show Timer")

    def cleanup(self) -> None:
        """Cleanup resources"""
        if self.initialized and self.indicator:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)

        # Clear event handlers
        if hasattr(self, '_setup_event_handlers'):
            # Would need to implement unsubscribe functionality
            pass

        self.initialized = False

    @property
    def is_available(self) -> bool:
        """Check if tray icon is available and initialized"""
        return APPINDICATOR_AVAILABLE and self.initialized