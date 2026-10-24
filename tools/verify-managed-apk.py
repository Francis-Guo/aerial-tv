#!/usr/bin/env python3
"""Verify the managed APK's signer, manifest and removed updater endpoints."""
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--build-tools", required=True, type=Path)
    parser.add_argument("--expected-cert-sha256", required=True)
    args = parser.parse_args()
    signer = run(str(args.build_tools / "apksigner"), "verify", "--verbose",
                 "--print-certs", "--min-sdk-version", "21", str(args.apk))
    certs = re.findall(r"Signer #\d+ certificate SHA-256 digest: ([0-9a-f]+)", signer)
    expected = args.expected_cert_sha256.replace(":", "").lower()
    require(certs == [expected], "Unexpected signing certificate")
    require("Verified using v1 scheme (JAR signing): true" in signer,
            "Android 6 requires a valid v1 signature")
    aapt = str(args.build_tools / "aapt2")
    badging = run(aapt, "dump", "badging", str(args.apk))
    require("package: name='app.orchard.tv'" in badging, "Unexpected package")
    require(re.search(r"^(?:sdkVersion|minSdkVersion):'21'$", badging, re.MULTILINE), "Unexpected minSdk")
    native = re.search(r"^native-code: (.+)$", badging, re.MULTILINE)
    require(native is None or "'armeabi-v7a'" in native.group(1),
            "Native libraries do not support this ARMv7 TV")
    require("launchable-activity: name='app.orchard.tv.MainActivity'" in badging,
            "Missing launchable activity")
    manifest = run(aapt, "dump", "xmltree", str(args.apk), "--file", "AndroidManifest.xml")
    for forbidden in ("REQUEST_INSTALL_PACKAGES", "android.permission.INSTALL_PACKAGES",
                      "androidx.core.content.FileProvider", "update_files"):
        require(forbidden not in manifest, "Unexpected manifest entry: " + forbidden)
    require(not re.search(r"android:debuggable[^\n]*0xffffffff", manifest),
            "Release must not be debuggable")
    banned = [b"aerial.qust.me/download/", b"aerial.qust.me/update/",
              b"pengchujin/aerial-tv/releases/latest/download/",
              b"check_update", b"update_test", b"Lapp/orchard/tv/update/Updates;"]
    with zipfile.ZipFile(args.apk) as archive:
        dex_names = [n for n in archive.namelist() if re.fullmatch(r"classes\d*\.dex", n)]
        require(bool(dex_names), "APK contains no DEX")
        for name in dex_names:
            data = archive.read(name)
            for forbidden in banned:
                require(forbidden not in data, "Updater marker remains: " + forbidden.decode())
    print(json.dumps({"apk": args.apk.name,
                      "sha256": hashlib.sha256(args.apk.read_bytes()).hexdigest(),
                      "certificate_sha256": certs[0],
                      "package": badging.splitlines()[0],
                      "checked_dex_files": len(dex_names),
                      "checks": "signature including v1, package, minSdk, ARMv7, manifest, updater markers",
                      "result": "PASS"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
