<p align="center">
  <img src="assets/brand/banner.png" alt="CompleteSaveInstance — Roblox instance archival" width="100%" />
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0-76F2CF?style=flat-square&labelColor=0B1220" alt="License: AGPL-3.0" /></a>
  <img src="https://img.shields.io/badge/language-Luau-9EDBFF?style=flat-square&labelColor=0B1220" alt="Language: Luau" />
  <img src="https://img.shields.io/badge/status-early_development-F1C875?style=flat-square&labelColor=0B1220" alt="Status: early development" />
</p>

<p align="center">
  <strong>A clearer foundation for Roblox instance archival.</strong><br />
  Accessible data. Explicit limits. Evidence before success.
</p>

<p align="center">
  <a href="#getting-started">Get started</a> ?
  <a href="docs/USAGE.md">Usage</a> ?
  <a href="docs/TROUBLESHOOTING.md">Troubleshooting</a> ?
  <a href="docs/ROADMAP.md">Roadmap</a> ?
  <a href="README.fr.md">Français</a>
</p>

---

## The project

**CompleteSaveInstance** is a Luau toolkit for exporting accessible Roblox
instances to place and model files. It builds on an existing serializer and
establishes a separate identity for future diagnostics, verification, and
reliability work.

Use it with experiences you own or have permission to archive. For your own
projects, start with Roblox Studio's built-in save and export features.

> **Development status:** this first milestone introduces the project identity,
> documentation, and repository checks. End-to-end export and Studio reopening
> have not been validated for this distribution. A completed function call is
> not proof of a usable backup.

## What is in the code today

- **Place and model serialization:** binary `.rbxl` / `.rbxm` and XML `.rbxlx` / `.rbxmx` paths.
- **Configurable selection:** instance roots, exclusion lists, properties, and modes.
- **Environment adapters:** detection and fallbacks for environment-specific APIs.
- **Existing diagnostics:** console messages, status display, and selected write probes.
- **Two entry points:** the primary `saveinstance.luau` and an older `saveinstance.lua` variant.

Availability depends on the runtime, readable properties, and loaded instances.
The Lua variant differs from the Luau source and is not feature-equivalent.

## Getting started

Read [the usage guide](docs/USAGE.md) first. This example uses a project tag and
an explicit diagnostic configuration. It requires a compatible runtime with
HTTP access, `loadstring`, and file APIs; it is not an ordinary Roblox
LocalScript or Studio command-bar script.

```lua
local source = game:HttpGet(
    "https://raw.githubusercontent.com/g0shtj0sh/CompleteSaveInstance/v0.1.0/saveinstance.luau",
    true
)
local completeSaveInstance = assert(loadstring(source, "CompleteSaveInstance"))()

completeSaveInstance({
    FilePath = "CompleteSaveInstance_Diagnostic.rbxl",
    mode = "optimized",
    Binary = true,
    CompressionMode = false,
    Decompile = false,
    SaveBytecode = false,
    NilInstances = false,
    IgnoreSpecialProperties = true,
    AlternativeWritefile = false,
    SafeMode = false,
    KillAllScripts = false,
    BoostFPS = false,
    ShutdownWhenDone = false,
    ShowStatus = true,
    __DEBUG_MODE = true,
})
```

**Private repository:** raw GitHub URLs require authorized access and may return
404 from an unauthenticated Roblox runtime. Use an authenticated local checkout
and your runtime's local script facility instead. Never embed a GitHub token in
a loader or exported place. Tag pinning selects the root script version;
inherited external helpers are not yet pinned.

## Know what was actually saved

Confirm that the output exists in the runtime's real workspace, then open it
in Roblox Studio and inspect a representative sample. A referenced asset ID
does not mean the asset binary was included. Client-side inspection cannot
recover server-only code, private DataStores, or unloaded streamed content.

`PROP dropped` reports a property omission; it does not by itself mean an
entire instance was lost. See [troubleshooting](docs/TROUBLESHOOTING.md).

## Explore the repository

- [Usage and compatibility](docs/USAGE.md) — entry points, first run, important options.
- [Troubleshooting](docs/TROUBLESHOOTING.md) — missing files, crashes, property omissions.
- [Architecture](docs/ARCHITECTURE.md) — inherited runtime and external dependencies.
- [Roadmap](docs/ROADMAP.md) — planned work after this foundation.
- [Contributing](CONTRIBUTING.md) — checks and useful bug reports.
- [Brand assets](assets/brand/README.md) — logo, banner, palette, and generation prompts.

## Development checks

```powershell
python scripts/check_repository.py
luau-compile --null saveinstance.luau saveinstance.lua
```

GitHub Actions validates repository consistency and compiles both entry points
using Luau **0.742**. These checks do not exercise Roblox APIs or verify an
exported place.

## License and credits

Distributed under [AGPL-3.0](LICENSE). Based on
[UniversalSynSaveInstance](https://github.com/luau/UniversalSynSaveInstance);
the inherited attribution is **UniversalSynSaveInstance https://discord.gg/wx4ThpAsmw**.
See [NOTICE.md](NOTICE.md) for provenance and acknowledgments.

Independent, unofficial project. Not affiliated with Roblox Corporation.
