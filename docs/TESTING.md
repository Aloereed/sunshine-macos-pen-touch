# Validation record

## Environment and identity

- Host: Intel NUC8i7BEH, x86_64 macOS 26.7.1 (25G241), Apple clang 21 / Command Line Tools SDK.
- Sunshine base: v2026.914.233613, commit 63d35f702ee9e362e43263742981836ec0710384.
- Library review base: 45c9b4db05779d18224a751e33cb8dfea78201bb; runtime backport base: 53e1a949fc0784af716b782ddfa6c647cafd1f05.
- Drawing application: Krita 5.3.4.1; independent Qt tablet-event test window also used.
- Main virtual display with HiDPI enabled; 2560×1440 streaming at 60 FPS.
- Tested application executable SHA-256: 1ca1ef7e080975a75fa7563e9a12db0cc4b6cbb82eae52fc77f511951f70bcb2.

## Executed automated checks

| Check                                      | Result                                               |
| ------------------------------------------ | ---------------------------------------------------- |
| libvirtualhid full suite                    | 141 run; 139 passed; 2 Linux hardware tests skipped    |
| macOS backend subset                       | 23 passed, including 9 new pen tests                  |
| Initial Sunshine filtered suite            | 30 passed, including the button-only regression       |
| Final touch/session filtered suite         | 22 passed, including 4 added regression tests         |
| Backend to AppKit to Qt local conversion   | 85 events; pressure through approximately 0.95        |
| Patch application to recorded clean bases  | Passed; see ../patches/manifest.json                       |

The two Sunshine filters overlap; their counts must not be added together as a unique total. The final filtered test log contains stale GCDA counter merge warnings after rebuilding. Assertions passed, but these logs do not establish a coverage percentage. No full cross-platform Sunshine CI or new test run during documentation assembly is claimed.

Library tests exercise availability, device state, pressure, hover/contact transitions, invalid values, tool identity, tilt conversion and button cleanup. Sunshine regressions cover button-only packets, retained-device reset, finger ownership/cancellation, invalid coordinates, pen priority and requiring a fresh finger DOWN after pen contact.

With each repository configured using its normal macOS build dependencies:

```sh
# libvirtualhid
cmake --build cmake-build-pen --target test_libvirtualhid
cmake-build-pen/tests/test_libvirtualhid

# Sunshine
cmake --build cmake-build-pen --target sunshine test_sunshine
cmake-build-pen/tests/test_sunshine --gtest_filter='VirtualHidDeviceTest.*:InputGamepadSessionTest.*'
```

## Manual acceptance, 2026-10-24

The tester confirmed pressure-sensitive drawing, finger clicking and window dragging all work with the final server build. This is user-reported hardware verification, not an automated UI assertion. An earlier independent receiver snapshot contained 866 cumulative Tablet events with maximum pressure approximately 0.806; it is supporting historical evidence, not a fresh measurement of the final acceptance session.

The local Qt conversion probe directly delivered backend events to the process's native view. It confirms event interpretation, including Pen/Eraser and tilt (15°, −30°), but by itself does not test global WindowServer delivery or network input.

## Limits and further verification

- Real-device confirmation does not yet cover tilt, eraser, side buttons, repeated reconnect stress or prolonged palm-contact scenarios.
- Single-finger emulation is main-display only. Multi-monitor, rotated displays and alternative HiDPI layouts need hardware validation.
- No hardware multitouch, two-finger gestures, right-click gesture or physical HID device registration is added.
- Pen-contact arbitration is state-based, not hardware palm rejection.
- Zero-pressure contact, unknown pressure sentinels and cancel paths have tests; further application interoperability remains appropriate before release.
