#!/usr/bin/env python3

"""Check for missing dependencies"""

import sys

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {module_name}")
        return True
    except ImportError as e:
        package = package_name or module_name
        print(f"✗ {module_name} - {e}")
        print(f"  Install with: pip install {package}")
        return False

def main():
    print("Checking dependencies...")
    print("=" * 40)

    dependencies = [
        ("yaml", "PyYAML>=6.0"),
        ("watchdog", "watchdog>=3.0.0"),
        ("psutil", "psutil>=5.9.0"),
        ("dateutil", "python-dateutil>=2.8.0"),
    ]

    missing = []
    for module, package in dependencies:
        if not check_import(module, package):
            missing.append(package)

    print("=" * 40)
    if missing:
        print(f"Missing dependencies: {len(missing)}")
        print("Install with:")
        for package in missing:
            print(f"  pip install {package}")
        return 1
    else:
        print("All dependencies are available!")
        return 0

if __name__ == "__main__":
    sys.exit(main())