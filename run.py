import subprocess
import sys
import platform

def install_requirements():
    python_cmd = sys.executable
    subprocess.check_call([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"])

def run_streamlit():
    python_cmd = sys.executable
    # Run streamlit through python -m to avoid path issues
    subprocess.check_call([python_cmd, "-m", "streamlit", "run", "main.py"])

if __name__ == "__main__":
    try:
        install_requirements()
        run_streamlit()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(0)