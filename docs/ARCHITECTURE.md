# Architecture and current scope

## Current implementation

The runtime remains in two inherited entry points. `saveinstance.luau` is primary;
`saveinstance.lua` is an older, separate variant. `Tools/` contains development
dumpers and metadata snapshots. `TODO/` contains exploratory patches. They are
not a supported exporter API.

The implementation performs capability discovery, metadata loading, option
resolution, instance selection, property extraction, serialization, and output.
Some write probes and fallbacks already exist; they do not establish a validated
end-to-end diagnostics pipeline.

## External dependencies

The Luau entry point loads `StreamBuffer` and `UniversalMethodFinder` from
`luau/SomeHub`; the older Lua entry point also loads the method finder. These
names identify external dependencies, so their URLs remain intact.

The runtime also queries external metadata and API dumps. Pinning the root
script tag does not pin these dependencies. Vendoring or pinning them, with
their provenance and licenses, is future work.

## Foundation changes — 2026-10-16

- CompleteSaveInstance logo, banner, documentation, and repository configuration.
- Updated project links, function names, and documentation classes.
- Global state prefix changed to `CSI`; disk cache to `completesaveinstance_cache/`.
- Generated-file credits identify this distribution and preserve its upstream.
- Repository consistency checks and Luau compilation CI.

Serializer algorithms, compression, property coverage, and output verification
have not been redesigned in this milestone. The import commit preserves the
original files for comparison.

## Documentation and preset layer

Moonwave 1.4.2 generates the API from `saveinstance.luau`; the older variant is
excluded to avoid mixing different defaults and features. Guides and a local
search index are built into the static Docusaurus website, deployed by GitHub
Actions to GitHub Pages.

`Script Presets/presets.json` defines the four configurations. The generator
combines them with a shared wrapper template. Wrappers perform a basic text
write/read probe, prefer a local engine, and otherwise load the pinned
`v0.2.0` engine. They report exceptions and file existence separately from file
validity. The actual serializer is not duplicated.

UltraCompleteSveInstance is the experimental configuration for the next
diagnostic work. Mock tests validate wrapper branches, not Roblox serialization.

## Next engine work

The next pipeline should expose preflight, write probe, inventory, extraction,
serialization, writing, validation, and reporting as measurable phases. Logs
should be buffered and repetitive failures aggregated. A backup needs evidence
about its actual output. See [the roadmap](ROADMAP.md) for unimplemented work.
