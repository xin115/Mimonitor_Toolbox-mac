#!/bin/bash
set -e
python3 -m pip install -r requirements-build.txt
python3 -m PyInstaller --clean --noconfirm MonitorToolbox.mac.spec
echo "Done! Check dist/MonitorToolbox.app"
