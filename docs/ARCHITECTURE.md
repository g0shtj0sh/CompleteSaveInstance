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

## Direction

The next pipeline should expose preflight, write probe, inventory, extraction,
serialization, writing, validation, and reporting as measurable phases. Logs
should be buffered and repetitive failures aggregated. A backup needs evidence
about its actual output. See [the roadmap](ROADMAP.md) for unimplemented work.
