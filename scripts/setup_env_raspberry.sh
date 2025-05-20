#!/bin/bash

# ===============================
# Drowsiness Detection Setup Script for Raspberry Pi OS
# ===============================

VENV_DIR="venv"
PYTHON_VERSION="3.10.15"
REQUIREMENTS_FILE="requirements-linux.txt"

echo "=========================================="
echo " Drowsiness Detection - Raspberry Pi Setup"
echo "=========================================="

# Step 0: Safety check
if [[ "$(uname -m)" != "aarch64" && "$(uname -m)" != "armv7l" ]]; then
    echo "[WARNING] This script is designed for Raspberry Pi OS. Proceed with caution."
fi

# Step 1: Update system packages
echo "[INFO] Updating system packages..."
sudo apt update

# Step 2: Check for pyenv and required Python version
if ! command -v pyenv &> /dev/null; then
    echo "[ERROR] pyenv is not installed. Please install pyenv and Python $PYTHON_VERSION before running this script."
    exit 1
fi

if ! pyenv versions --bare | grep -q "$PYTHON_VERSION"; then
    echo "[ERROR] Python $PYTHON_VERSION is not installed via pyenv."
    echo "        Please install it by running: pyenv install $PYTHON_VERSION"
    exit 1
fi

# Initialize pyenv for current shell
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Step 3: Set Python version globally
echo "[INFO] Setting Python $PYTHON_VERSION as global version..."
pyenv global "$PYTHON_VERSION"

# Step 4: Confirm Python version
PY_VERSION=$(python3 --version)
echo "[INFO] Current Python version: $PY_VERSION"

# Step 5: Install libcamera system packages
echo "[INFO] Installing Raspberry Pi camera libraries..."
sudo apt install -y python3-libcamera libcamera-dev

# Step 6: Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "[INFO] Virtual environment already exists. Skipping creation."
else
    echo "[INFO] Creating virtual environment with system site packages..."
    python3 -m venv --system-site-packages "$VENV_DIR"
fi

# Step 7: Activate virtual environment
echo "[INFO] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Step 8: Install project dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "[INFO] Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "[WARNING] $REQUIREMENTS_FILE not found. Skipping."
fi

# Step 9: Install uvicorn for FastAPI
echo "[INFO] Installing uvicorn server..."
pip install "uvicorn[standard]"

echo
echo "[SUCCESS] Environment setup complete!"
echo "[INFO] To activate the environment later, run:"
echo "       source $VENV_DIR/bin/activate"
echo "[INFO] To deactivate the environment, run: deactivate"
