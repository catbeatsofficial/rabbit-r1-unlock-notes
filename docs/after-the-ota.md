# If you took the latest OTA: what happened here

One R1 was unlocked, took a newer Rabbit OTA overnight, and could not boot Android
afterwards. The only public firmware, v0.8.293, was about 14 months older than what
the unit had been running, so "going back" meant flashing that older firmware.
It looped too. Two separate problems were hiding behind that loop, and they needed
separate fixes. This page is the timeline from the working handoff notes. It records
one unit. It is not a promise that the same steps are safe on yours.

## Timeline (October 2026)

1. **Starting point.** The unit ran rabbitOS 2.3.x (July 2026) plus a September 2026
   OTA. Rabbit's own **OS3 developer-mode** flow plus `fastboot flashing unlock`
   unlocked it, and it booted fine (orange state).
2. **The OTA.** The next morning it had taken a further rabbitOS 2.x OTA overnight.
   The working theory was that this OTA **re-locked the bootloader and wrote newer
   low-level firmware**. That was an inference, not something we confirmed.
3. **First failures.** One trip into fastbootd, then a reboot. A normal boot was never
   verified after that. A patched debug boot image looped; restoring the stock one
   still looped. The loop may have started before the patch.
4. **Going back to v0.8.293.** A web flash died mid-upload (a WebUSB error). A command-line
   flash of every piece reported OK and still looped. A complete official web flash
   finished cleanly, **re-locked** the bootloader, and still looped.
5. **Diagnosis.** Crash logs showed `lock_state=0x4` (locked), verity mode `eio` and
   `managed=yes`. Unlocking again didn't help, and fastbootd never came up, the same
   symptoms as [r1_escape issue 96](https://github.com/RabbitHoleEscapeR1/r1_escape/issues/96).
6. **What was ruled out.** Bad image files (hashes matched a known-good list), a partial
   flash, verified boot on or off, a locked bootloader, leftover newer boot pieces, and a
   stuck boot command.
7. **The fix.** A persistent dm-verity error in `seccfg`, which stock restores never
   write ([recovery.md](recovery.md)). After a repair verified by full readback, Android
   booted. ADB then needed its own fix ([adb.md](adb.md)).

## What we don't know

- The exact build number of either OTA. The notes record only "rabbitOS 2.x" and the
  months. (The owner remembers it as the OS3 generation; the unlock flow is called OS3
  developer mode.)
- Whether the OTA re-locked the unit, or whether the official web flash did. Both
  happened before anyone checked.
- Whether fused anti-rollback was involved. It was the leading theory at first and was
  never demonstrated. It also isn't ruled out for other units.
- What first set the verity flag.

## Which problem do you have?

| What you see | Most likely | Read |
|---|---|---|
| Boots normally, you want to unlock | Nothing is broken. Use Rabbit's own developer-mode flow. | [current-firmware.md](current-firmware.md) |
| Boot logo, "corruption" message, black screen, restart, even after restoring official images | The persistent `seccfg` verity flag | [recovery.md](recovery.md) |
| Boots, but ADB disappears after boot | Rabbit's boot code turning ADB off | [adb.md](adb.md) |
| Boots with ADB, wants a custom home screen | Disable the stock launcher and updater | [after-adb.md](after-adb.md) |

## Lessons for someone who just took the OTA

- **Don't flash the public v0.8.293 images over a newer firmware to "go back".** That is
  what led to the loop here. We don't know that it was the cause, and a downgrade may not
  be safe on your unit.
- **Restoring official images does not clear a verity loop.** The flag lives in `seccfg`.
- **A full official web flash re-locks the bootloader.** Check `fastboot getvar unlocked`
  afterwards, and don't relock while modified images are installed.
- **Rabbit's setup flow can force the OTA.** We disabled the updater package instead.
- **Back up first.** Read-only copies of `seccfg`, boot, vbmeta and the logical partitions,
  plus your own way back to bootloader fastboot. Record your OS build number from
  Settings > Device info before you change anything.
- **Don't run `adb root`.** It dropped USB access until reboot.
