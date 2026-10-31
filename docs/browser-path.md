# Toward a browser-based path (plan, not built)

Owners shouldn't need Python, Homebrew and a terminal to get to Android on their R1.
This is a feasibility sketch for doing as much as possible from a web page over
WebUSB in Chrome. **Nothing here is implemented or tested yet.**

| Step | In the browser? | Notes |
|---|---|---|
| Developer mode + unlock request | Already web | Rabbit's own [developer-mode/unlock flow](https://www.rabbit.tech/support/article/unlock-bootloader-rabbit-r1) |
| `fastboot flashing unlock` | Likely | WebUSB fastboot implementations exist (e.g. the approach used by Android's web flash tools) |
| Flash prepared system/vendor images | Likely, but heavy | fastboot over WebUSB can flash; the images are GBs, so the page should patch the owner's own stock images locally rather than host modified firmware |
| Build the ADB edits in-page | Plausible | Our edits are same-length byte replacements inside ext4 file data; the reader/patcher could run in WebAssembly or plain JS on the owner's stock image |
| `seccfg` verity repair (only if stuck in the verity loop) | Hard | Needs MediaTek BROM/XFlash access and the device's own crypto (we used mtkclient). Rabbit's [official web flasher](https://rabbit-hmi-oss.github.io/flashing/) shows BROM-level flashing from a browser is possible, but porting the authenticated header regeneration is a project of its own |
| Install a launcher / apps | Yes | WebADB-style clients can `adb install` once ADB is up |

Principles for building it:

- Never host modified firmware. The page reads the owner's own downloaded stock
  image, verifies its hash against a known value, applies the documented edits,
  and verifies again before flashing.
- Read back after every write, keep a before-image, and refuse to continue on any mismatch.
- Say plainly which steps can brick a device and which only touch user data.
