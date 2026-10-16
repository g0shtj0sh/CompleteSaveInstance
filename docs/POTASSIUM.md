---
sidebar_position: 4
title: Potassium
---

import PresetLauncher from '@site/src/csi/PresetLauncher';

# Potassium edition

The dedicated entry point binds documented Potassium APIs to the shared
CompleteSaveInstance serializer. Choose a preset below and click **Copier le
script** to copy a complete runnable loader.

## UltraCompleteSveInstance

The current development target for maximum accessible coverage, with native
binary-property reads and the append-based writer enabled. A completed run
does not establish that all place content was captured.

<PresetLauncher id="UltraCompleteSveInstance" initialProfile="Potassium" />

## DiagnosticSaveInstance

An initial test without scripts or compression. This profile exercises
Potassium's binary-property reader and uses the ordinary writer.

<PresetLauncher id="DiagnosticSaveInstance" initialProfile="Potassium" />

## MapSaveInstance

A full-root export without script extraction. Native binary-property reads and
the append-based writer are enabled.

<PresetLauncher id="MapSaveInstance" initialProfile="Potassium" />

## ScriptsSaveInstance

The scripts-focused configuration with bounded decompilation and bytecode jobs,
native property access, and the append-based writer.

<PresetLauncher id="ScriptsSaveInstance" initialProfile="Potassium" />

## What the adapter adds

- **Binary geometry:** `getbspval(instance, property, false)` attempts raw
  `BinaryString` reads before ordinary hidden-property fallbacks. No Base64
  text is written as binary geometry. Lua errors or invalid return types fall
  through to the existing reader. Empty strings remain valid byte sequences.
- **Explicit bindings:** documented `gethiddenproperty`, `getnilinstances`,
  `getscriptbytecode`, Base64 codecs, and GUI/clipboard helpers are bound
  directly, avoiding heuristic method discovery for this edition.
- **Compression:** `crypt.lz4compress` is offered to the existing format check
  and benchmark. Availability does not guarantee it is selected; incompatible
  output is rejected and existing fallbacks remain available.
- **Large writes:** Map, Scripts, and Ultra enable `AlternativeWritefile`.
  The existing writer uses approximately 4 MB append batches where supported,
  reducing whole-file string concatenation. Binary probes and ordinary writer
  fallbacks remain active.
- **Script extraction:** since 0.4.2, the shared engine reads each script's
  bytecode once per export and passes cached bytes to Potassium's documented
  `decompile` overload. Both Ultra configurations benefit when run on Potassium.
  ModuleScripts are not excluded as a class.
  Version 0.4.4 removes forced per-script frame waits and deferral of immediately
  completed jobs. Native API latency remains executor-dependent; the selection
  and timeout settings are unchanged.
- **Reports:** `profile: "Potassium"` and `runtimeAdapter` identify the executor
  version, available APIs, and binary-read attempts, successes, and failures.
  `sharedCoreUrl` and `sharedCoreBytes` identify the second-stage source, while
  the wrapper's `sourceOrigin` identifies the dedicated entry point.

Both entry points use the same serializer. The Potassium entry point is under
`Executors/Potassium/saveinstance.luau`; its four presets are under
`Executors/Potassium/Script Presets/`. Loaders pin both stages to v0.5.0.
For local adapter development, edit its `CORE_URL` as well as the preset's
`CORE_PATH`; opting into a local adapter alone still downloads its pinned core.

## Reference review and limits

The official [reference index](https://docs.potassium.pro/llms.txt) and
[complete reference](https://docs.potassium.pro/llms-full.txt) were read on
2026-10-16. All **198 indexed pages** were present in the complete reference.
The repository's `Executors/Potassium/API_REVIEW.md` records the selection and
the snapshot hashes, including APIs considered but not integrated.

`getpcd` returns a hash and binary data. Its page does not specify how to pack
those values into the serializer's `PhysicalConfigData` property, so this
adapter does not invent a packing scheme. It also does not substitute
Potassium's built-in `saveinstance`, whose options and serializer differ.

Reading the reference establishes an API contract, not compatibility with the
installed executor build. Mock tests and compilation cannot validate Roblox
native calls or catch native crashes. Studio reopening and the missing road
still require a fresh export. See [missing geometry](GEOMETRY.md).

The 0.4.2 progress checkpoint is written before script jobs and compression.
Keep `<output-path>.progress.json` if Potassium freezes. Lua deadlines cannot
interrupt native code that blocks the entire client; see
[troubleshooting](TROUBLESHOOTING.md). Source columns and chunks over 8 MiB are
stored uncompressed, which can increase file size without dropping their data.

Sources: [binary-property reads](https://docs.potassium.pro/api-reference/Reflection%20Library/getbspval),
[LZ4](https://docs.potassium.pro/api-reference/Crypt%20Library/crypt.lz4compress),
[physical configuration](https://docs.potassium.pro/api-reference/Reflection%20Library/getpcd),
[file appending](https://docs.potassium.pro/api-reference/FileSystem%20Library/appendfile).
