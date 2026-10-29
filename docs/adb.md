# Stable ADB on stock-based v0.8.293

## The decisive finding

Changing `ro.debuggable` alone did not keep ADB enabled. In the inspected
`services.jar`, custom `AdbService.systemReady` code disabled ADB on an
`IS_USER` build unless **`ro.adb.force_enable` was true**. The failing boot
logged `disable adb when boot`, cleared persistent USB configuration,
stopped adbd and set `adb_enabled=0`.

Adding `ro.adb.force_enable=1` to the stock-based system image was the decisive
change. The final boot reached `sys.boot_completed=1` with `sys.usb.config=adb`
and `adb_enabled=1`, and shell access remained available.

This describes code found in v0.8.293, not an assumption about newer Rabbit
releases. Inspect the firmware you actually intend to use.

## Configuration used in the successful experiment

All edits were built locally from the exact stock images. The boot image was
restored to **stock**. No patched kernel or persistent root manager was used.

| Location | Change | Purpose |
|---|---|---|
| system build properties | `ro.debuggable=1` | Debuggable property setting |
| system build properties | `ro.adb.secure=0` | Authentication disabled in this experiment |
| system build properties | `ro.adb.force_enable=1` | Prevent the custom boot-time ADB shutdown |
| system build properties | `persist.adb.nonblocking_ffs=0`, `ro.adb.nonblocking_ffs=0` | Retained compatibility settings from the tested build |
| vendor and ODM build properties | `persist.sys.usb.config=adb` | Set both defaults; ODM loads later |
| vendor USB init file | blank the `no_disconnect=1` mount option | Allow the FunctionFS gadget to detach on daemon close |
| system APK directory entries | Judy, RabbitLauncher, R1SystemUpdater renamed from `.apk` to `.off` | Disable the vendor ADB-reset service, stock home package and updater in the tested configuration |

The tested files were `/system/build.prop`, `/build.prop` and
`/odm/etc/build.prop` within their respective logical images, plus
`/etc/init/hw/init.mt6765.usb.rc` in vendor. Image-root paths differ from
mounted paths; resolve them in the actual filesystem rather than guessing.

APK paths in this stock build:

```text
/system/priv-app/Judy/Judy.apk
/system/app/RabbitLauncher/RabbitLauncher.apk
/system/priv-app/R1SystemUpdater/R1SystemUpdater.apk
```

Disabling the stock home package means you need another valid HOME activity
for a usable home screen. A stock fallback screen can appear until one is
installed. That is separate from whether Android and ADB have booted.

The private experiment also enabled unauthenticated TCP ADB on port 5555.
That permits anyone who can reach the port to issue shell commands. It is
**not required for the USB technique**, and should be omitted from a USB-only
build. Omitting it produces a variant we have not device-tested. Likewise,
keeping authentication enabled would be a useful separate variant, but is
not the configuration established by this experiment.

## Image preparation and verification

The local builder read Android sparse `super` and validated logical-partition
metadata checksums, resolved ext4 extents, and extracted system_a/vendor_a.
It used **same-length replacements** inside existing file data and APK
directory-entry names. New property lines replaced selected comment lines,
with trailing-space padding trimmed by Android init. `none` became `adb `.

For this exact ext4 layout, the metadata-checksum feature was absent. The
builder did not allocate blocks, resize files, or change extents/bitmaps.
It re-read all edited files through the filesystem reader and performed a
full byte comparison against stock, checking the diff matched the planned
patches. This is not permission to raw-patch another filesystem without
checking its features, metadata and checksums.

The original builder also accumulated later hardware-policy changes unrelated
to ADB. It is excluded here so this package contains only recovery/access work.
The table above records the access-specific changes rather than distributing
an unreviewed combined image or a one-click flasher.

## Installation conditions and rollback

The tested device remained unlocked, with top-level active vbmeta verification
disabled. Record the state of all related vbmeta partitions; do not generalize
this one configuration into a rule that lower-level verification is irrelevant.
Never relock this modified boot chain.

The successful installation sequence used stock boot_a, cleared userdata and
metadata to remove old persisted USB settings, then wrote the prepared logical
system_a/vendor_a through **fastbootd**, after confirming `is-userspace: yes`.
The data reset was destructive; do not repeat it on a working installation.
It is reported as part of the tested path, not proven necessary for all units.

Before any such change, extract and hash matching stock images for rollback,
keep copies of the original device state, and confirm how to re-enter fastboot.
Do not overwrite preloader or identity partitions as an ADB fix. If an image
fails to boot, restore the reviewed matching stock logical images via the
known-working transport; do not loop through speculative partition writes.

## Verify the result

From a normal terminal, once Android has finished booting:

```sh
adb devices -l
adb shell id
adb shell getprop sys.boot_completed
adb shell getprop ro.adb.force_enable
adb shell getprop sys.usb.config
adb shell settings get global adb_enabled
```

Our successful shell reported **uid 2000**, boot completed `1`, force-enable
`1`, USB config `adb`, and ADB enabled `1`. Leave the connection running through
boot completion; a connection that only survives the first minute is not a
successful fix. Reboot once and repeat the checks.

Do not use `adb root` as a verification command here. Restarting adbd as root
left USB ADB unusable until reboot. Debuggable settings and disabled ADB
authentication do not, by themselves, demonstrate root access.

## Failed paths worth avoiding

- A debug-ramdisk-only image did not enable ADB in this experiment.
- `fastboot boot` of stock and test boot images failed in the bootloader,
  before reaching the kernel; repeating RAM boots provided no new evidence.
- Disabling Judy alone did not establish the final fix.
- Disabling the stock home/updater packages alone did not establish it either.
- A still-enumerated USB interface could be a dead interface after adbd stopped;
  USB enumeration alone was not evidence that the daemon remained alive.
- The decisive evidence was the boot-time AdbService log and then stable access
  with the force-enable property. Earlier USB-wedge explanations were hypotheses.
