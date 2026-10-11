# Generated image storage — measured 10 October 2026

These are logical file sizes, not a claim about APFS physical space. Compression,
clones/shared extents and filesystem overhead may make physical use different.

| Item | Measured storage |
| --- | ---: |
| 17 retained synthetic trial PNGs and JSON metadata in repository evidence | 17,724,060 bytes (17.72 MB) |
| Copies in the two private trial worker folders | 17,724,060 bytes (17.72 MB) |
| Combined retained trial output copies | 35,448,120 bytes (35.45 MB) |
| Generation output plus metadata, observed median | 1,114,190 bytes (1.11 MB) |
| Observed generation range | 370,114–1,767,199 bytes (0.37–1.77 MB) |
| One reference edit, full PNG plus metadata | 1,379,509 bytes (1.38 MB) |
| Shared pinned model snapshot, 18 files | 15,980,140,843 bytes (15.98 GB) |
| Shared private image-worker environment, unique non-symlink files | 1,092,409,741 bytes (1.09 GB) |

An edited image or a new generation version is a **complete PNG**, not a small
change file. Keeping the original plus ten versions means eleven output files.
At this sample median, 1,000 outputs would be about 1.11 GB; this is an estimate,
and output content/compression changes the size. The weights and worker environment
are shared once; they are not copied per image, revision or deployment.

The repository samples and private copies are retained evaluation evidence, not
user images imported into the app gallery. No existing image evidence was deleted.
The environment figure excludes interpreter symlink targets. These measurements
inspect only the named trial locations, not all files on the Mac.

## Product accounting and retention

Images separates PNG bytes, downloadable JSON bytes, request manifests, shared app
SQLite/WAL bytes, image-backup bytes and disk free space. Each gallery card reports
its complete output size. New versions retain a link to the originating job; they
do not overwrite its files. Prompt reuse creates a new full generation, not a
reference-conditioned edit; reference uploads/editing remain a later file-handling
checkpoint.

Remove one output or all saved outputs from Images after confirming the count and
size. Active jobs cannot be deleted. This removes PNGs and downloadable details;
job history/inputs, chats, model weights and existing backups remain. Backup copies
can therefore continue to occupy space after deleting a gallery output, until the
last seven retained database snapshots no longer reference it.

Automatic image companions store PNG/JSON files by SHA-256 and one manifest per
database snapshot. Unchanged files are shared across backups, rather than copied
seven times. The offline restore command verifies the paired database digest,
complete artifact coverage, every blob digest and PNG/metadata before restoring
into a **new** directory. Model weights are excluded.

Measurements: `artifacts/images-i1/storage-measurement.json` and
`artifacts/images-i1/private-storage-measurement.json`.
