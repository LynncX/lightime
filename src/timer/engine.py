"""
Timer engine for Lightime Pomodoro Timer
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from enum import Enum

from ..models.session import (
    SessionManager, ActiveSession, SessionRecord, SessionStatus, SessionType
)
from ..models.config import LightimeConfig


class TimerEvent(Enum):
    """Timer event types"""
    SESSION_STARTED = "session_started"
    SESSION_PAUSED = "session_paused"
    SESSION_RESUMED = "session_resumed"
    SESSION_COMPLETED = "session_completed"
    SESSION_CANCELLED = "session_cancelled"
    SESSION_INTERRUPTED = "session_interrupted"
    WARNING_TRIGGERED = "warning_triggered"
    TIME_UPDATED = "time_updated"


class TimerEngine:
    """Core timer engine managing Pomodoro sessions"""

    def __init__(self, config: LightimeConfig):
        self.config = config
        self.session_manager = SessionManager()
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._event_handlers: Dict[TimerEvent, list[Callable]] = {
            event: [] for event in TimerEvent
        }
        self._last_update_time: Optional[datetime] = None
        self._warning_triggered = False

    def add_event_handler(self, event: TimerEvent, handler: Callable) -> None:
        """Add an event handler for specific timer events"""
        self._event_handlers[event].append(handler)

    def remove_event_handler(self, event: TimerEvent, handler: Callable) -> None:
        """Remove an event handler"""
        if handler in self._event_handlers[event]:
            self._event_handlers[event].remove(handler)

    def _emit_event(self, event: TimerEvent, data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event to all registered handlers"""
        for handler in self._event_handlers[event]:
            try:
                handler(data or {})
            except Exception as e:
                # Log error but don't crash the timer
                print(f"Error in event handler for {event}: {e}")

    @property
    def has_active_session(self) -> bool:
        """Check if there's an active session"""
        return self.session_manager.has_active_session

    @property
    def active_session(self) -> Optional[ActiveSession]:
        """Get the current active session"""
        return self.session_manager.active_session

    def start_session(
        self,
        duration_minutes: Optional[int] = None,
        session_type: SessionType = SessionType.WORK
    ) -> ActiveSession:
        """Start a new Pomodoro session"""
        if self.has_active_session:
            raise ValueError("Cannot start session while another is active")

        duration = duration_minutes or self.config.default_duration

        # Create and start the session
        session = self.session_manager.create_session(duration_minutes=duration, session_type=session_type)
        session.start()

        # Reset warning state
        self._warning_triggered = False

        # Start the timer thread
        self._start_timer_thread()

        self._emit_event(TimerEvent.SESSION_STARTED, {
            'session_id': session.record.id,
            'duration_minutes': duration,
            'session_type': session_type.value
        })

        return session

    def pause_session(self) -> None:
        """Pause the current session"""
        if not self.has_active_session:
            return

        session = self.active_session
        if session.is_running:
            session.pause()
            self._pause_event.set()

            self._emit_event(TimerEvent.SESSION_PAUSED, {
                'session_id': session.record.id,
                'elapsed_time': session.elapsed_time.total_seconds()
            })

    def resume_session(self) -> None:
        """Resume a paused session"""
        if not self.has_active_session:
            return

        session = self.active_session
        if session.is_paused:
            session.start()
            self._pause_event.clear()

            self._emit_event(TimerEvent.SESSION_RESUMED, {
                'session_id': session.record.id,
                'remaining_time': session.remaining_time.total_seconds()
            })

    def complete_session(self) -> Optional[SessionRecord]:
        """Complete the current session"""
        if not self.has_active_session:
            return None

        session = self.active_session
        record = self.session_manager.complete_session()

        # Stop the timer thread
        self._stop_timer_thread()

        self._emit_event(TimerEvent.SESSION_COMPLETED, {
            'session_id': record.id,
            'duration_minutes': record.duration_minutes,
            'actual_duration_minutes': record.actual_duration_minutes,
            'effective_work_minutes': record.effective_work_minutes,
            'interruptions_count': record.interruptions_count
        })

        return record

    def cancel_session(self) -> Optional[SessionRecord]:
        """Cancel the current session"""
        if not self.has_active_session:
            return None

        session = self.active_session
        record = self.session_manager.cancel_session()

        # Stop the timer thread
        self._stop_timer_thread()

        self._emit_event(TimerEvent.SESSION_CANCELLED, {
            'session_id': record.id,
            'duration_minutes': record.duration_minutes,
            'actual_duration_minutes': record.actual_duration_minutes
        })

        return record

    def interrupt_session(self) -> None:
        """Record an interruption in the current session"""
        if not self.has_active_session:
            return

        self.session_manager.interrupt_session()

        self._emit_event(TimerEvent.SESSION_INTERRUPTED, {
            'session_id': self.active_session.record.id,
            'interruptions_count': self.active_session.record.interruptions_count
        })

    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current session"""
        if not self.has_active_session:
            return None

        session = self.active_session
        return {
            'session_id': session.record.id,
            'session_type': session.record.session_type.value,
            'duration_minutes': session.record.duration_minutes,
            'status': session.record.status.value,
            'start_time': session.record.start_time.isoformat(),
            'elapsed_seconds': session.elapsed_time.total_seconds(),
            'remaining_seconds': session.remaining_time.total_seconds(),
            'is_completed': session.is_completed,
            'is_paused': session.is_paused,
            'interruptions_count': session.record.interruptions_count,
            'warning_triggered': session.record.warning_triggered,
            'progress_percentage': min(100.0, (session.elapsed_time.total_seconds() / (session.record.duration_minutes * 60)) * 100)
        }

    def _start_timer_thread(self) -> None:
        """Start the timer monitoring thread"""
        if self._timer_thread and self._timer_thread.is_alive():
            return

        self._stop_event.clear()
        self._pause_event.clear()
        self._timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self._timer_thread.start()

    def _stop_timer_thread(self) -> None:
        """Stop the timer monitoring thread"""
        self._stop_event.set()
        self._pause_event.clear()

        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.join(timeout=1.0)

    def _timer_loop(self) -> None:
        """Main timer loop running in separate thread"""
        self._last_update_time = datetime.now()

        while not self._stop_event.is_set():
            try:
                # Check if session is still active
                if not self.has_active_session:
                    break

                session = self.active_session

                # Handle pause state
                if session.is_paused:
                    self._pause_event.wait(timeout=0.1)
                    continue

                # Check for session completion
                if session.is_completed:
                    # Session completed, emit event and complete
                    self.complete_session()
                    break

                # Check for warning threshold
                self._check_warning_threshold(session)

                # Emit time update event
                now = datetime.now()
                if (now - self._last_update_time).total_seconds() >= 1.0:  # Update every second
                    self._emit_event(TimerEvent.TIME_UPDATED, {
                        'session_id': session.record.id,
                        'elapsed_seconds': session.elapsed_time.total_seconds(),
                        'remaining_seconds': session.remaining_time.total_seconds(),
                        'progress_percentage': min(100.0, (session.elapsed_time.total_seconds() / (session.record.duration_minutes * 60)) * 100)
                    })
                    self._last_update_time = now

                # Sleep for a short interval
                time.sleep(0.1)

            except Exception as e:
                print(f"Error in timer loop: {e}")
                time.sleep(0.5)  # Brief pause on error

    def _check_warning_threshold(self, session: ActiveSession) -> None:
        """Check if warning threshold has been reached"""
        if session.record.warning_triggered:
            return  # Already triggered

        remaining_minutes = session.remaining_time.total_seconds() / 60.0

        if remaining_minutes <= self.config.warning_minutes:
            session.trigger_warning()
            self._warning_triggered = True

            self._emit_event(TimerEvent.WARNING_TRIGGERED, {
                'session_id': session.record.id,
                'remaining_minutes': remaining_minutes,
                'warning_threshold': self.config.warning_minutes
            })

    def update_config(self, config: LightimeConfig) -> None:
        """Update timer configuration"""
        self.config = config

        # If there's an active session, update its duration if needed
        if self.has_active_session and hasattr(config, 'default_duration'):
            session = self.active_session
            # Don't change duration for sessions in progress
            if session.record.status == SessionStatus.CREATED:
                session.record.duration_minutes = config.default_duration

    def shutdown(self) -> None:
        """Clean shutdown of the timer engine"""
        # Cancel any active session
        if self.has_active_session:
            self.cancel_session()

        # Stop timer thread
        self._stop_timer_thread()

        # Clear event handlers
        for event_handlers in self._event_handlers.values():
            event_handlers.clear()