# Lightime Installation Guide

## Quick Installation (Current Setup)

Since you already have PyGObject 3.42.1 installed system-wide, follow these steps:

### Step 1: Install Missing System Dependencies
```bash
# Install the correct Ayatana AppIndicator library for Ubuntu 22.04+
sudo apt install libayatana-appindicator3-dev
```

### Step 2: Install Python Dependencies
```bash
# Activate your conda environment
conda activate lightime

# Install the core requirements (skip system-wide packages)
pip install -r requirements-conda.txt
```

### Step 3: Test the Application
```bash
# Test core functionality
python test_models_only.py

# Test GUI imports
python test_gui_imports.py

# Run the application
python src/main.py
```

## What's Already Installed ✅

From your output, you have these dependencies ready:
- ✅ **Python 3.10** (conda environment)
- ✅ **PyGObject 3.42.1** (system-wide)
- ✅ **pyyaml-6.0.3** (just installed)
- ✅ **watchdog-6.0.0** (just installed)
- ✅ **psutil-7.1.3** (just installed)

## What Still Needed

1. **System Dependencies**: `libayatana-appindicator3-dev`
2. **Python Dependencies**: The remaining packages will be installed via pip

## Troubleshooting

### If pycairo is needed:
```bash
# Install system-wide pycairo
sudo apt install python3-cairo-dev

# Or install via pip (if system version doesn't work)
pip install pycairo
```

### Verify Installation:
```bash
python -c "
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
print('✅ GTK3 working!')

try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3
    print('✅ AyatanaAppIndicator3 working!')
except ImportError:
    print('❌ AyatanaAppIndicator3 not found')
"
```

## Expected Result

If all goes well, you should see:
- A tiny always-on-top timer window
- System tray icon with context menu
- Pomodoro timer functionality
- Session logging

## Alternative: GUI-less Mode

If GUI issues persist, Lightime can still work as a command-line tool:
```bash
python src/main.py --test  # Run tests
python src/main.py --help  # See options
```