"""
Setup script for ScanLabel AI.
Installs all required dependencies.
"""

import subprocess
import sys
import os


def install_requirements():
    """Install requirements from requirements.txt"""
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found!")
        return False
    
    print("Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print("✓ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def main():
    """Main setup function."""
    print("=" * 60)
    print("ScanLabel AI - Setup")
    print("=" * 60)
    print()
    
    if install_requirements():
        print()
        print("=" * 60)
        print("Setup completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Train the model: python train_model.py")
        print("2. Run the API: uvicorn main:app --reload")
        print()
    else:
        print()
        print("Setup failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()








