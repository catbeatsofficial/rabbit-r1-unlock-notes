# After ADB: living with an R1 you can reach

Written 2026-10-31 from about three days of daily use of one unit, after the
[recovery](recovery.md) and the [ADB fix](adb.md). The same device and firmware
caveats apply: rabbitOS v0.8.293 base, Android 13, MT6765.

## What the device looks like now

- **ADB stays up** across reboots, over USB and over Wi-Fi on port 5555.
  `ro.adb.force_enable=1`, `ro.adb.secure=0` (no key prompt), and
  `persist.sys.usb.config=adb` are all set.
- **No Rabbit apps run.** Judy, RabbitLauncher and R1SystemUpdater are renamed
  `.off` in the system image. With the updater gone, nothing pulls an OTA. Don't
  finish Rabbit's setup flow on a device you want to keep: owners report that it
  forces the OTA.
- **Home is whatever you install.** With RabbitLauncher off, Android's
  FallbackHome takes over until another app declares a HOME activity. We run our
  own WebView launcher (catbeats CuteOS, a separate project).

## Everyday ADB

```sh
adb devices                                   # USB
adb connect <r1-ip>:5555                      # Wi-Fi, once it's on the same network
adb connect adb-<serial>._adb._tcp            # Wi-Fi by mDNS name, no IP needed (when mDNS resolves)
adb install -r -g your-launcher.apk           # -r keeps app data, -g grants runtime permissions
adb reboot
```

- Port 5555 with `ro.adb.secure=0` means **anyone on the same network can get a
  shell**. That's fine for a home network toy; don't take it onto public Wi-Fi like this.
- **Never run `adb root`.** It restarts adbd, and on this build adbd doesn't come
  back until a reboot (see [adb.md](adb.md) for the gadget detail).
- If mDNS names stop resolving on macOS, the IP form still works.

## A launcher of your own

Any APK with this in its manifest becomes a Home candidate:

```xml
<intent-filter>
  <action android:name="android.intent.action.MAIN" />
  <category android:name="android.intent.category.HOME" />
  <category android:name="android.intent.category.DEFAULT" />
</intent-filter>
```

Install it, then press Home once (or reboot) and pick it. Things we learned:

- **Hardware keys:** the side button and the scroll wheel arrive as ordinary key
  events in the foreground activity; the wheel arrives as a stream of up/down notches.
- **Shell-only actions from the app:** some useful switches (`cmd wifi`, Bluetooth
  unpairing, USB data role for a USB-C audio interface) need shell (uid 2000),
  not an app uid. With TCP ADB on, an app can open an ADB connection to
  `127.0.0.1:5555` and run them as shell. It's powerful and blunt; keep the
  command list fixed and never pass user text straight through.
- **Camera motor:** the R1's rotating camera is driven through a sysfs file whose
  SELinux rule only allowed factory and platform apps. Our vendor image swaps that
  rule for `untrusted_app` (see the build notes in [adb.md](adb.md)); without it, a
  normal app can use the camera but can't turn it.
- **Screen:** there's no system lock screen in this setup. Our launcher keeps the
  screen on and draws its own sleep/wake (with an unlock animation), dimming the
  backlight to 0.

## Power and charging quirks

- **Eight quick presses** of the side button power the R1 off.
- It often boots into a **charging screen** when plugged in; **hold the side button
  about 3 s** to boot Android.
- The battery is about 1,000 mAh. Bus-powered USB gear (we tried a 500 mA audio
  interface) drains it quickly; a PD pass-through hub is the next thing to try.

## Keeping it recoverable

- Keep your stock `super` (or system/vendor) images, your own `seccfg` backup and
  your boot images somewhere off the device before changing anything.
- Every image we flashed was built as a **same-size, same-layout edit** of stock
  and verified by reading it back. Keep stock images ready to flash back.
- Don't relock the bootloader with modified images installed.
