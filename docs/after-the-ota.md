# If you took the latest OTA: what happened here, and the way back

This is the story of one R1 that took Rabbit's newest OTA, became hard to reach,
and was brought back to a booting, unlocked device with ADB by **returning to
rabbitOS v0.8.293**. It records what worked on that unit. It is not a promise
that the same steps are safe on yours.

## The short version

1. The unit took Rabbit's newest OTA, which the owner believes was **rabbitOS 3 (OS3)**;
   the exact build number wasn't recorded. Rabbit's own developer-mode unlock worked on it
   (the owner's report; see "Not written down yet" below).
2. Later the unit was taken back to **v0.8.293** with the official images.
3. That is when two separate problems appeared, and they need separate fixes:
   - a **boot loop** (a stuck dm-verity error flag in `seccfg`), and
   - **ADB that kept switching itself off**.
4. Both were fixed on v0.8.293. The device now boots, stays unlocked, and keeps ADB.

Nobody has shown that the OTA itself caused the loop. The notes say so
([recovery.md](recovery.md), [evidence.md](evidence.md)). What is known is the order
of events: unlock, OTA, flashing, then the loop.

## Which problem do you have?

| What you see | Most likely | Read |
|---|---|---|
| Boots normally, you want to unlock | Nothing is broken. Use Rabbit's own developer-mode flow. | [current-firmware.md](current-firmware.md) |
| Boot logo, "corruption" message, black screen, restart, even after restoring official images | The persistent `seccfg` verity flag | [recovery.md](recovery.md) |
| Boots, but ADB disappears after boot | Rabbit's boot code turning ADB off | [adb.md](adb.md) |
| Boots with ADB, wants a custom home screen | Disable the stock launcher and updater | [after-adb.md](after-adb.md) |

## Traps we hit, in the order we hit them

- **Restoring official images does not clear the loop.** The flag lives in
  `seccfg`, which stock restores don't write. This looked like a bad image for a
  long time.
- **Unlocking and disabling verification didn't clear it either.** AVB accepted
  the state while the bootloader still ran verity in error mode.
- **A loop does not prove anti-rollback.** It was considered and not demonstrated.
  It also isn't ruled out for other units, so treat any downgrade as unproven.
- **ADB gate.** Setting `ro.debuggable=1` was not enough. v0.8.293's `AdbService`
  disabled ADB at boot unless `ro.adb.force_enable=1` ([adb.md](adb.md)).
- **Rabbit's setup flow can bring the OTA back.** Owners report that finishing
  setup forces the update. We disabled the updater package instead.
- **Don't relock** while modified or verification-disabled images are installed.
- **Don't run `adb root`.** It dropped USB access until reboot.

## Before touching anything

- Write down the OS version, active slot and `fastboot getvar` output, with
  identifiers removed.
- Take a full read-only backup of `seccfg`, boot, vbmeta and the logical
  partitions, and keep your own way back to bootloader fastboot.
- Treat missing backups or a firmware mismatch as a stop condition.
- A corrected `seccfg` from another unit is not a substitute for generating one
  from your own ([recovery.md](recovery.md)).

## Not written down yet

The early recovery work was done with another AI tool, so these were never
recorded in this repository. They are open, not forgotten:

- the exact OS3 build number and the date of the OTA (believed to be rabbitOS 3);
- what exactly worked on it (unlock only, or ADB too);
- which tool and images were used to return to v0.8.293, and how the device was
  put into fastboot.

If you took the same OTA, record your own build number from Settings > Device info
before you change anything, and say so in any report.
