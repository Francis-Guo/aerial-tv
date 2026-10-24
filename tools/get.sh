#!/usr/bin/env bash
set -euo pipefail
echo "This managed fork does not run remote installers or download APKs." >&2
echo "Use a verified local APK and official ADB; see docs/MANAGED-BUILD.zh-CN.md." >&2
exit 1
