---
sidebar_position: 2
title: Script Presets
---

# Script Presets

import PresetLauncher from '@site/src/csi/PresetLauncher';

Preset scripts select a configuration for the shared CompleteSaveInstance
engine. They do not duplicate the serializer. The current development focus is
**UltraCompleteSveInstance**, the experimental maximum-coverage configuration.

Choose **Universal** or **Potassium**, then click **Copier le script**. Each
button copies the complete runnable loader shown below it. Potassium has a
[dedicated engine and guide](POTASSIUM.md) with native binary-property reads.

## DiagnosticSaveInstance

An initial diagnostic with decompilation, bytecode capture, nil instances, and
compression disabled. Uses fallback property access. Start here to separate
file-writing and serialization failures from more advanced work.

<PresetLauncher id="DiagnosticSaveInstance" />

## MapSaveInstance

A full-root, map-focused export without decompilation or bytecode. It favors
scene properties and keeps default runtime-service exclusions. This is not a
strict map-only filter: accessible UI, sound, and other non-script content can
also be included.

<PresetLauncher id="MapSaveInstance" />

## ScriptsSaveInstance

An authorized script-focused export using the engine's `scripts` mode, bounded
decompilation and bytecode timeouts. Server-only scripts remain unavailable.
Structural instances can still appear as containers.

<PresetLauncher id="ScriptsSaveInstance" />

## UltraCompleteSveInstance

**Experimental / current development target.** Uses full mode, decompilation,
bytecode capture, nil instances, special property access, non-archivable
instances, player content, and empty exclusion lists. Empty exclusions can
include large amounts of runtime content, so begin on a small test place.

This is the configuration we will diagnose and improve to preserve as much
accessible place content as possible. It is not a promise of complete capture
or a previously verified fix. Timeouts are bounded. `SafeMode`, script
termination, forced shutdown, and rendering changes stay disabled.

<PresetLauncher id="UltraCompleteSveInstance" />

## Versioned loaders

Run a preset in a compatible environment with HTTP access and file APIs:

```lua
loadstring(game:HttpGet(
    "https://raw.githubusercontent.com/g0shtj0sh/CompleteSaveInstance/v0.4.1/Script%20Presets/UltraCompleteSveInstance.luau",
    true
))()
```

Replace the final filename with `DiagnosticSaveInstance.luau`,
`MapSaveInstance.luau`, or `ScriptsSaveInstance.luau` for a different goal.
The [catalog on GitHub](https://github.com/g0shtj0sh/CompleteSaveInstance/blob/main/Script%20Presets/README.md)
shows each loader and its exact option values.

## Local installation

For local development, copy the engine and selected preset into the runtime's
file workspace:

```text
CompleteSaveInstance/
  saveinstance.luau
  Script Presets/
    DiagnosticSaveInstance.luau
    MapSaveInstance.luau
    ScriptsSaveInstance.luau
    UltraCompleteSveInstance.luau
```

Execute the chosen preset through the runtime's local script facility. If your
layout differs, change `CORE_PATH` at the top of the preset. Set
`USE_LOCAL_CORE = true` to opt into that local engine; the default downloads
the pinned version. A missing local file produces an error. External helpers are
still fetched by the engine and are not yet pinned.

Every preset performs a basic text write/read probe, chooses a unique output name,
and distinguishes a returned function from an existing file. Output contents
and Studio compatibility remain unverified until you inspect them.

Wrappers write `<output-path>.report.json` with engine identity, file evidence,
class counts, and omitted binary property columns. A report-writing error is
printed explicitly. Use the [missing geometry guide](GEOMETRY.md) when objects
or surfaces are absent.

## Changing a configuration

Edit `Script Presets/presets.json`, then run:

```powershell
python scripts/generate_presets.py
```

The generated scripts and catalog stay in sync. Run the repository checks and
compile the generated scripts before committing. Runtime observations belong
in the issue report, including the exact preset revision and options.
