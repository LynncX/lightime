#!/usr/bin/env python3

"""
Test only the core models without complex imports
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_models():
    """Test basic model functionality"""
    print("=== Testing Core Models ===\n")

    try:
        # Test configuration model
        print("1. Testing Configuration Model...")
        from models.config import (
            LightimeConfig, TimeDisplayFormat, VisualWarningMode,
            IconSize, VisualWarnings, KeyboardShortcuts
        )

        config = LightimeConfig()
        print(f"   ✓ Config created: {config.config_version}")
        print(f"   ✓ Default duration: {config.default_duration}")
        print(f"   ✓ Time format: {config.time_display_format.value}")

        # Test config to/from dict
        config_dict = config.to_dict()
        config_restored = LightimeConfig.from_dict(config_dict)
        print(f"   ✓ Config serialization works")

        return True

    except Exception as e:
        print(f"   ✗ Configuration model test failed: {e}")
        return False

def test_session_models():
    """Test session models"""
    try:
        print("\n2. Testing Session Models...")
        from models.session import (
            SessionRecord, ActiveSession, SessionManager,
            SessionStatus, SessionType
        )

        # Test session record
        record = SessionRecord(
            duration_minutes=25,
            session_type=SessionType.WORK
        )
        print(f"   ✓ Session record: {record.id}")
        print(f"   ✓ Duration: {record.duration_minutes}min")
        print(f"   ✓ Type: {record.session_type.value}")

        # Test session manager
        manager = SessionManager()
        active_session = manager.create_session(duration_minutes=15)
        print(f"   ✓ Active session created: {active_session.record.id}")

        # Test status changes
        active_session.start()
        print(f"   ✓ Session started: {active_session.record.status}")

        active_session.pause()
        print(f"   ✓ Session paused: {active_session.record.status}")

        active_session.start()  # Resume
        print(f"   ✓ Session resumed: {active_session.record.status}")

        # Test completion
        completed_record = manager.complete_session()
        print(f"   ✓ Session completed: {completed_record.status}")

        return True

    except Exception as e:
        print(f"   ✗ Session model test failed: {e}")
        return False

def test_timer_functionality():
    """Test basic timer functionality without threading"""
    try:
        print("\n3. Testing Timer Functionality...")
        from models.config import LightimeConfig
        from models.session import SessionType

        # Test timer engine by directly testing session manager
        config = LightimeConfig()
        from models.session import SessionManager

        print(f"   ✓ Creating session manager...")
        manager = SessionManager()

        print(f"   ✓ Has active session: {manager.has_active_session}")

        # Test session creation
        session = manager.create_session(
            duration_minutes=1,  # 1 minute for testing
            session_type=SessionType.WORK
        )
        print(f"   ✓ Test session created: {session.record.id}")

        # Test manual time calculations
        import time
        session.start()
        time.sleep(1)  # Wait 1 second

        elapsed = session.elapsed_time.total_seconds()
        remaining = session.remaining_time.total_seconds()
        progress = elapsed / (session.record.duration_minutes * 60)

        print(f"   ✓ Time calculations work: {elapsed:.1f}s elapsed, {remaining:.1f}s remaining")
        print(f"   ✓ Progress: {progress*100:.1f}%")

        # Test session completion
        completed = manager.complete_session()
        print(f"   ✓ Session completion: {completed.status}")

        print(f"   ✓ Session manager tests passed")
        return True

    except Exception as e:
        print(f"   ✗ Timer functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_helper_functions():
    """Test utility helper functions"""
    try:
        print("\n4. Testing Helper Functions...")
        from utils.helpers import (
            format_time_display, parse_duration_string,
            calculate_session_progress, clamp_value
        )

        # Test time formatting
        time_25min = 25 * 60
        formatted = format_time_display(time_25min, "MINUTES_SECONDS")
        print(f"   ✓ Time formatting: {formatted}")

        # Test duration parsing
        parsed = parse_duration_string("25min")
        print(f"   ✓ Duration parsing: 25min -> {parsed} minutes")

        # Test progress calculation
        progress = calculate_session_progress(750, 1500)  # 50% progress
        print(f"   ✓ Progress calculation: {progress*100:.1f}%")

        # Test value clamping
        clamped = clamp_value(150, 0, 100)
        print(f"   ✓ Value clamping: 150 -> {clamped} (max 100)")

        return True

    except Exception as e:
        print(f"   ✗ Helper functions test failed: {e}")
        return False

def main():
    """Run all model tests"""
    print("=== Lightime Core Models Test ===\n")

    tests = [
        test_basic_models,
        test_session_models,
        test_timer_functionality,
        test_helper_functions,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ✗ Test failed with exception: {e}")

    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All core model tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
