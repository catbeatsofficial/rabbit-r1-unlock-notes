# Publication scope

This directory is a standalone Git repository. Only its explicitly allowlisted
documentation and offline inspector belong in a public release. No parent
directory or parent history is part of this repository.

It contains no firmware binaries, partition dumps, raw logs, serial numbers,
network names/passwords, local user paths, signing keys, or application code.
Do not add those while preparing a release. Check filenames and text as well
as Git status before publishing; a `.gitignore` is not a secret scanner.

The firmware-specific write operations are described as a validated case study.
No automatically executing writer is included. The offline inspector has
synthetic fixture tests; that does not make it a repair or authentication tool.

Before publishing from this directory:

```sh
git status --short
git ls-files
git diff --cached --check
```

Review the tracked text and its claims. Set the intended GitHub owner/name and
license explicitly before creating the public remote. Nothing in this package
requires publishing any other local project.
