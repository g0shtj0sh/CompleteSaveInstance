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
