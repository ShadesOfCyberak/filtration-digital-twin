#!/usr/bin/env python3
"""
Convenience entry point for the ESP32 Mock Telemetry Generator.
Runs `backend/scripts/mock_esp32_device.py`.
"""
import os
import sys

# Ensure backend directory is in path
script_dir = os.path.dirname(os.path.abspath(__file__))
mock_script = os.path.join(script_dir, "backend", "scripts", "mock_esp32_device.py")

if __name__ == "__main__":
    import subprocess
    cmd = [sys.executable, mock_script] + sys.argv[1:]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass
