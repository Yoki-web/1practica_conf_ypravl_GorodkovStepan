#!/bin/bash
cd "$(dirname "$0")/.."
python3 scripts/create_test_vfs.py
./run.sh --vfs vfs/minimal.zip --script scripts/test_stage3.txt
