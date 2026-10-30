# Developer mode, unlock and root on a recently updated R1

Checked against Rabbit's live support instructions on 2026-10-30. The exact
version of the newest OTA and a matching public image set were not verified in
this project. The latest **public GitHub recovery package** shown then was
v0.8.293; it must not be assumed to match a newer installed OTA.

## For a device that still boots

1. Record the r1OS version in the device's Settings > Device info, its active
   slot and the firmware provenance. Keep this information private if it
   contains identifiers. Obtain a complete backup of the device's *current*
   boot, vbmeta and logical partitions before considering a patch. Keep a
   known way back to bootloader fastboot.
2. In OS3, link the r1, then open Settings > r1 > Developer mode. Complete
   Rabbit's warranty acknowledgement and IMEI step on the account page. The
   owner must do this step themselves. With the r1 powered on and online,
   choose Device modification > Unlock. See [Rabbit's current instructions](https://www.rabbit.tech/support/article/unlock-bootloader-rabbit-r1).
3. Enter bootloader fastboot with the [official flash tool](https://rabbit-hmi-oss.github.io/flashing/)
   or a method validated for the current device. Check `fastboot devices`,
   `fastboot getvar is-userspace`, `fastboot getvar unlocked` and
   `fastboot flashing get_unlock_ability` before a write. Then use
   `fastboot flashing unlock` and follow the device's confirmation. The
   standard unlock path can wipe user data. Verify `unlocked: yes` afterward.
4. Stop here if bootloader access is the goal. Developer mode and bootloader
   unlocking do not grant an Android shell or root. Our tested ADB path is
   documented in [adb.md](adb.md) for **v0.8.293 only**. Inspect a newer
   firmware's USB init, AdbService and vendor services before adapting it.
5. For Magisk root, first identify where the **current firmware's** ramdisk
   lives and obtain that device/build's boot image. Follow [Magisk's installation
   guide](https://topjohnwu.github.io/Magisk/install.html) to patch a matching
   image on the device, retain the original and compare image metadata before
   flashing. Determine AVB state from the matching vbmeta before the patched
   boot is installed; a modified boot can trigger a dm-verity loop. A separate
   [first-hand R1 Magisk account](https://bentlybro.com/posts/rooting-the-rabbit-r1-two-days-from-a-dm-verity-brick-to-magisk-on-stock-rabbitos)
   achieved `uid=0` on its own firmware snapshot. **We have not reproduced
   that result on this device or on the newest OTA.** Use its sequence as an
   evidence source, not as a set of universal images or commands.

The v0.8.293 stock image and the system/vendor modifications in this repository
are not drop-in root packages for a newer OTA. Do not relock after installing
modified images. If a boot fails, preserve logs and read-only backups before
choosing a recovery path. See [recovery.md](recovery.md) for the separate
`seccfg` error we repaired on one unit.

## Agent workflow

An agent working on another owner's device should:

- Ask for the current OS/build, boot state, active slot, and *redacted* output
  of `fastboot getvar all`; never request an IMEI, full raw logs or signing keys
  in a public issue.
- Classify each command as read-only, bootloader unlock/wipe, or partition
  write. Present exact image hashes and target slots for review before a write.
- Verify that every input image belongs to the installed firmware. Treat a
  version mismatch or missing current backup as a stop condition.
- Keep a command log and after every write compare a full readback where the
  transport allows it. Do not infer root from `ro.debuggable`, unlocked state,
  or `adb shell id` showing uid 2000.
- For a boot loop, collect evidence first. The verity latch and repair described
  here were specific to one authenticated V4 `seccfg`; offsets and generated
  headers are not transferable to another unit.

References: [Rabbit developer mode](https://www.rabbit.tech/support/article/unlock-bootloader-rabbit-r1),
[Android unlock flow](https://source.android.com/docs/core/architecture/bootloader/locking_unlocking),
[public R1 firmware releases](https://github.com/rabbit-hmi-oss/firmware/releases),
[Magisk installation](https://topjohnwu.github.io/Magisk/install.html),
[first-hand R1 root account](https://bentlybro.com/posts/rooting-the-rabbit-r1-two-days-from-a-dm-verity-brick-to-magisk-on-stock-rabbitos).
