# Evidence and limits

These notes derive from local build reports, full readbacks, captured logs and
physical observations from one R1. Raw private dumps/logs are not distributed.

## Verified in this case

- A working fastboot interface existed during the corruption loop.
- After unlocking, the bootloader reported unlocked and not secure.
- The original corrupted `seccfg` and its corrected candidate were each 8 MiB.
- The original unlocked V4 header had dm-verity state 1. The corrected header
  had state 0; the managed-verity record was cleared and the device-crypto
  authentication validated.
- Exactly 94 bytes differed; the rest of the full partition was preserved.
- The write-stage current-state check matched the reviewed original, and the
  full post-write readback exactly matched the candidate.
- The device subsequently booted into setup. Anti-rollback was not demonstrated
  as the cause of this loop.
- The final access configuration used stock v0.8.293 boot, modified stock-based
  system/vendor, unlocked bootloader and disabled active top-level vbmeta
  verification. The Android runtime was version 13 / SDK 33, even though older
  recovery property fragments mentioned version 12.
- Custom AdbService boot logic gated ADB on `ro.adb.force_enable`.
- Stable access after boot completion was an Android shell with uid 2000.

## Firmware reference hashes

Hashes here identify public stock inputs, not transferable device-bound repairs:

| Input | SHA-256 |
|---|---|
| Stock boot.img | `0480ffab24e208ca20e761ebc07c15c0992ee3c91a3f55377731fdec532ae30f` |
| Extracted stock system_a | `f7e97812b61b9c24ad4592942921dbbd3caef8c27c51162f6c340c52d87302bc` |
| Extracted stock vendor_a | `279dfbe260bc66f587729571f2e516750f46a06906650542e6618767b5dad42a` |

A hash match is an integrity check, not a compatibility guarantee.

## Other root reports

A separate [first-hand report](https://bentlybro.com/posts/rooting-the-rabbit-r1-two-days-from-a-dm-verity-brick-to-magisk-on-stock-rabbitos)
describes Magisk root on its author's R1. This repo records no Magisk result on
our unit; the report and our verified ADB shell must not be conflated.

## Not established

- Persistent Android root, a tested Magisk setup, or reliable `adb root`.
- Support for other firmware revisions or every R1 hardware revision.
- A universal safe firmware downgrade path.
- Whether every compatibility setting retained in the final build was necessary.
- Whether disabling all three stock packages was required once force-enable was
  found. They were disabled in the final tested configuration.
- Device validation of a USB-only/authenticated variation of that configuration.
- The precise initiating event in the earlier corruption loop.

Third-party recovery accounts are credited separately. Their offset layouts,
crypto paths and reports of partial-write outcomes are not substituted for
our verified full-readback result.
