# Rabbit R1: from a verity loop to an unlocked device with ADB

An independently documented recovery of one Rabbit R1, followed by enabling
stable Android Debug Bridge access on stock-based firmware. Tested on
**rabbitOS v0.8.293, Android 13 / SDK 33, MT6765** in October 2026.

The result was an **unlocked bootloader and an ADB shell running as uid 2000**.
This is not a demonstrated Magisk installation or persistent root method.
`adb root` stopped working USB access until reboot in our tests.

## Start with your current device

[Developer mode, bootloader unlock and the route toward root on recent firmware](docs/current-firmware.md)
separates Rabbit's live account unlock procedure from the version-specific ADB
and Magisk work. It includes a checklist for agents working with another owner.

## After it works

- [Living with it](docs/after-adb.md): everyday Wi-Fi ADB, installing your own
  launcher as Home, the camera motor, power quirks and what to avoid (2026-10-31).
- [Toward a browser-based path](docs/browser-path.md): a plan, not yet built, for
  doing the unlock and ADB steps from a web page.

## Read in order

1. [Recovery and bootloader state](docs/recovery.md): the persistent `seccfg`
   dm-verity error that survived stock restores, and the repair that booted.
2. [Why ADB kept disappearing](docs/adb.md): the firmware's
   `ro.adb.force_enable` gate, USB defaults, and the final configuration.
3. [Evidence and limits](docs/evidence.md): verified observations, failed paths,
   and what remains unproven.

For an already booting device, the destructive recovery steps are unnecessary.
Unlocking the bootloader can erase user data. Firmware/partition writes can
prevent booting. Keep your own backups and recovery access before changing them.
Do not relock while modified or verification-disabled images are installed.

## What is included

Documentation and a read-only offline `seccfg` inspector. There is no automatic
flasher, firmware download, universal unlock script, or binary partition dump.
The inspector does not authenticate or repair a header and has no device IO:

```sh
python3 scripts/inspect-seccfg.py /path/to/your-own-seccfg-backup.bin
```

Run its synthetic, offline tests with `python3 scripts/test-inspector.py`.

These are build-specific findings from one device, not a promise that the same
offsets or firmware downgrade are appropriate for another unit. Anti-rollback
was considered during diagnosis but was not demonstrated as our blocker.

## Credits and upstream references

- [Official Rabbit firmware](https://github.com/rabbit-hmi-oss/firmware/releases)
  and [official web flasher](https://rabbit-hmi-oss.github.io/flashing/).
- [jonathanprocter's dm-verity recovery account](https://github.com/jonathanprocter/rabbit-r1-deverity-recovery/blob/main/docs/rabbit-r1-de-verity-recovery-community-writeup.md)
  supplied the key lead about persistent `seccfg` state. Our case was separately
  validated with a full partition readback.
- [David Buchanan's R1 boot notes](https://github.com/DavidBuchanan314/rabbit_r1_boot_notes)
  explain the boot chain and authenticated `seccfg` structure.
- [bkerler/mtkclient](https://github.com/bkerler/mtkclient) supplied the MediaTek
  transport, partition access and device-crypto implementation.
- [r1_escape issue 96](https://github.com/RabbitHoleEscapeR1/r1_escape/issues/96)
  records a similar corruption loop; similarity alone does not establish that
  every affected unit has the same underlying cause.

See [publishing notes](docs/publishing.md) for the scope of this repository.
