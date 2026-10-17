# Troubleshooting

## Source URL returns 404

The repository is public and no GitHub token is required. Confirm the exact
owner, repository, tag, and filename. The space in `Script Presets` must be
encoded as `%20` in a raw URL. Check your runtime's HTTP access and try a local
checkout when diagnosing network problems.

## Function returned, but no file exists

Find the runtime's actual workspace and test a small write/read cycle. Use a
unique `FilePath`. Check whether `Callback` or `CopyToClipboard` redirected the
output. A completed call or disappearing status message is not proof of a file.

## Disconnection, blank screen, or crash

`SafeMode` deliberately disconnects the client and can activate script
termination and rendering changes. Explicitly disable `SafeMode`,
`KillAllScripts`, `BoostFPS`, and `ShutdownWhenDone` for diagnosis.
A native process crash differs from a Lua exception; `pcall` cannot catch it.

Test a smaller selection. Record final console messages, elapsed time, memory
observations, runtime version, and whether a partial file exists. A crash alone
does not identify its cause.

## Frozen at “Saving… Size: …”

Use a current versioned preset. The size on the old status display can remain
unchanged during property and script extraction; it does not identify a disk
write or the operation causing a freeze.

Starting with 0.4.2, both preset profiles write
`<export-folder>/progress.json` in the runtime's file workspace while running.
The console prints its exact path. Preserve it with the final console messages
if the client stops responding; a final `report.json` may not exist yet.

- `phase: "scripts"`: `detail.operation` identifies bytecode or decompilation;
  `detail.path` identifies the script, including ModuleScripts.
- `read-property` / `encode-property`: inspect `detail.class` and
  `detail.property`; binary read checkpoints also include an index and total.
- `compress`: inspect the chunk, property, and byte count.
- `write`: serialization reached the output stage. This checkpoint alone does
  not prove the file was written successfully.

A checkpoint records the last announced operation, not a proven root cause.
It is written before each script job and compression call; other progress is
updated at phase changes and periodically while Lua is running. No script
source or bytecode is included in the checkpoint.

The primary engine now uses independent script jobs, memoizes bytecode reads,
and yields more frequently in collection and binary property reads. It skips
native compression for Source columns and chunks over 8 MiB, preserving their
uncompressed bytes. Final reports expose `scriptJobs` and `compression` counters.

Per-job deadlines can stop yielding jobs, and reject results returned after a
deadline. They cannot preempt native code that blocks the whole client. A total
freeze can therefore still require an executor-side fix. A fresh runtime test
and Studio inspection remain necessary.

## Low FPS while exporting

Use a preset pinned to 0.5.0 or newer for the progress panel and shorter Lua work
slices. `WorkBudgetMs` defaults to 4 ms; smaller values, down to 1 ms, can give the
game more scheduler time at the cost of export speed. Large binary loops now
yield between batches as well as during property reading. These settings do not
change the content selected by Ultra.

A native read/decompiler call, compression, or a large allocation can still block
rendering. Frame rate also includes the game's own workload. The exporter does
not change your FPS cap or graphics settings, and it cannot guarantee 60 FPS.
`BoostFPS` disables 3D rendering and is not the intended solution for keeping
the game playable during export; both Ultra presets leave it disabled.

The bar is for the named stage/property, not the whole export. For example,
`ModuleScript.Source · 500 / 4000` means 500 source entries have been processed;
it does not mean 12.5% of the total export time has elapsed.

## `PROP dropped` messages

The binary encoder can omit a property column when reading or encoding fails.
This does not by itself mean that the corresponding instances were omitted.
The `n` value must not be treated as a count of whole objects lost. Keep the
exact message, class, property, and source revision in reports. Precise failure
classification remains part of the planned audit.

## Studio cannot open the output

Preserve the failed file privately and record its size and format. Reproduce on
a small authorized place without decompilation or compression. Confirm that the
extension agrees with the selected format. Try XML as a separate diagnostic;
success there does not establish that the binary path was repaired.

## Missing content

Asset references do not embed asset binaries or grant permission to use them.
Streaming can leave parts of the world unavailable to the client. Server-only
scripts and private DataStores are outside client inspection. Property read
restrictions can omit data even when the instance is present.

## Useful bug reports

Include revision, runtime and Roblox versions, minimal options, exact console
messages, output location and size, and Studio's error. Share a reproduction you
have permission to distribute. Remove credentials and private content first.
