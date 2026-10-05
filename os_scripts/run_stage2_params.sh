#!/bin/bash
cd "$(dirname "$0")/.."
./run.sh --vfs vfs/minimal.zip --script scripts/test_stage2.txt
