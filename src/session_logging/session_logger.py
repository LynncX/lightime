"""
Session logging functionality for Lightime Pomodoro Timer
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum

from ..models.session import SessionRecord
from ..models.config import LoggingConfig, LogFileFormat


class LogField(Enum):
    """Standard log fields"""
    ID = "id"
    SESSION_TYPE = "session_type"
    START_TIME = "start_time"
    END_TIME = "end_time"
    DURATION_MINUTES = "duration_minutes"
    STATUS = "status"
    INTERRUPTIONS_COUNT = "interruptions_count"
    TOTAL_INTERRUPTION_SECONDS = "total_interruption_seconds"
    WARNING_TRIGGERED = "warning_triggered"
    ACTUAL_DURATION_MINUTES = "actual_duration_minutes"
    EFFECTIVE_WORK_MINUTES = "effective_work_minutes"
    METADATA = "metadata"


class SessionLogger:
    """Handles logging of completed Pomodoro sessions"""

    def __init__(self, logging_config: LoggingConfig):
        self.config = logging_config
        self._ensure_log_directory()

    def _ensure_log_directory(self) -> None:
        """Ensure log directory exists"""
        log_file_path = self.config.get_expanded_path()
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

    def log_session(self, session: SessionRecord) -> bool:
        """Log a completed session"""
        if not self.config.auto_log_sessions:
            return True

        try:
            if self.config.log_file_format == LogFileFormat.CSV:
                return self._log_csv(session)
            elif self.config.log_file_format == LogFileFormat.JSON:
                return self._log_json(session)
            elif self.config.log_file_format == LogFileFormat.PLAIN_TEXT:
                return self._log_plain_text(session)
            else:
                print(f"Unsupported log format: {self.config.log_file_format}")
                return False

        except Exception as e:
            print(f"Error logging session: {e}")
            return False

    def _log_csv(self, session: SessionRecord) -> bool:
        """Log session in CSV format"""
        log_file_path = self.config.get_expanded_path()
        file_exists = log_file_path.exists()

        try:
            with open(log_file_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    LogField.ID.value,
                    LogField.SESSION_TYPE.value,
                    LogField.START_TIME.value,
                    LogField.END_TIME.value,
                    LogField.DURATION_MINUTES.value,
                    LogField.STATUS.value,
                    LogField.INTERRUPTIONS_COUNT.value,
                    LogField.TOTAL_INTERRUPTION_SECONDS.value,
                    LogField.WARNING_TRIGGERED.value,
                    LogField.ACTUAL_DURATION_MINUTES.value,
                    LogField.EFFECTIVE_WORK_MINUTES.value,
                    LogField.METADATA.value
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header if file is new
                if not file_exists:
                    writer.writeheader()

                # Write session data
                writer.writerow(session.to_dict())

            return True

        except Exception as e:
            print(f"Error writing CSV log: {e}")
            return False

    def _log_json(self, session: SessionRecord) -> bool:
        """Log session in JSON format"""
        log_file_path = self.config.get_expanded_path()

        try:
            # Read existing data
            sessions = []
            if log_file_path.exists():
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            sessions = data
                        elif isinstance(data, dict) and 'sessions' in data:
                            sessions = data['sessions']
                    except json.JSONDecodeError:
                        sessions = []

            # Add new session
            sessions.append(session.to_dict())

            # Write updated data
            with open(log_file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': '1.0.0',
                    'generated_at': datetime.now().isoformat(),
                    'sessions': sessions
                }, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error writing JSON log: {e}")
            return False

    def _log_plain_text(self, session: SessionRecord) -> bool:
        """Log session in plain text format"""
        log_file_path = self.config.get_expanded_path()

        try:
            with open(log_file_path, 'a', encoding='utf-8') as f:
                # Format session information
                lines = [
                    "=" * 50,
                    f"Session ID: {session.id}",
                    f"Type: {session.session_type.value.title()}",
                    f"Status: {session.status.value}",
                    f"Start Time: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
                ]

                if session.end_time:
                    lines.append(f"End Time: {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    lines.append(f"Actual Duration: {session.actual_duration_minutes:.2f} minutes")
                    lines.append(f"Effective Work: {session.effective_work_minutes:.2f} minutes")

                lines.extend([
                    f"Planned Duration: {session.duration_minutes} minutes",
                    f"Interruptions: {session.interruptions_count}",
                    f"Warning Triggered: {'Yes' if session.warning_triggered else 'No'}",
                    "=" * 50,
                    ""
                ])

                f.write('\n'.join(lines))

            return True

        except Exception as e:
            print(f"Error writing plain text log: {e}")
            return False

    def get_session_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Read session history from log file"""
        log_file_path = self.config.get_expanded_path()

        if not log_file_path.exists():
            return []

        try:
            if self.config.log_file_format == LogFileFormat.CSV:
                return self._read_csv_history(log_file_path, limit)
            elif self.config.log_file_format == LogFileFormat.JSON:
                return self._read_json_history(log_file_path, limit)
            elif self.config.log_file_format == LogFileFormat.PLAIN_TEXT:
                return self._read_plain_text_history(log_file_path, limit)
            else:
                return []

        except Exception as e:
            print(f"Error reading session history: {e}")
            return []

    def _read_csv_history(self, log_file_path: Path, limit: Optional[int]) -> List[Dict[str, Any]]:
        """Read history from CSV file"""
        sessions = []

        with open(log_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            sessions = list(reader)

        if limit:
            sessions = sessions[-limit:]

        return sessions

    def _read_json_history(self, log_file_path: Path, limit: Optional[int]) -> List[Dict[str, Any]]:
        """Read history from JSON file"""
        with open(log_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            sessions = data.get('sessions', [])

        if limit:
            sessions = sessions[-limit:]

        return sessions

    def _read_plain_text_history(self, log_file_path: Path, limit: Optional[int]) -> List[Dict[str, Any]]:
        """Read history from plain text file (limited parsing)"""
        # For plain text, we can do basic parsing or return empty list
        # This would be more complex to parse reliably
        return []

    def get_statistics(self) -> Dict[str, Any]:
        """Calculate statistics from logged sessions"""
        sessions = self.get_session_history()

        if not sessions:
            return {
                'total_sessions': 0,
                'total_work_minutes': 0,
                'average_session_length': 0,
                'completion_rate': 0,
                'interruption_rate': 0
            }

        try:
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.get('status') == 'completed'])
            total_work_minutes = sum(float(s.get('effective_work_minutes', s.get('actual_duration_minutes', 0))) for s in sessions)
            total_interruptions = sum(int(s.get('interruptions_count', 0)) for s in sessions)

            return {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'total_work_minutes': total_work_minutes,
                'total_work_hours': total_work_minutes / 60.0,
                'average_session_length': total_work_minutes / total_sessions if total_sessions > 0 else 0,
                'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                'interruption_rate': (total_interruptions / total_sessions) if total_sessions > 0 else 0,
                'total_interruptions': total_interruptions
            }

        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {
                'total_sessions': 0,
                'total_work_minutes': 0,
                'average_session_length': 0,
                'completion_rate': 0,
                'interruption_rate': 0
            }

    def export_to_format(
        self,
        output_path: Path,
        output_format: LogFileFormat,
        sessions: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Export sessions to different format"""
        try:
            sessions_to_export = sessions or self.get_session_history()

            if not sessions_to_export:
                return True

            # Create a temporary logger with the target format
            temp_config = LoggingConfig(
                log_file_format=output_format,
                log_file_path=str(output_path),
                auto_log_sessions=True
            )

            temp_logger = SessionLogger(temp_config)

            # Convert dicts back to SessionRecord objects
            session_records = []
            for session_dict in sessions_to_export:
                session_records.append(SessionRecord.from_dict(session_dict))

            # Log all sessions to the new format
            output_path.parent.mkdir(parents=True, exist_ok=True)
            for session in session_records:
                if not temp_logger.log_session(session):
                    return False

            return True

        except Exception as e:
            print(f"Error exporting sessions: {e}")
            return False

    def clear_log(self) -> bool:
        """Clear the log file"""
        try:
            log_file_path = self.config.get_expanded_path()
            if log_file_path.exists():
                log_file_path.unlink()
            return True

        except Exception as e:
            print(f"Error clearing log file: {e}")
            return False

    def get_log_info(self) -> Dict[str, Any]:
        """Get information about the log file"""
        log_file_path = self.config.get_expanded_path()

        info = {
            'file_path': str(log_file_path),
            'format': self.config.log_file_format.value,
            'auto_logging': self.config.auto_log_sessions,
            'exists': log_file_path.exists(),
            'size_bytes': 0,
            'session_count': 0
        }

        if log_file_path.exists():
            info['size_bytes'] = log_file_path.stat().st_size
            info['session_count'] = len(self.get_session_history())

        return info