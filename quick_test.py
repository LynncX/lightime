#!/usr/bin/env python3

"""
Quick test to verify Lightime dependencies are working
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_core_deps():
    """Test core Python dependencies"""
    print("Testing core dependencies...")

    try:
        import yaml
        print("✅ PyYAML available")
    except ImportError:
        print("❌ PyYAML missing - run: pip install PyYAML")
        return False

    try:
        import watchdog
        print("✅ Watchdog available")
    except ImportError:
        print("❌ Watchdog missing - run: pip install watchdog")
        return False

    try:
        import psutil
        print("✅ psutil available")
    except ImportError:
        print("❌ psutil missing - run: pip install psutil")
        return False

    return True

def test_gtk_deps():
    """Test GTK/GUI dependencies"""
    print("\nTesting GTK dependencies...")

    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        print("✅ GTK3 available")
    except (ImportError, ValueError) as e:
        print(f"❌ GTK3 not working: {e}")
        return False

    # Test AppIndicator
    indicator_available = False
    try:
        gi.require_version('AyatanaAppIndicator3', '0.1')
        from gi.repository import AyatanaAppIndicator3
        print("✅ AyatanaAppIndicator3 available")
        indicator_available = True
    except (ImportError, ValueError):
        print("⚠️  AyatanaAppIndicator3 not available")

    try:
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3
        print("✅ AppIndicator3 (legacy) available")
        indicator_available = True
    except (ImportError, ValueError):
        print("⚠️  AppIndicator3 (legacy) not available")

    return indicator_available

def test_lightime_core():
    """Test Lightime core functionality"""
    print("\nTesting Lightime core...")

    try:
        from models.config import LightimeConfig
        config = LightimeConfig()
        print("✅ Configuration system working")
    except Exception as e:
        print(f"❌ Configuration system failed: {e}")
        return False

    try:
        from models.session import SessionManager
        manager = SessionManager()
        session = manager.create_session(duration_minutes=25)
        print("✅ Session management working")
    except Exception as e:
        print(f"❌ Session management failed: {e}")
        return False

    return True

def main():
    """Run quick tests"""
    print("=== Lightime Quick Dependency Test ===\n")

    core_ok = test_core_deps()
    gtk_ok = test_gtk_deps()
    lightime_ok = test_lightime_core()

    print(f"\n=== Results ===")
    print(f"Core dependencies: {'✅ OK' if core_ok else '❌ MISSING'}")
    print(f"GUI dependencies: {'✅ OK' if gtk_ok else '⚠️  PARTIAL'}")
    print(f"Lightime core: {'✅ OK' if lightime_ok else '❌ BROKEN'}")

    if core_ok and lightime_ok:
        print(f"\n🎉 Lightime core functionality is working!")
        if gtk_ok:
            print("🖥️  GUI should work too - try: python src/main.py")
        else:
            print("⚠️  GUI may have issues - install system dependencies")
        return 0
    else:
        print(f"\n❌ Some dependencies missing - check requirements")
        return 1

if __name__ == "__main__":
    sys.exit(main())