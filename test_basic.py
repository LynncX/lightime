#!/usr/bin/env python3

"""
Basic functionality test without GUI dependencies
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config_loading():
    """Test configuration loading"""
    print("Testing configuration loading...")

    try:
        from models.config import LightimeConfig

        # Test default configuration
        config = LightimeConfig()
        print(f"✓ Default duration: {config.default_duration}")
        print(f"✓ Warning minutes: {config.warning_minutes}")
        print(f"✓ Preset durations: {config.preset_durations}")

        return True

    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_session_models():
    """Test session data models"""
    print("\nTesting session models...")

    try:
        from models.session import SessionRecord, ActiveSession, SessionManager, SessionType, SessionStatus

        # Test session record
        record = SessionRecord(duration_minutes=25, session_type=SessionType.WORK)
        print(f"✓ Session record created: {record.id}")

        # Test session manager
        manager = SessionManager()
        active_session = manager.create_session(duration_minutes=25)
        print(f"✓ Active session created: {active_session.record.id}")

        # Test session status changes
        active_session.start()
        print(f"✓ Session started: {active_session.record.status}")

        return True

    except Exception as e:
        print(f"✗ Session models test failed: {e}")
        return False

def test_timer_engine():
    """Test timer engine (without thread)"""
    print("\nTesting timer engine...")

    try:
        from models.config import LightimeConfig
        from timer.engine import TimerEngine

        config = LightimeConfig()
        engine = TimerEngine(config)

        print(f"✓ Timer engine initialized")
        print(f"✓ Has active session: {engine.has_active_session}")

        # Test session creation
        session = engine.start_session(duration_minutes=1)  # 1 minute test
        print(f"✓ Session started: {session.record.id}")

        # Test session info
        info = engine.get_session_info()
        print(f"✓ Session info: {info['duration_minutes']}min, {info['status']}")

        # Clean up
        engine.cancel_session()
        engine.shutdown()

        return True

    except Exception as e:
        print(f"✗ Timer engine test failed: {e}")
        return False

def test_configuration_manager():
    """Test configuration manager"""
    print("\nTesting configuration manager...")

    try:
        from utils.config import ConfigManager, ConfigPaths

        # Test config paths
        paths = ConfigPaths()
        print(f"✓ Config directory: {paths.config_dir}")

        # Test config manager
        with ConfigManager() as config_manager:
            config = config_manager.config
            print(f"✓ Config loaded: {config.config_version}")
            print(f"✓ Default duration: {config.default_duration}")

        return True

    except Exception as e:
        print(f"✗ Configuration manager test failed: {e}")
        return False

def test_performance_monitoring():
    """Test performance monitoring"""
    print("\nTesting performance monitoring...")

    try:
        from models.config import PerformanceSettings
        from utils.performance import PerformanceMonitor

        settings = PerformanceSettings()
        monitor = PerformanceMonitor(settings)

        snapshot = monitor.get_current_snapshot()
        print(f"✓ Performance snapshot: {snapshot.memory_mb:.1f}MB")

        stats = monitor.get_statistics()
        print(f"✓ Performance stats collected")

        return True

    except Exception as e:
        print(f"✗ Performance monitoring test failed: {e}")
        return False

def test_application_context():
    """Test application context without GUI"""
    print("\nTesting application context...")

    try:
        from app_context import ApplicationContext

        app_context = ApplicationContext()
        print(f"✓ Application context initialized")

        info = app_context.get_application_info()
        print(f"✓ App info retrieved: v{info['version']}")

        # Test integration
        integration_tests = app_context.test_integration()
        print(f"✓ Integration tests passed: {integration_tests}")

        # Cleanup
        app_context.shutdown()
        print(f"✓ Application context shutdown")

        return True

    except Exception as e:
        print(f"✗ Application context test failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("=== Lightime Basic Functionality Tests ===\n")

    tests = [
        test_config_loading,
        test_session_models,
        test_timer_engine,
        test_configuration_manager,
        test_performance_monitoring,
        test_application_context,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())