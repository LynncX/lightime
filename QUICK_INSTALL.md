# Lightime - One-Line Installation

## 🚀 Super Quick Installation

### Option 1: Install from Web (Recommended for Beginners)

```bash
curl -fsSL https://raw.githubusercontent.com/your-username/lightime/main/install.sh | bash
```

### Option 2: Download and Install

```bash
# Download the installer
wget https://raw.githubusercontent.com/your-username/lightime/main/install.sh

# Make it executable and run
chmod +x install.sh
./install.sh
```

### Option 3: Git Clone and Install

```bash
git clone https://github.com/your-username/lightime.git
cd lightime
chmod +x install.sh
./install.sh
```

## 🎯 What Happens During Installation

The installer will automatically:

1. ✅ **Check your system** - Detect Linux distribution and requirements
2. ✅ **Install dependencies** - Install all required packages for your system
3. ✅ **Download Lightime** - Get the latest version from GitHub
4. ✅ **Setup Python environment** - Create isolated environment with dependencies
5. ✅ **Create desktop entry** - Add Lightime to your application menu
6. ✅ **Test everything** - Verify installation works correctly
7. ✅ **Create shortcuts** - Add convenient run, update, and uninstall scripts

## 🏃‍♂️ After Installation

Once installation completes, you can start Lightime immediately:

```bash
cd ~/lightime
./run.sh
```

## 📋 What You'll See

### Installation Process:
```
╔══════════════════════════════════════════════════════════════╗
║                    Lightime Pomodoro Timer                    ║
║                     One-Click Installer                      ║
╚══════════════════════════════════════════════════════════════╝

[STEP 1/7] Pre-flight checks
[INFO] Checking internet connection...
[SUCCESS] Internet connection available
[SUCCESS] Detected: Ubuntu/Debian

[STEP 2/7] Setting up Git
[SUCCESS] Git is available

[STEP 3/7] Downloading Lightime
[SUCCESS] Repository ready at: /home/username/lightime

[STEP 4/7] Installing system dependencies
[SUCCESS] System dependencies installed

[STEP 5/7] Setting up Python environment
[SUCCESS] Python environment ready

[STEP 6/7] Testing installation
[SUCCESS] Core functionality tests passed
[SUCCESS] GUI dependencies test passed

[STEP 7/7] Creating shortcuts
[SUCCESS] Desktop entry created
[SUCCESS] Run scripts created

╔══════════════════════════════════════════════════════════════╗
║                  🎉 Installation Complete! 🎉                    ║
╚══════════════════════════════════════════════════════════════╝

Lightime Pomodoro Timer is now installed!

🚀 To start Lightime:
   cd /home/username/lightime
   ./run.sh

📂 Installation location:
   /home/username/lightime

⚙️  Configuration:
   ~/.config/lightime/config.yaml

📊 Session logs:
   ~/.local/share/lightime/sessions.csv

🔄 Update Lightime:
   cd /home/username/lightime && ./update.sh

🗑️  Uninstall Lightime:
   cd /home/username/lightime && ./uninstall.sh

Enjoy your Pomodoro sessions! 🍅
```

## 📱 Desktop Integration

After installation, you'll find Lightime in your application menu:
- **Applications → Office → Lightime**
- **Or click the desktop entry** if your system supports it

## 🛠️ Management Scripts

The installer creates these convenient scripts in `~/lightime/`:

- **`./run.sh`** - Start Lightime
- **`./update.sh`** - Update to latest version
- **`./uninstall.sh`** - Remove Lightime completely

## 🔧 Advanced Options

The installer supports these options:

```bash
# Show help
./install.sh --help

# Update existing installation
./install.sh --update

# Uninstall Lightime
./install.sh --uninstall
```

## ⚠️ Troubleshooting

If you encounter issues:

1. **Internet connection**: Make sure you're connected to the internet
2. **Permissions**: Don't run with `sudo` - the installer works as a normal user
3. **Disk space**: Ensure you have at least 500MB free space
4. **System updates**: Run `sudo apt update && sudo apt upgrade` first (Ubuntu/Debian)

## 🎯 Success Indicators

Installation was successful if you see:
- ✅ Green "Installation Complete!" message
- ✅ `~/lightime` directory created
- ✅ Lightime appears in your application menu
- ✅ `./run.sh` starts the application

## 🆘 Getting Help

If you run into problems:

1. Check the error messages during installation
2. Run `~/lightime/quick_test.py` to diagnose issues
3. Visit the GitHub repository for troubleshooting guides
4. Open an issue with your system information and error messages

**The one-click installer makes Lightime accessible to everyone - no technical knowledge required!** 🎉