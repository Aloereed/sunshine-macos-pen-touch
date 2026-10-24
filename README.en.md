# macOS pen pressure and single-finger input for Sunshine

[中文](README.md) · [Build and installation](docs/INSTALL.md) · [Validation](docs/TESTING.md)

Community source patches for Sunshine and libvirtualhid. Pressure-sensitive drawing, finger clicks and window dragging were confirmed together on an Intel macOS host on 2026-10-24. This is not an official Sunshine release and no prebuilt application is provided.

The patches add CoreGraphics tablet events, logical display bounds for HiDPI pen coordinates, button-only packet handling, single-finger mouse emulation and session-state cleanup. Pen contact takes priority over an emulated finger drag.

This is not a registered HID tablet or native macOS multitouch. The finger fallback targets the main display; two-finger gestures and hardware palm rejection are not implemented. Real-device validation covers pressure, clicks and dragging. Tilt, eraser identity and side buttons have automated/local event coverage only.

## Reproduce

1. Clone Sunshine at `63d35f702ee9e362e43263742981836ec0710384` and initialize its submodules.
2. Run `python3 scripts/apply-patches.py /path/to/Sunshine --check-only`, then without `--check-only`.
3. Follow the [installation guide](docs/INSTALL.md) to build Sunshine **and its Web UI**, then stage a separate signed application with `scripts/stage-app.py`.
4. Grant macOS Accessibility and Screen Recording permissions, stop your existing Sunshine service, and test the new application before changing automatic startup.
5. To roll back, stop the test app and restore the original Sunshine application/service path.

The helper checks exact commits and SHA-256 hashes before applying the two runtime patches. `libvirtualhid-macos-pen.patch` is a separate developer patch against a newer library base; do not apply it in addition to the pinned-library runtime patch. See `patches/manifest.json`.

The documented Homebrew build route was derived from the pinned upstream build files. The successful hardware build used isolated dependency prefixes; the Homebrew route is not claimed as a fresh-machine end-to-end validation. Apple Silicon, older macOS versions and multi-monitor input remain unverified.

## Licensing and attribution

Based on [Sunshine](https://github.com/LizardByte/Sunshine) and [libvirtualhid](https://github.com/LizardByte/libvirtualhid). Sunshine-derived patches are GPL-3.0; the relevant libvirtualhid non-driver components are MIT. See [LICENSE.md](LICENSE.md). No proprietary broker is included or modified.

OpenAI Codex assisted implementation, debugging and documentation. Hardware acceptance was provided by a human tester.
