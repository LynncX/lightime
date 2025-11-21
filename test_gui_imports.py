#!/usr/bin/env python3

"""
Test GUI imports to verify compatibility with different AppIndicator libraries
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_gtk_import():
    """Test GTK3 import"""
    print("Testing GTK3 import...")
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        print("✓ GTK3 import successful")
        return True
    except ImportError as e:
        print(f"✗ GTK3 import failed: {e}")
        return False
    except ValueError as e:
        print(f"✗ GTK3 version not available: {e}")
        return False

def test_appindicator_import():
    """Test AppIndicator library import with fallback"""
    print("\nTesting AppIndicator libraries...")

    # Test AyatanaAppIndicator3 first (modern Ubuntu 22.04+)
    try:
        gi.require_version('AyatanaAppIndicator3', '0.1')
        from gi.repository import AyatanaAppIndicator3
        print("✓ AyatanaAppIndicator3 import successful (modern)")
        return True
    except (ImportError, ValueError):
        print("• AyatanaAppIndicator3 not available, trying legacy fallback...")

        try:
            gi.require_version('AppIndicator3', '0.1')
            from gi.repository import AppIndicator3
            print("✓ AppIndicator3 import successful (legacy fallback)")
            return True
        except (ImportError, ValueError):
            print("✗ No AppIndicator library available")
            return False

def test_lightime_gui_imports():
    """Test Lightime GUI component imports"""
    print("\nTesting Lightime GUI components...")

    try:
        # Test timer window
        from gui.timer_window import TimerWindow
        print("✓ TimerWindow import successful")

        # Test tray icon (will print status)
        from gui.tray_icon import TrayIcon
        print("✓ TrayIcon import successful")

        # Test GUI application
        from gui.application import LightimeApplication, GUIManager
        print("✓ GUI application imports successful")

        return True

    except ImportError as e:
        print(f"✗ GUI component import failed: {e}")
        return False

def test_full_import():
    """Test complete application import"""
    print("\nTesting complete application...")

    try:
        # Import app context
        from app_context import ApplicationContext
        print("✓ ApplicationContext import successful")

        # Try to create app context
        app = ApplicationContext()
        print("✓ ApplicationContext creation successful")

        # Test integration
        integration = app.test_integration()
        print(f"✓ Integration tests: {integration}")

        # Cleanup
        app.shutdown()
        print("✓ Application cleanup successful")

        return True

    except Exception as e:
        print(f"✗ Full application test failed: {e}")
        return False

def main():
    """Run all GUI import tests"""
    print("=== Lightime GUI Import Test ===\n")

    tests = [
        ("GTK3", test_gtk_import),
        ("AppIndicator", test_appindicator_import),
        ("Lightime GUI", test_lightime_gui_imports),
        ("Full Application", test_full_import),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1

    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All GUI import tests passed!")
        print("\nYou should now be able to run:")
        print("  python3 src/main.py")
        return 0
    else:
        print("❌ Some GUI tests failed")
        print("\nInstall missing dependencies:")
        print("  sudo apt install libayatana-appindicator3-dev")
        return 1

if __name__ == "__main__":
    sys.exit(main())