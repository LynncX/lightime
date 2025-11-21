"""
Performance monitoring utilities for Lightime Pomodoro Timer
"""

import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
import os
import gc

from ..models.config import PerformanceSettings


@dataclass
class PerformanceSnapshot:
    """Snapshot of performance metrics at a point in time"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    open_files: int = 0
    thread_count: int = 0
    process_id: int = field(default_factory=lambda: os.getpid())

    def to_dict(self) -> Dict:
        """Convert snapshot to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_mb': self.memory_mb,
            'memory_percent': self.memory_percent,
            'open_files': self.open_files,
            'thread_count': self.thread_count,
            'process_id': self.process_id
        }


@dataclass
class PerformanceAlert:
    """Performance alert information"""
    alert_type: str  # 'cpu', 'memory', 'file_handles'
    threshold: float
    current_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""

    def to_dict(self) -> Dict:
        """Convert alert to dictionary"""
        return {
            'alert_type': self.alert_type,
            'threshold': self.threshold,
            'current_value': self.current_value,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message
        }


class PerformanceMonitor:
    """Monitors application performance and enforces limits"""

    def __init__(self, performance_settings: PerformanceSettings):
        self.settings = performance_settings
        self.process = psutil.Process()
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._snapshots: List[PerformanceSnapshot] = []
        self._alerts: List[PerformanceAlert] = []
        self._alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        self._lock = threading.Lock()
        self._startup_time = datetime.now()

        # Initialize baseline measurements
        self._baseline_snapshot = self._take_snapshot()

    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """Add callback for performance alerts"""
        with self._lock:
            self._alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """Remove alert callback"""
        with self._lock:
            if callback in self._alert_callbacks:
                self._alert_callbacks.remove(callback)

    def start_monitoring(self, interval_seconds: float = 1.0) -> None:
        """Start performance monitoring in background thread"""
        if self._monitoring:
            return

        self._monitoring = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        if not self._monitoring:
            return

        self._monitoring = False
        self._stop_event.set()

        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)

    def _monitoring_loop(self, interval_seconds: float) -> None:
        """Main monitoring loop"""
        while self._monitoring and not self._stop_event.is_set():
            try:
                snapshot = self._take_snapshot()
                self._add_snapshot(snapshot)
                self._check_thresholds(snapshot)

                self._stop_event.wait(interval_seconds)

            except Exception as e:
                print(f"Error in performance monitoring: {e}")
                time.sleep(1.0)  # Brief pause on error

    def _take_snapshot(self) -> PerformanceSnapshot:
        """Take a performance snapshot"""
        try:
            # CPU usage (non-blocking)
            cpu_percent = self.process.cpu_percent()

            # Memory usage
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
            memory_percent = self.process.memory_percent()

            # Other metrics
            open_files = len(self.process.open_files())
            thread_count = self.process.num_threads()

            return PerformanceSnapshot(
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                open_files=open_files,
                thread_count=thread_count
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Error getting performance data: {e}")
            return PerformanceSnapshot()

    def _add_snapshot(self, snapshot: PerformanceSnapshot) -> None:
        """Add snapshot to history with size limiting"""
        with self._lock:
            self._snapshots.append(snapshot)

            # Keep only last 1000 snapshots to prevent memory bloat
            if len(self._snapshots) > 1000:
                self._snapshots = self._snapshots[-1000:]

    def _check_thresholds(self, snapshot: PerformanceSnapshot) -> None:
        """Check performance thresholds and generate alerts"""
        alerts = []

        # Check CPU usage
        if snapshot.cpu_percent > self.settings.max_cpu_usage:
            alerts.append(PerformanceAlert(
                alert_type='cpu',
                threshold=self.settings.max_cpu_usage,
                current_value=snapshot.cpu_percent,
                message=f"CPU usage ({snapshot.cpu_percent:.1f}%) exceeds threshold ({self.settings.max_cpu_usage:.1f}%)"
            ))

        # Check memory usage
        if snapshot.memory_mb > self.settings.max_memory_mb:
            alerts.append(PerformanceAlert(
                alert_type='memory',
                threshold=self.settings.max_memory_mb,
                current_value=snapshot.memory_mb,
                message=f"Memory usage ({snapshot.memory_mb:.1f}MB) exceeds threshold ({self.settings.max_memory_mb}MB)"
            ))

        # Check for too many open files (potential resource leak)
        if snapshot.open_files > 100:  # Reasonable limit for a small application
            alerts.append(PerformanceAlert(
                alert_type='file_handles',
                threshold=100,
                current_value=snapshot.open_files,
                message=f"Open file handles ({snapshot.open_files}) may indicate resource leak"
            ))

        # Send alerts
        for alert in alerts:
            self._send_alert(alert)

    def _send_alert(self, alert: PerformanceAlert) -> None:
        """Send performance alert to callbacks"""
        with self._lock:
            self._alerts.append(alert)

            # Keep only last 100 alerts
            if len(self._alerts) > 100:
                self._alerts = self._alerts[-100:]

        # Notify callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Error in performance alert callback: {e}")

    def get_current_snapshot(self) -> PerformanceSnapshot:
        """Get current performance snapshot"""
        return self._take_snapshot()

    def get_snapshots(self, limit: Optional[int] = None) -> List[PerformanceSnapshot]:
        """Get recent performance snapshots"""
        with self._lock:
            if limit:
                return self._snapshots[-limit:]
            return self._snapshots.copy()

    def get_alerts(self, limit: Optional[int] = None) -> List[PerformanceAlert]:
        """Get recent performance alerts"""
        with self._lock:
            if limit:
                return self._alerts[-limit:]
            return self._alerts.copy()

    def get_statistics(self) -> Dict:
        """Get performance statistics"""
        with self._lock:
            if not self._snapshots:
                return {}

            snapshots = self._snapshots

        cpu_values = [s.cpu_percent for s in snapshots]
        memory_values = [s.memory_mb for s in snapshots]

        return {
            'monitoring_duration_seconds': (datetime.now() - self._startup_time).total_seconds(),
            'snapshot_count': len(snapshots),
            'cpu': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0
            },
            'memory': {
                'current_mb': memory_values[-1] if memory_values else 0,
                'average_mb': sum(memory_values) / len(memory_values) if memory_values else 0,
                'max_mb': max(memory_values) if memory_values else 0,
                'min_mb': min(memory_values) if memory_values else 0
            },
            'alerts_count': len(self._alerts),
            'settings': {
                'max_cpu_usage': self.settings.max_cpu_usage,
                'max_memory_mb': self.settings.max_memory_mb,
                'startup_timeout_seconds': self.settings.startup_timeout_seconds
            }
        }

    def check_startup_performance(self) -> bool:
        """Check if startup performance meets requirements"""
        startup_time = datetime.now() - self._startup_time
        startup_seconds = startup_time.total_seconds()

        if startup_seconds > self.settings.startup_timeout_seconds:
            print(f"Startup time ({startup_seconds:.2f}s) exceeds threshold ({self.settings.startup_timeout_seconds}s)")
            return False

        # Check immediate resource usage
        snapshot = self._take_snapshot()
        if snapshot.memory_mb > self.settings.max_memory_mb:
            print(f"Startup memory usage ({snapshot.memory_mb:.1f}MB) exceeds threshold ({self.settings.max_memory_mb}MB)")
            return False

        return True

    def enforce_limits(self) -> bool:
        """Enforce performance limits (may trigger cleanup)"""
        snapshot = self._take_snapshot()
        cleanup_performed = False

        # Memory cleanup if needed
        if snapshot.memory_mb > self.settings.max_memory_mb * 0.8:  # 80% threshold
            gc.collect()  # Force garbage collection
            cleanup_performed = True

        return cleanup_performed

    def get_system_info(self) -> Dict:
        """Get system performance information"""
        try:
            # System-wide CPU and memory
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                'system': {
                    'cpu_count': cpu_count,
                    'memory_total_gb': memory.total / 1024 / 1024 / 1024,
                    'memory_available_gb': memory.available / 1024 / 1024 / 1024,
                    'memory_percent': memory.percent,
                    'disk_total_gb': disk.total / 1024 / 1024 / 1024,
                    'disk_free_gb': disk.free / 1024 / 1024 / 1024,
                    'disk_percent': ((disk.total - disk.free) / disk.total) * 100
                },
                'process': {
                    'pid': self.process.pid,
                    'create_time': datetime.fromtimestamp(self.process.create_time()).isoformat(),
                    'cmdline': self.process.cmdline()
                }
            }

        except Exception as e:
            print(f"Error getting system info: {e}")
            return {}

    def export_metrics(self, file_path: str) -> bool:
        """Export performance metrics to file"""
        try:
            import json

            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'settings': {
                    'max_cpu_usage': self.settings.max_cpu_usage,
                    'max_memory_mb': self.settings.max_memory_mb,
                    'startup_timeout_seconds': self.settings.startup_timeout_seconds
                },
                'statistics': self.get_statistics(),
                'snapshots': [s.to_dict() for s in self._snapshots[-100:]],  # Last 100 snapshots
                'alerts': [a.to_dict() for a in self._alerts[-50:]],  # Last 50 alerts
                'system_info': self.get_system_info()
            }

            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error exporting metrics: {e}")
            return False

    def reset_metrics(self) -> None:
        """Reset collected metrics and alerts"""
        with self._lock:
            self._snapshots.clear()
            self._alerts.clear()
        self._startup_time = datetime.now()