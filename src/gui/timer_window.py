"""
Main timer window for Lightime Pomodoro Timer
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

import threading
import time
from datetime import datetime
from typing import Optional, Callable

from gi.repository import Gtk, Gdk, GLib, Pango

try:
    from ..app_context import ApplicationContext
    from ..models.session import SessionStatus, SessionType
    from ..utils.helpers import format_time_display, calculate_session_progress
    from ..utils.error_handling import handle_error, ErrorSeverity, ErrorCategory
except ImportError:
    # Fallback for module execution
    from src.app_context import ApplicationContext
    from src.models.session import SessionStatus, SessionType
    from src.utils.helpers import format_time_display, calculate_session_progress
    from src.utils.error_handling import handle_error, ErrorSeverity, ErrorCategory


class TimerWindow(Gtk.Window):
    """Main timer window displaying current Pomodoro session"""

    def __init__(self, app_context: ApplicationContext):
        super().__init__(title="Lightime")

        self.app_context = app_context
        self.config = app_context.config

        # Window setup
        self._setup_window()

        # UI components
        self.time_label = None
        self.status_label = None
        self.progress_bar = None
        self.start_button = None
        self.pause_button = None
        self.stop_button = None
        self.preset_buttons = []

        # Create UI
        self._create_ui()

        # Setup timer update
        self.update_timer_id = None

        # Setup event handlers
        self._setup_event_handlers()

        # Apply initial state
        self._update_display()

    def _setup_window(self) -> None:
        """Setup window properties"""
        # Window properties
        self.set_default_size(
            self.config.icon_size.width,
            self.config.icon_size.height
        )

        # Window behavior
        self.set_decorated(False)  # No window decorations
        self.set_skip_taskbar_hint(True)  # Don't show in taskbar
        self.set_skip_pager_hint(True)  # Don't show in pager
        self.set_keep_above(True)  # Always on top
        self.set_accept_focus(False)  # Don't accept focus by default
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)  # Utility window type

        # Window styling
        self.set_app_paintable(True)

        # Visual warning setup
        self._original_opacity = 1.0
        self._warning_active = False
        self._warning_animation_id = None

        # Try to set window properties
        try:
            # Set window above all others (X11 specific)
            if self.app_context.system_integration.x11_integration.is_x11:
                self.app_context.system_integration.x11_integration.set_window_above()
        except Exception as e:
            handle_error(
                exception=e,
                message="Error setting window properties",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.GUI
            )

    def _create_ui(self) -> None:
        """Create the user interface"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        main_box.set_border_width(12)
        self.add(main_box)

        # Time display
        self.time_label = Gtk.Label()
        self.time_label.set_markup("<span size='xx-large' weight='bold'>00:00</span>")
        self.time_label.set_halign(Gtk.Align.CENTER)
        self.time_label.set_valign(Gtk.Align.CENTER)
        main_box.pack_start(self.time_label, True, True, 0)

        # Status display
        self.status_label = Gtk.Label()
        self.status_label.set_markup("<span size='small'>Ready</span>")
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.set_valign(Gtk.Align.CENTER)
        main_box.pack_start(self.status_label, False, False, 0)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_halign(Gtk.Align.FILL)
        self.progress_bar.set_valign(Gtk.Align.CENTER)
        self.progress_bar.set_fraction(0.0)
        main_box.pack_start(self.progress_bar, False, False, 4)

        # Control buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        button_box.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(button_box, False, False, 4)

        # Start button
        self.start_button = Gtk.Button(label="Start")
        self.start_button.connect("clicked", self._on_start_clicked)
        self.start_button.set_sensitive(True)
        button_box.pack_start(self.start_button, False, False, 0)

        # Pause button
        self.pause_button = Gtk.Button(label="Pause")
        self.pause_button.connect("clicked", self._on_pause_clicked)
        self.pause_button.set_sensitive(False)
        button_box.pack_start(self.pause_button, False, False, 0)

        # Stop button
        self.stop_button = Gtk.Button(label="Stop")
        self.stop_button.connect("clicked", self._on_stop_clicked)
        self.stop_button.set_sensitive(False)
        button_box.pack_start(self.stop_button, False, False, 0)

        # Preset buttons
        self._create_preset_buttons(main_box)

        # Apply styling
        self._apply_styling()

        # Show all widgets
        self.show_all()

    def _create_preset_buttons(self, container) -> None:
        """Create preset duration buttons"""
        preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        preset_box.set_halign(Gtk.Align.CENTER)

        for duration in self.config.preset_durations:
            button = Gtk.Button(label=f"{duration}m")
            button.connect("clicked", self._on_preset_clicked, duration)
            preset_box.pack_start(button, False, False, 0)
            self.preset_buttons.append(button)

        container.pack_start(preset_box, False, False, 4)

    def _apply_styling(self) -> None:
        """Apply custom styling to widgets"""
        # Create CSS provider
        css_provider = Gtk.CssProvider()

        # Basic styling
        css = """
        window {
            background-color: #2b2b2b;
            border-radius: 8px;
            border: 1px solid #555;
        }

        button {
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            min-width: 50px;
        }

        button:hover {
            background-color: #4a4a4a;
        }

        button:active {
            background-color: #6a6a6a;
        }

        progressbar {
            border-radius: 2px;
        }

        progressbar trough {
            background-color: #1a1a1a;
            border-radius: 2px;
        }

        progressbar progress {
            background-color: #4CAF50;
            border-radius: 2px;
        }
        """

        css_provider.load_from_data(css.encode('utf-8'))

        # Apply to style context
        style_context = self.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Apply to all child widgets
        self._apply_styling_recursive(self, css_provider)

    def _apply_styling_recursive(self, widget, css_provider) -> None:
        """Recursively apply styling to widget and its children"""
        widget.get_style_context().add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        if hasattr(widget, 'get_children'):
            for child in widget.get_children():
                self._apply_styling_recursive(child, css_provider)

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

    def _on_start_clicked(self, button) -> None:
        """Handle start button click"""
        try:
            if not self.app_context.timer_engine.has_active_session:
                # Start new session with default duration
                self.app_context.timer_engine.start_session(
                    duration_minutes=self.config.default_duration,
                    session_type=SessionType.WORK
                )
            else:
                # Resume paused session
                self.app_context.timer_engine.resume_session()
        except Exception as e:
            handle_error(
                exception=e,
                message="Error starting timer",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _on_pause_clicked(self, button) -> None:
        """Handle pause button click"""
        try:
            self.app_context.timer_engine.pause_session()
        except Exception as e:
            handle_error(
                exception=e,
                message="Error pausing timer",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _on_stop_clicked(self, button) -> None:
        """Handle stop button click"""
        try:
            self.app_context.timer_engine.cancel_session()
        except Exception as e:
            handle_error(
                exception=e,
                message="Error stopping timer",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _on_preset_clicked(self, button, duration: int) -> None:
        """Handle preset button click"""
        try:
            # Cancel existing session if any
            if self.app_context.timer_engine.has_active_session:
                self.app_context.timer_engine.cancel_session()

            # Start new session with preset duration
            self.app_context.timer_engine.start_session(
                duration_minutes=duration,
                session_type=SessionType.WORK
            )
        except Exception as e:
            handle_error(
                exception=e,
                message="Error starting preset timer",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.GUI
            )

    def _on_session_started(self, data: dict) -> None:
        """Handle session started event"""
        GLib.idle_add(self._update_display)

    def _on_session_paused(self, data: dict) -> None:
        """Handle session paused event"""
        GLib.idle_add(self._update_display)

    def _on_session_resumed(self, data: dict) -> None:
        """Handle session resumed event"""
        GLib.idle_add(self._update_display)

    def _on_session_completed(self, data: dict) -> None:
        """Handle session completed event"""
        GLib.idle_add(self._update_display)
        GLib.idle_add(self._stop_warning_animation)

    def _on_session_cancelled(self, data: dict) -> None:
        """Handle session cancelled event"""
        GLib.idle_add(self._update_display)
        GLib.idle_add(self._stop_warning_animation)

    def _on_warning_triggered(self, data: dict) -> None:
        """Handle warning triggered event"""
        GLib.idle_add(self._start_warning_animation)

    def _on_time_updated(self, data: dict) -> None:
        """Handle time update event"""
        GLib.idle_add(self._update_timer_display, data)

    def _update_display(self) -> None:
        """Update the entire display based on current state"""
        timer_engine = self.app_context.timer_engine

        if timer_engine.has_active_session:
            session = timer_engine.active_session
            self._update_timer_display({'elapsed_seconds': session.elapsed_time.total_seconds()})
            self._update_button_states(True, session.is_paused)

            # Update status
            if session.is_paused:
                status_text = "Paused"
            elif session.record.warning_triggered:
                status_text = "Warning!"
            else:
                status_text = session.record.session_type.value.title()

            self.status_label.set_markup(f"<span size='small'>{status_text}</span>")
        else:
            # No active session
            self.time_label.set_markup("<span size='xx-large' weight='bold'>00:00</span>")
            self.progress_bar.set_fraction(0.0)
            self.status_label.set_markup("<span size='small'>Ready</span>")
            self._update_button_states(False, False)
            self._stop_warning_animation()

    def _update_timer_display(self, data: dict) -> None:
        """Update timer display with current time"""
        try:
            timer_engine = self.app_context.timer_engine

            if timer_engine.has_active_session:
                session = timer_engine.active_session

                # Calculate time display
                if self.config.time_display_format.value == "MINUTES_SECONDS":
                    remaining_seconds = max(0, session.remaining_time.total_seconds())
                    time_text = format_time_display(remaining_seconds, "MINUTES_SECONDS")
                else:
                    remaining_seconds = max(0, session.remaining_time.total_seconds())
                    time_text = format_time_display(remaining_seconds, "MINUTES_ONLY")

                self.time_label.set_markup(f"<span size='xx-large' weight='bold'>{time_text}</span>")

                # Update progress bar
                progress = calculate_session_progress(
                    session.elapsed_time.total_seconds(),
                    session.record.duration_minutes * 60
                )
                self.progress_bar.set_fraction(progress)

        except Exception as e:
            handle_error(
                exception=e,
                message="Error updating timer display",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.GUI
            )

    def _update_button_states(self, has_session: bool, is_paused: bool) -> None:
        """Update button states based on session state"""
        if has_session:
            self.start_button.set_sensitive(is_paused)
            self.start_button.set_label("Resume" if is_paused else "Running")
            self.pause_button.set_sensitive(not is_paused)
            self.stop_button.set_sensitive(True)

            # Disable preset buttons during session
            for button in self.preset_buttons:
                button.set_sensitive(False)
        else:
            self.start_button.set_sensitive(True)
            self.start_button.set_label("Start")
            self.pause_button.set_sensitive(False)
            self.stop_button.set_sensitive(False)

            # Enable preset buttons
            for button in self.preset_buttons:
                button.set_sensitive(True)

    def _start_warning_animation(self) -> None:
        """Start warning animation"""
        if self._warning_active:
            return

        self._warning_active = True

        if self.config.visual_warnings.mode.value == "FLASH":
            self._start_flash_animation()
        elif self.config.visual_warnings.mode.value == "RESIZE":
            self._start_resize_animation()
        elif self.config.visual_warnings.mode.value == "COLOR_CHANGE":
            self._start_color_animation()

    def _stop_warning_animation(self) -> None:
        """Stop warning animation"""
        self._warning_active = False

        if self._warning_animation_id:
            GLib.source_remove(self._warning_animation_id)
            self._warning_animation_id = None

        # Reset window appearance
        self.set_opacity(self._original_opacity)
        # Could reset size and color here too

    def _start_flash_animation(self) -> None:
        """Start flash animation"""
        def flash_step():
            if not self._warning_active:
                return False

            current_opacity = self.get_opacity()
            new_opacity = 0.3 if current_opacity > 0.5 else 1.0
            self.set_opacity(new_opacity)

            return True

        self._warning_animation_id = GLib.timeout_add(
            self.config.visual_warnings.flash_interval_ms,
            flash_step
        )

    def _start_resize_animation(self) -> None:
        """Start resize animation"""
        # Simplified resize animation
        def resize_step():
            if not self._warning_active:
                return False

            current_size = self.get_size()
            scale_factor = 1.2 if self.get_size() == (64, 64) else 1.0

            new_width = int(self.config.icon_size.width * scale_factor)
            new_height = int(self.config.icon_size.height * scale_factor)
            self.resize(new_width, new_height)

            return True

        self._warning_animation_id = GLib.timeout_add(500, resize_step)

    def _start_color_animation(self) -> None:
        """Start color change animation"""
        # Update progress bar color to warning color
        css_provider = Gtk.CssProvider()
        css = f"""
        progressbar progress {{
            background-color: {self.config.visual_warnings.warning_color};
            border-radius: 2px;
        }}
        """
        css_provider.load_from_data(css.encode('utf-8'))

        progress_style = self.progress_bar.get_style_context()
        progress_style.add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_window_state_event(self, widget, event) -> bool:
        """Handle window state changes"""
        # Keep window above others even when other windows get focus
        if event.new_window_state & Gdk.WindowState.FOCUSED:
            self.set_keep_above(True)
        return True

    def on_delete_event(self, widget, event) -> bool:
        """Handle window close event"""
        # Don't actually close, just hide
        self.hide()
        return True  # Prevent window destruction

    def cleanup(self) -> None:
        """Cleanup resources"""
        self._stop_warning_animation()

        if self.update_timer_id:
            GLib.source_remove(self.update_timer_id)