# Recovery: a persistent error outside the stock images

## 1. Starting point and unlocking

The device initially booted normally. Developer mode on its then-current OS
was used to reach fastboot and permit `fastboot flashing unlock`; it booted
after that unlock. An OTA and later flashing experiments preceded the loop.
The exact earliest cause of the loop was not established. This is not a
recommendation to take an OTA or downgrade another working device.

Unlocking wipes data on devices that follow the normal Android flow. It is
separate from ADB enablement and from Android root. In this case, fastboot
subsequently reported `unlocked: yes`, `secure: no`, with slot A selected.
The official restore also re-locked the device during the investigation;
the later diagnostic/repair state was unlocked again.

Use Android platform-tools and inspect your own device state before writing:

```sh
fastboot devices
fastboot getvar unlocked
fastboot getvar secure
fastboot getvar current-slot
fastboot getvar is-userspace
```

Bootloader fastboot and userspace **fastbootd** are different. A response of
`is-userspace: yes` identifies fastbootd. In our case logical system/vendor
updates later used fastbootd; bootloader fastboot was available even while
Android could not start.

## 2. The loop

Symptoms were the boot logo, corruption message, black screen and restart.
Restoring the official v0.8.293 images did not clear it. Unlocking and disabling
verification did not independently solve it either. Fresh boot evidence showed
AVB accepting the unlocked/verification-disabled state while LK still passed
managed verity in error mode. This distinguished a persistent error record
from a proven rollback-index failure.

Do not conclude that a loop proves fused anti-rollback, or that this recovery
disproves anti-rollback on other devices or firmware combinations.

## 3. Read-only diagnosis first

The useful local backups were `expdb` (historical and fresh boot logs), `seccfg`,
`para`, the active `boot` and `vbmeta`. Other read-only captures helped confirm
which firmware was actually installed. Do not publish raw dumps: they can
contain device identifiers or other unrelated data.

Upstream mtkclient connected through preloader serial mode (`--serialport` in
the local checkout), not its default USB path. Use the syntax reported by
your pinned checkout's help; transport options can change between versions.
The original test used a Python environment with pyserial and the dependencies
required by that checkout. No third-party mtkclient source is bundled here.

In the captured V4 `seccfg`, the first seven little-endian words were:

| Offset | Meaning in this tested build | Before | After |
|---|---|---:|---:|
| `0x00` | magic | `0x4d4d4d4d` | unchanged |
| `0x04` | structure version | `4` | unchanged |
| `0x08` | authenticated header size | `60` | unchanged |
| `0x0c` | lock state | `3` (unlocked) | `3` |
| `0x10` | dm-verity error state | `1` | `0` |
| `0x14` | runtime field | `0` | unchanged |
| `0x18` | end marker | `0x45454545` | unchanged |

There was also a named `avb.managed_verity_mode` record in the region
`[0x240, 0x2c0)`. The full partition was 8 MiB. These offsets describe this
specific validated structure; do not apply them to a different format.

## 4. What was actually repaired

The successful operation preserved the device's own full backup and changed:

1. The header's dm-verity state to zero while retaining unlocked state 3.
2. The authenticated header data, regenerated using mtkclient and the device's
   crypto engine. Local detection selected crypto type **V4**. Another write-up
   mentions another path; do not force its crypto type on this device.
3. The managed-verity record at `0x240` through `0x2bf`, cleared to zero.

The preparation stage was deliberately prevented from calling flash write or
erase handlers. It parsed/authenticated the original, generated the corrected
header, validated the candidate with device crypto again, and verified that
every changed byte was in the intended regions. The full candidate differed
from the original by only **94 bytes**.

The separate write stage re-read the current partition and refused to write
unless it exactly matched the reviewed original backup. It wrote **seccfg
only**, then read back all 8 MiB and compared the result byte-for-byte with
the candidate. Both the write result and full readback were successful.

### Reproducing the preparation logic

The local mtkclient checkout was commit
[`118a000a83ea31c4f427fe5225abfe964546e05e`](https://github.com/bkerler/mtkclient/tree/118a000a83ea31c4f427fe5225abfe964546e05e).
Its tracked files were unmodified. The adapter used `XFlashExt.cryptosetup()`
and `SecCfgV4` from that checkout. The essential logic was:

```python
# Fragment inside an established XFlash context, not a standalone script.
# original is this unit's full, freshly read partition backup.
sc = SecCfgV4(ext.cryptosetup(), ext.mtk, ext.custom_sej_hw)
assert sc.parse(original)                    # authenticate, detect crypto path
assert sc.lock_state == 3 and sc.dm_verity_state == 1
sc.lock_state = 4                           # RAM only: bypass already-unlocked guard
sc.dm_verity_state = 0
ok, header = sc.create(lockflag="unlock", critical=False)
assert ok and len(header) == 512
candidate = bytearray(original)
candidate[:60] = header[:60]                 # authenticated structure only
candidate[0x240:0x2c0] = bytes(0x80)          # reviewed record region only
check = SecCfgV4(ext.cryptosetup(), ext.mtk, ext.custom_sej_hw)
assert check.parse(candidate)               # authenticate corrected data
assert check.lock_state == 3 and check.dm_verity_state == 0
```

The temporary `lock_state=4` assignment happened only in the parsed Python
object, because `create(unlock)` otherwise returned “already unlocked.” The
generated header was checked to retain state 3; state 4 was never written.
The preparation adapter also explicitly rejected write/erase calls in the
transport layer. Retain those protections, full-layout checks and changed-byte
checks if implementing your own adapter. Do not run the normal unlock writer
and assume it is equivalent to this preparation-only operation.

Before a separate writer is allowed to run, validate length, all header words,
the cleared record and the allowed diff ranges (`0x10..0x13`, `0x1c..0x3b`,
`0x240..0x2bf` in this structure). The writer must use GPT-derived partition
bounds, re-read and compare the original immediately before writing, then
verify a full readback. This repository's inspector performs none of that
device-side authentication or writing.

A blind hex edit is insufficient because the header authentication must also
be regenerated. A corrected dump from someone else's unit is not a substitute
for generating and validating a candidate from your own unit. This repository
intentionally does not ship the original device-bound writer or its hashes
as a universal repair tool.

After repair the device reached orange-state warning, fastbootd, then Rabbit
setup. Orange state is expected with an unlocked bootloader. No preloader,
slot-B partition, LK, or vbmeta write was part of this **repair operation**.
Earlier stock-restore attempts had touched additional partitions; do not
confuse that history with the minimal operation that finally fixed the loop.

## 5. macOS and physical-device details

- Preloader appeared as USB `0e8d:2000`; fastboot as `0e8d:201c`.
- The preloader accepted ASCII `FASTBOOT` over serial to enter fastboot. See
  the credited recovery account for that transport technique.
- Browser flash tools could hold the USB interface; quitting them released it.
- A successful mtkclient capture could leave the device paused on a black
  screen. That alone did not mean a new brick.
- Eight quick side-button taps shut down our device, which made preloader
  capture easier. This is an observed behavior, not a universal reset recipe.
- Cold boot on USB sometimes showed charging mode; holding the side button
  about three seconds continued into Android.
- The automation sandbox could inspect files but not open USB or an ADB server
  listener. Ordinary Terminal could. This was a host-access constraint.

Do not repeatedly write unrelated partitions to chase USB access problems.
If the device now boots, stop the recovery work and move to ADB diagnosis.
