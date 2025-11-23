#!/bin/bash
# Script to run Lightime from home directory with proper conda environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if conda environment exists
if ! command -v conda >/dev/null 2>&1; then
    echo "❌ Conda not found. Please install miniforge/miniconda first."
    exit 1
fi

if ! conda info --envs | grep -q "lightime"; then
    echo "❌ Conda environment 'lightime' not found."
    echo "   Please create it first: conda create -n lightime python=3.11"
    exit 1
fi

# Check if source code exists
if [ ! -f "$SCRIPT_DIR/src/main.py" ]; then
    echo "❌ Source code not found at $SCRIPT_DIR/src/main.py"
    exit 1
fi

# Activate conda environment
echo "✓ Activating conda environment 'lightime'"
source ~/miniforge3/bin/activate lightime 2>/dev/null || source ~/miniconda3/bin/activate lightime 2>/dev/null || {
    echo "❌ Failed to activate conda environment"
    exit 1
}

# Check for dependencies
if ! python3 -c "import watchdog, psutil" 2>/dev/null; then
    echo "📦 Installing missing dependencies..."
    pip install watchdog>=3.0.0 psutil>=5.9.0
fi

# Change to script directory
cd "$SCRIPT_DIR"

# Run as module to avoid namespace collision issues
echo "🚀 Starting Lightime..."
python3 -m src.main "$@"