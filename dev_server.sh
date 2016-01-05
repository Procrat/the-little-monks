#!/usr/bin/env bash

set -euo pipefail

rootdir="$(dirname $BASH_SOURCE)"
dev_appserver.py --log_level debug "$rootdir"
