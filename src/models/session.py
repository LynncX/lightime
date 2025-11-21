"""
Session data models for Lightime Pomodoro Timer
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
import uuid


class SessionStatus(Enum):
    """Status of a Pomodoro session"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"
    WARNING = "warning"  # When warning threshold is reached


class SessionType(Enum):
    """Type of Pomodoro session"""
    WORK = "work"
    BREAK = "break"
    LONG_BREAK = "long_break"


@dataclass
class SessionRecord:
    """Immutable record of a completed Pomodoro session for logging"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_type: SessionType = SessionType.WORK
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_minutes: int = 25
    status: SessionStatus = SessionStatus.CREATED
    interruptions_count: int = 0
    total_interruption_time: timedelta = field(default_factory=lambda: timedelta(0))
    warning_triggered: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def actual_duration_minutes(self) -> float:
        """Calculate actual duration in minutes based on start and end times"""
        if self.end_time is None:
            return 0.0
        duration = self.end_time - self.start_time
        return duration.total_seconds() / 60.0

    @property
    def effective_work_minutes(self) -> float:
        """Calculate effective work minutes excluding interruptions"""
        return max(0, self.actual_duration_minutes - self.total_interruption_time.total_seconds() / 60.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session record to dictionary for serialization"""
        return {
            'id': self.id,
            'session_type': self.session_type.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status.value,
            'interruptions_count': self.interruptions_count,
            'total_interruption_seconds': self.total_interruption_time.total_seconds(),
            'warning_triggered': self.warning_triggered,
            'metadata': self.metadata,
            'actual_duration_minutes': self.actual_duration_minutes,
            'effective_work_minutes': self.effective_work_minutes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionRecord':
        """Create session record from dictionary"""
        record = cls(
            id=data.get('id', str(uuid.uuid4())),
            session_type=SessionType(data.get('session_type', 'work')),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            duration_minutes=data.get('duration_minutes', 25),
            status=SessionStatus(data.get('status', 'created')),
            interruptions_count=data.get('interruptions_count', 0),
            warning_triggered=data.get('warning_triggered', False),
            metadata=data.get('metadata', {})
        )

        # Convert interruption time back to timedelta
        interruption_seconds = data.get('total_interruption_seconds', 0)
        record.total_interruption_time = timedelta(seconds=interruption_seconds)

        return record


@dataclass
class ActiveSession:
    """Mutable active session state"""
    record: SessionRecord
    pause_time: Optional[datetime] = None
    last_warning_time: Optional[datetime] = None
    warning_count: int = 0

    @property
    def is_running(self) -> bool:
        """Check if session is currently running"""
        return self.record.status == SessionStatus.RUNNING

    @property
    def is_paused(self) -> bool:
        """Check if session is currently paused"""
        return self.record.status == SessionStatus.PAUSED

    @property
    def elapsed_time(self) -> timedelta:
        """Calculate elapsed time including pauses"""
        now = datetime.now()
        if self.pause_time:
            # Session is paused
            return self.pause_time - self.record.start_time
        else:
            # Session is running or completed
            return now - self.record.start_time

    @property
    def remaining_time(self) -> timedelta:
        """Calculate remaining time for the session"""
        target_duration = timedelta(minutes=self.record.duration_minutes)
        return max(timedelta(0), target_duration - self.elapsed_time)

    @property
    def is_completed(self) -> bool:
        """Check if session has reached its duration"""
        return self.elapsed_time >= timedelta(minutes=self.record.duration_minutes)

    def start(self) -> None:
        """Start or resume the session"""
        if self.record.status in [SessionStatus.CREATED, SessionStatus.PAUSED]:
            self.record.status = SessionStatus.RUNNING
            self.pause_time = None

    def pause(self) -> None:
        """Pause the current session"""
        if self.record.status == SessionStatus.RUNNING:
            self.record.status = SessionStatus.PAUSED
            self.pause_time = datetime.now()

    def complete(self) -> SessionRecord:
        """Complete the session and return immutable record"""
        self.record.end_time = datetime.now()
        self.record.status = SessionStatus.COMPLETED
        return self.record

    def cancel(self) -> SessionRecord:
        """Cancel the session and return immutable record"""
        self.record.end_time = datetime.now()
        self.record.status = SessionStatus.CANCELLED
        return self.record

    def interrupt(self) -> None:
        """Record an interruption"""
        self.record.interruptions_count += 1
        self.record.status = SessionStatus.INTERRUPTED

    def trigger_warning(self) -> None:
        """Trigger warning state"""
        self.record.status = SessionStatus.WARNING
        self.last_warning_time = datetime.now()
        self.warning_count += 1
        self.record.warning_triggered = True


class SessionManager:
    """Manages session lifecycle and state"""

    def __init__(self):
        self._active_session: Optional[ActiveSession] = None
        self._session_history: list[SessionRecord] = []

    @property
    def has_active_session(self) -> bool:
        """Check if there's an active session"""
        return self._active_session is not None

    @property
    def active_session(self) -> Optional[ActiveSession]:
        """Get current active session"""
        return self._active_session

    @property
    def session_history(self) -> list[SessionRecord]:
        """Get session history (immutable copy)"""
        return self._session_history.copy()

    def create_session(
        self,
        duration_minutes: int = 25,
        session_type: SessionType = SessionType.WORK
    ) -> ActiveSession:
        """Create a new active session"""
        if self.has_active_session:
            raise ValueError("Cannot create session while another is active")

        record = SessionRecord(
            duration_minutes=duration_minutes,
            session_type=session_type,
            status=SessionStatus.CREATED
        )
        self._active_session = ActiveSession(record=record)
        return self._active_session

    def start_session(self) -> None:
        """Start the current active session"""
        if not self.has_active_session:
            raise ValueError("No active session to start")
        self._active_session.start()

    def pause_session(self) -> None:
        """Pause the current active session"""
        if not self.has_active_session:
            raise ValueError("No active session to pause")
        self._active_session.pause()

    def complete_session(self) -> SessionRecord:
        """Complete the current session and add to history"""
        if not self.has_active_session:
            raise ValueError("No active session to complete")

        record = self._active_session.complete()
        self._session_history.append(record)
        self._active_session = None
        return record

    def cancel_session(self) -> SessionRecord:
        """Cancel the current session and add to history"""
        if not self.has_active_session:
            raise ValueError("No active session to cancel")

        record = self._active_session.cancel()
        self._session_history.append(record)
        self._active_session = None
        return record

    def interrupt_session(self) -> None:
        """Record an interruption in the current session"""
        if not self.has_active_session:
            raise ValueError("No active session to interrupt")
        self._active_session.interrupt()

    def get_recent_sessions(self, count: int = 10) -> list[SessionRecord]:
        """Get the most recent sessions"""
        return self._session_history[-count:] if self._session_history else []