"""
Error handling utilities for Lightime Pomodoro Timer
"""

import logging
import traceback
import sys
import os
import threading
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, Callable, List
from pathlib import Path
from dataclasses import dataclass, field

from ..models.config import LightimeConfig


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Non-critical, user can continue
    MEDIUM = "medium"     # May affect functionality but app continues
    HIGH = "high"         # Serious issue, may need restart
    CRITICAL = "critical" # App cannot continue


class ErrorCategory(Enum):
    """Error categories"""
    CONFIGURATION = "configuration"
    TIMER = "timer"
    GUI = "gui"
    FILE_IO = "file_io"
    SYSTEM_INTEGRATION = "system_integration"
    PERFORMANCE = "performance"
    NETWORK = "network"
    USER_INPUT = "user_input"
    UNKNOWN = "unknown"


@dataclass
class ErrorReport:
    """Detailed error report"""
    error_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    severity: ErrorSeverity = ErrorSeverity.LOW
    category: ErrorCategory = ErrorCategory.UNKNOWN
    message: str = ""
    exception: Optional[Exception] = None
    traceback_str: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    user_action: str = ""
    resolution: str = ""
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert error report to dictionary"""
        return {
            'error_id': self.error_id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'category': self.category.value,
            'message': self.message,
            'exception_type': type(self.exception).__name__ if self.exception else None,
            'traceback': self.traceback_str,
            'context': self.context,
            'user_action': self.user_action,
            'resolution': self.resolution,
            'resolved': self.resolved
        }


class ErrorManager:
    """Centralized error management and reporting"""

    def __init__(self, config: Optional[LightimeConfig] = None):
        self.config = config
        self.logger = self._setup_logger()
        self._error_reports: List[ErrorReport] = []
        self._error_callbacks: List[Callable[[ErrorReport], None]] = []
        self._shutdown_handlers: List[Callable[[], None]] = []

        # Setup global exception handler
        self._setup_global_exception_handler()

    def _setup_logger(self) -> logging.Logger:
        """Setup error logging"""
        logger = logging.getLogger('lightime.errors')
        logger.setLevel(logging.WARNING)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (if configured)
        if self.config and hasattr(self.config.logging, 'get_expanded_path'):
            try:
                log_dir = self.config.logging.get_expanded_path().parent
                log_dir.mkdir(parents=True, exist_ok=True)

                file_handler = logging.FileHandler(
                    log_dir / 'lightime_errors.log',
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.WARNING)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            except Exception as e:
                print(f"Error setting up file logger: {e}")

        return logger

    def _setup_global_exception_handler(self) -> None:
        """Setup global exception handler for uncaught exceptions"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions"""
            if issubclass(exc_type, KeyboardInterrupt):
                # Allow KeyboardInterrupt to terminate
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            self.handle_error(
                exception=exc_value,
                severity=ErrorSeverity.CRITICAL,
                category=ErrorCategory.UNKNOWN,
                context={'uncaught_exception': True},
                user_action="Application encountered an unexpected error and needs to restart"
            )

        sys.excepthook = handle_exception

    def add_error_callback(self, callback: Callable[[ErrorReport], None]) -> None:
        """Add callback for error notifications"""
        self._error_callbacks.append(callback)

    def remove_error_callback(self, callback: Callable[[ErrorReport], None]) -> None:
        """Remove error callback"""
        if callback in self._error_callbacks:
            self._error_callbacks.remove(callback)

    def add_shutdown_handler(self, handler: Callable[[], None]) -> None:
        """Add shutdown handler for cleanup"""
        self._shutdown_handlers.append(handler)

    def handle_error(
        self,
        exception: Optional[Exception] = None,
        message: str = "",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[Dict[str, Any]] = None,
        user_action: str = "",
        log_level: Optional[int] = None
    ) -> ErrorReport:
        """Handle and log an error"""
        # Generate error ID
        error_id = f"ERR-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{id(exception) % 10000:04d}"

        # Create error report
        error_report = ErrorReport(
            error_id=error_id,
            severity=severity,
            category=category,
            message=message or str(exception) if exception else "Unknown error",
            exception=exception,
            traceback_str=traceback.format_exc() if exception else "",
            context=context or {},
            user_action=user_action
        )

        # Store error report
        self._error_reports.append(error_report)

        # Limit stored reports to prevent memory bloat
        if len(self._error_reports) > 1000:
            self._error_reports = self._error_reports[-1000:]

        # Log the error
        self._log_error(error_report, log_level)

        # Notify callbacks
        self._notify_callbacks(error_report)

        # Handle critical errors
        if severity == ErrorSeverity.CRITICAL:
            self._handle_critical_error(error_report)

        return error_report

    def _log_error(self, error_report: ErrorReport, log_level: Optional[int] = None) -> None:
        """Log error report"""
        if log_level is None:
            # Determine log level from severity
            log_level_map = {
                ErrorSeverity.LOW: logging.INFO,
                ErrorSeverity.MEDIUM: logging.WARNING,
                ErrorSeverity.HIGH: logging.ERROR,
                ErrorSeverity.CRITICAL: logging.CRITICAL
            }
            log_level = log_level_map.get(error_report.severity, logging.WARNING)

        # Format log message
        log_message = (
            f"[{error_report.error_id}] "
            f"{error_report.category.value.upper()}: {error_report.message}"
        )

        if error_report.context:
            log_message += f" | Context: {error_report.context}"

        self.logger.log(log_level, log_message)

        # Log full traceback for exceptions
        if error_report.traceback_str:
            self.logger.debug(f"[{error_report.error_id}] Traceback: {error_report.traceback_str}")

    def _notify_callbacks(self, error_report: ErrorReport) -> None:
        """Notify error callbacks"""
        for callback in self._error_callbacks:
            try:
                callback(error_report)
            except Exception as e:
                self.logger.error(f"Error in error callback: {e}")

    def _handle_critical_error(self, error_report: ErrorReport) -> None:
        """Handle critical errors that may require shutdown"""
        self.logger.critical(f"Critical error occurred: {error_report.error_id}")

        # Run shutdown handlers
        for handler in self._shutdown_handlers:
            try:
                handler()
            except Exception as e:
                self.logger.error(f"Error in shutdown handler: {e}")

    def resolve_error(self, error_id: str, resolution: str = "") -> bool:
        """Mark an error as resolved"""
        for error_report in self._error_reports:
            if error_report.error_id == error_id:
                error_report.resolved = True
                error_report.resolution = resolution
                self.logger.info(f"Error {error_id} resolved: {resolution}")
                return True
        return False

    def get_errors(
        self,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        resolved: Optional[bool] = None,
        limit: Optional[int] = None
    ) -> List[ErrorReport]:
        """Get filtered error reports"""
        errors = self._error_reports

        # Apply filters
        if severity:
            errors = [e for e in errors if e.severity == severity]

        if category:
            errors = [e for e in errors if e.category == category]

        if resolved is not None:
            errors = [e for e in errors if e.resolved == resolved]

        # Sort by timestamp (newest first)
        errors.sort(key=lambda e: e.timestamp, reverse=True)

        # Apply limit
        if limit:
            errors = errors[:limit]

        return errors

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = len(self._error_reports)
        unresolved_errors = len([e for e in self._error_reports if not e.resolved])

        # Count by severity
        severity_counts = {}
        for severity in ErrorSeverity:
            count = len([e for e in self._error_reports if e.severity == severity])
            severity_counts[severity.value] = count

        # Count by category
        category_counts = {}
        for category in ErrorCategory:
            count = len([e for e in self._error_reports if e.category == category])
            category_counts[category.value] = count

        # Recent errors (last 24 hours)
        cutoff = datetime.now().timestamp() - (24 * 3600)
        recent_errors = len([e for e in self._error_reports if e.timestamp.timestamp() > cutoff])

        return {
            'total_errors': total_errors,
            'unresolved_errors': unresolved_errors,
            'resolved_errors': total_errors - unresolved_errors,
            'recent_errors_24h': recent_errors,
            'severity_distribution': severity_counts,
            'category_distribution': category_counts,
            'resolution_rate': ((total_errors - unresolved_errors) / total_errors * 100) if total_errors > 0 else 0
        }

    def export_errors(self, file_path: str) -> bool:
        """Export error reports to file"""
        try:
            import json

            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'statistics': self.get_error_statistics(),
                'errors': [error.to_dict() for error in self._error_reports]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            self.logger.error(f"Error exporting error reports: {e}")
            return False

    def clear_errors(self, resolved_only: bool = True) -> int:
        """Clear error reports"""
        if resolved_only:
            original_count = len(self._error_reports)
            self._error_reports = [e for e in self._error_reports if not e.resolved]
            cleared_count = original_count - len(self._error_reports)
        else:
            cleared_count = len(self._error_reports)
            self._error_reports.clear()

        self.logger.info(f"Cleared {cleared_count} error reports")
        return cleared_count

    def create_error_context(self, **kwargs) -> Dict[str, Any]:
        """Create standardized error context"""
        context = {
            'timestamp': datetime.now().isoformat(),
            'process_id': os.getpid() if 'os' in globals() else None,
            'thread_id': threading.current_thread().ident if 'threading' in globals() else None,
        }

        # Add application-specific context
        if self.config:
            context['config_version'] = self.config.config_version

        # Add provided context
        context.update(kwargs)

        return context

    def shutdown(self) -> None:
        """Clean shutdown of error manager"""
        self.logger.info("Error manager shutting down")

        # Export final error report
        try:
            log_dir = Path.home() / ".local" / "share" / "lightime"
            log_dir.mkdir(parents=True, exist_ok=True)
            self.export_errors(str(log_dir / "final_error_report.json"))
        except Exception as e:
            print(f"Error exporting final error report: {e}")

        # Clear callbacks
        self._error_callbacks.clear()
        self._shutdown_handlers.clear()


# Global error manager instance
_global_error_manager: Optional[ErrorManager] = None


def get_error_manager() -> ErrorManager:
    """Get global error manager instance"""
    global _global_error_manager
    if _global_error_manager is None:
        _global_error_manager = ErrorManager()
    return _global_error_manager


def handle_error(
    exception: Optional[Exception] = None,
    message: str = "",
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    context: Optional[Dict[str, Any]] = None,
    user_action: str = ""
) -> ErrorReport:
    """Convenience function to handle errors"""
    error_manager = get_error_manager()
    return error_manager.handle_error(
        exception=exception,
        message=message,
        severity=severity,
        category=category,
        context=context,
        user_action=user_action
    )


def safe_execute(
    func: Callable,
    *args,
    default_return=None,
    error_message: str = "",
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    **kwargs
) -> Any:
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(
            exception=e,
            message=error_message or f"Error executing {func.__name__}",
            severity=severity,
            category=category,
            context={'function': func.__name__, 'args': args, 'kwargs': kwargs}
        )
        return default_return