#!/bin/bash

# ===============================
# Drowsiness Detection Setup Script for Raspberry Pi OS
# ===============================

VENV_DIR="venv"
PYTHON_VERSION="3.10"
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

# Step 1.5: Ensure pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "[INFO] pyenv not found. Installing pyenv..."

    # Install pyenv via pyenv-installer
    curl -fsSL https://pyenv.run | bash

    # Add pyenv to .bashrc if not already present
    if ! grep -q 'pyenv init' ~/.bashrc; then
        echo -e '\n# Pyenv initialization' >> ~/.bashrc
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
        echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
        echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
        echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
        echo 'eval "$(pyenv init - bash)"' >> ~/.profile
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
        echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
        echo 'eval "$(pyenv init - bash)"' >> ~/.bash_profile
    fi

    echo "[INFO] pyenv has been installed. Please restart your terminal by 'exec $SHELL' or run 'source ~/.bashrc' to finalize the installation."
    exit 0
fi

# Step 2: Load pyenv (IMPORTANT for script usage)
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

if command -v pyenv >/dev/null 2>&1; then
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
else
    echo "[ERROR] pyenv is not installed or not in PATH."
    echo "        Please install pyenv and ensure it's configured in your shell before running this script."
    exit 1
fi

# Install dependencies for building Python
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git

# Step 3: Install desired Python version if not installed
if ! pyenv versions --bare | grep -q "^${PYTHON_VERSION}\$"; then
    echo "[INFO] Python $PYTHON_VERSION is not installed. Installing with pyenv..."
    pyenv install -v "$PYTHON_VERSION"
fi

# Step 4: Set Python version for this shell
echo "[INFO] Setting Python $PYTHON_VERSION for this shell session..."
pyenv shell "$PYTHON_VERSION"

# Step 5: Confirm Python version
PY_VERSION=$(python3 --version)
echo "[INFO] Current Python version: $PY_VERSION"

# Step 6: Install libcamera system packages
echo "[INFO] Installing Raspberry Pi camera libraries..."
sudo apt install -y python3-libcamera libcamera-dev

# Step 7: Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "[INFO] Virtual environment already exists. Skipping creation."
else
    echo "[INFO] Creating virtual environment with system site packages..."
    python3 -m venv --system-site-packages "$VENV_DIR"
fi

# Step 8: Activate virtual environment
echo "[INFO] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Step 9: Install project dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "[INFO] Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "[WARNING] $REQUIREMENTS_FILE not found. Skipping."
fi

# Step 10: Install uvicorn for FastAPI
echo "[INFO] Installing uvicorn server..."
pip install "uvicorn[standard]"

echo
echo "[SUCCESS] Environment setup complete!"
echo "[INFO] To activate the environment later, run:"
echo "       source $VENV_DIR/bin/activate"
echo "[INFO] To deactivate the environment, run: deactivate"
