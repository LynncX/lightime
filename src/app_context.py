"""
Application context and main orchestrator for Lightime Pomodoro Timer
"""

import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import atexit

try:
    from .models.config import LightimeConfig
    from .models.session import SessionRecord
    from .utils.config import ConfigManager
    from .utils.performance import PerformanceMonitor
    from .utils.error_handling import ErrorManager, ErrorSeverity
    from .utils.system_integration import SystemIntegration
    from .utils.helpers import setup_signal_handlers
    from .timer.engine import TimerEngine, TimerEvent
    from .session_logging.session_logger import SessionLogger
except ImportError:
    # Fallback for direct execution
    from models.config import LightimeConfig
    from models.session import SessionRecord
    from utils.config import ConfigManager
    from utils.performance import PerformanceMonitor
    from utils.error_handling import ErrorManager, ErrorSeverity
    from utils.system_integration import SystemIntegration
    from utils.helpers import setup_signal_handlers
    from timer.engine import TimerEngine, TimerEvent
    from session_logging.session_logger import SessionLogger


class ApplicationContext:
    """Main application context and orchestrator"""

    def __init__(self, config_dir: Optional[Path] = None):
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

        # Initialize core components
        self.config_manager = ConfigManager(config_dir)
        self.error_manager = ErrorManager(self.config_manager.config)
        self.performance_monitor = PerformanceMonitor(self.config_manager.config.performance)
        self.system_integration = SystemIntegration()
        self.session_logger = SessionLogger(self.config_manager.config.logging)
        self.timer_engine = TimerEngine(self.config_manager.config)

        # Application state
        self._running = False
        self._shutdown_handlers: list[Callable] = []

        # Setup component interactions
        self._setup_component_interactions()

        # Setup signal handlers
        setup_signal_handlers(self.shutdown)

        # Register cleanup
        atexit.register(self.shutdown)

        self.logger.info("Lightime application context initialized")

    def _setup_logging(self) -> None:
        """Setup basic logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _setup_component_interactions(self) -> None:
        """Setup interactions between components"""
        # Timer event handlers
        self.timer_engine.add_event_handler(
            TimerEvent.SESSION_COMPLETED,
            self._handle_session_completed
        )

        self.timer_engine.add_event_handler(
            TimerEvent.WARNING_TRIGGERED,
            self._handle_warning_triggered
        )

        # Configuration change handler
        self.config_manager.add_change_callback(self._handle_config_change)

        # Performance alert handler
        self.performance_monitor.add_alert_callback(self._handle_performance_alert)

        # Error callback for system notifications
        self.error_manager.add_error_callback(self._handle_error_notification)

    def _handle_session_completed(self, data: Dict[str, Any]) -> None:
        """Handle session completion"""
        try:
            # Log the session
            # Note: This would be called from timer engine with actual session record
            session_record = data.get('session_record')
            if session_record and isinstance(session_record, SessionRecord):
                self.session_logger.log_session(session_record)

                # Show completion notification
                self.system_integration.show_notification(
                    "Pomodoro Completed!",
                    f"Session completed in {data.get('actual_duration_minutes', 0):.1f} minutes"
                )

                # Auto-lock screen if configured
                if self.config_manager.config.logging.auto_log_sessions:  # Using existing config as trigger
                    self.system_integration.lock_screen()

        except Exception as e:
            self.error_manager.handle_error(
                exception=e,
                message="Error handling session completion",
                severity=ErrorSeverity.MEDIUM
            )

    def _handle_warning_triggered(self, data: Dict[str, Any]) -> None:
        """Handle timer warning"""
        try:
            remaining_minutes = data.get('remaining_minutes', 0)
            self.system_integration.show_notification(
                "Pomodoro Warning",
                f"{remaining_minutes:.1f} minutes remaining",
                timeout=3000
            )
        except Exception as e:
            self.error_manager.handle_error(
                exception=e,
                message="Error handling timer warning",
                severity=ErrorSeverity.LOW
            )

    def _handle_config_change(self, new_config: LightimeConfig) -> None:
        """Handle configuration changes"""
        try:
            # Update timer engine config
            self.timer_engine.update_config(new_config)

            # Update performance monitor settings
            self.performance_monitor.settings = new_config.performance

            # Update session logger config
            self.session_logger.config = new_config.logging

            self.logger.info("Configuration updated successfully")

        except Exception as e:
            self.error_manager.handle_error(
                exception=e,
                message="Error handling configuration change",
                severity=ErrorSeverity.MEDIUM
            )

    def _handle_performance_alert(self, alert) -> None:
        """Handle performance alerts"""
        if alert.alert_type == 'memory' and alert.current_value > alert.threshold * 1.5:
            # Critical memory usage
            self.error_manager.handle_error(
                message=f"Critical memory usage: {alert.current_value:.1f}MB",
                severity=ErrorSeverity.HIGH,
                category=self.error_manager.ErrorCategory.PERFORMANCE
            )

    def _handle_error_notification(self, error_report) -> None:
        """Handle error notifications"""
        if error_report.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.system_integration.show_notification(
                "Lightime Error",
                f"Error: {error_report.message}",
                level=self.system_integration.NotificationLevel.NORMAL
            )

    @property
    def config(self) -> LightimeConfig:
        """Get current configuration"""
        return self.config_manager.config

    @property
    def running(self) -> bool:
        """Check if application is running"""
        return self._running

    def start(self) -> bool:
        """Start the application"""
        try:
            if self._running:
                self.logger.warning("Application is already running")
                return True

            self.logger.info("Starting Lightime application")

            # Check startup performance
            if not self.performance_monitor.check_startup_performance():
                self.error_manager.handle_error(
                    message="Application startup exceeded performance limits",
                    severity=ErrorSeverity.MEDIUM
                )

            # Start performance monitoring
            self.performance_monitor.start_monitoring()

            # Create desktop entry if needed
            desktop_created = self.system_integration.create_desktop_entry()
            if desktop_created:
                self.logger.info("Desktop entry created successfully")

            self._running = True
            self.logger.info("Lightime application started successfully")

            return True

        except Exception as e:
            self.error_manager.handle_error(
                exception=e,
                message="Failed to start application",
                severity=ErrorSeverity.CRITICAL
            )
            return False

    def stop(self) -> bool:
        """Stop the application"""
        try:
            if not self._running:
                return True

            self.logger.info("Stopping Lightime application")

            # Cancel any active session
            if self.timer_engine.has_active_session:
                self.timer_engine.cancel_session()

            # Stop performance monitoring
            self.performance_monitor.stop_monitoring()

            self._running = False
            self.logger.info("Lightime application stopped successfully")

            return True

        except Exception as e:
            self.error_manager.handle_error(
                exception=e,
                message="Error stopping application",
                severity=ErrorSeverity.MEDIUM
            )
            return False

    def shutdown(self) -> None:
        """Clean shutdown of the application"""
        try:
            self.logger.info("Shutting down Lightime application")

            self.stop()

            # Run shutdown handlers
            for handler in self._shutdown_handlers:
                try:
                    handler()
                except Exception as e:
                    self.logger.error(f"Error in shutdown handler: {e}")

            # Shutdown components
            self.timer_engine.shutdown()
            self.performance_monitor.shutdown()
            self.config_manager.shutdown()
            self.error_manager.shutdown()

            self.logger.info("Lightime application shutdown complete")

        except Exception as e:
            print(f"Error during shutdown: {e}")

    def add_shutdown_handler(self, handler: Callable) -> None:
        """Add shutdown handler"""
        self._shutdown_handlers.append(handler)

    def remove_shutdown_handler(self, handler: Callable) -> None:
        """Remove shutdown handler"""
        if handler in self._shutdown_handlers:
            self._shutdown_handlers.remove(handler)

    def get_application_info(self) -> Dict[str, Any]:
        """Get comprehensive application information"""
        return {
            'version': '1.0.0',
            'running': self._running,
            'config': self.config.to_dict(),
            'system_info': self.system_integration.get_application_info(),
            'performance_stats': self.performance_monitor.get_statistics(),
            'error_stats': self.error_manager.get_error_statistics(),
            'session_logger_info': self.session_logger.get_log_info(),
            'timer_info': {
                'has_active_session': self.timer_engine.has_active_session,
                'session_info': self.timer_engine.get_session_info()
            }
        }

    def test_integration(self) -> Dict[str, Any]:
        """Test application integration"""
        try:
            results = {
                'config_loading': self.config is not None,
                'system_integration': self.system_integration.test_integration(),
                'performance_monitoring': self.performance_monitor.get_current_snapshot() is not None,
                'error_handling': True,  # Always available
                'session_logging': self.session_logger.get_log_info()['exists'],
                'timer_engine': True  # Basic timer engine creation succeeded
            }

            # Test configuration hot-reload
            original_config = self.config_manager.config
            test_update = {'max_cpu_usage': 2.0}
            config_reload_test = self.config_manager.update_config(test_update, create_user_file=False)
            results['config_hot_reload'] = config_reload_test

            # Restore original config
            self.config_manager._config = original_config

            return results

        except Exception as e:
            return {
                'error': str(e),
                'integration_tests': False
            }

    def export_diagnostics(self, file_path: str) -> bool:
        """Export diagnostic information"""
        try:
            import json

            diagnostics = {
                'export_timestamp': self.error_manager.create_error_context()['timestamp'],
                'application_info': self.get_application_info(),
                'integration_tests': self.test_integration(),
                'system_info': self.system_integration.system_info,
                'recent_errors': [error.to_dict() for error in self.error_manager.get_errors(limit=10)],
                'recent_performance': [
                    snapshot.to_dict()
                    for snapshot in self.performance_monitor.get_snapshots(limit=20)
                ]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(diagnostics, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Diagnostics exported to {file_path}")
            return True

        except Exception as e:
            self.error_manager.handle_error(
                exception=e,
                message="Error exporting diagnostics",
                severity=ErrorSeverity.MEDIUM
            )
            return False


# Global application context
_global_app_context: Optional[ApplicationContext] = None


def get_app_context() -> ApplicationContext:
    """Get global application context"""
    global _global_app_context
    if _global_app_context is None:
        _global_app_context = ApplicationContext()
    return _global_app_context


def initialize_app(config_dir: Optional[Path] = None) -> ApplicationContext:
    """Initialize application context"""
    global _global_app_context
    if _global_app_context is not None:
        return _global_app_context

    _global_app_context = ApplicationContext(config_dir)
    return _global_app_context


def shutdown_app() -> None:
    """Shutdown application context"""
    global _global_app_context
    if _global_app_context is not None:
        _global_app_context.shutdown()
        _global_app_context = None