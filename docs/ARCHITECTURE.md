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
write/read probe and load the pinned `v0.4.0` engine by default. Local development
requires an explicit `USE_LOCAL_CORE = true`. They record source identity,
exceptions, and file existence in a JSON sidecar separately from file validity.
The actual serializer is not duplicated.

UltraCompleteSveInstance is the experimental configuration for the next
diagnostic work. Mock tests validate wrapper branches, not Roblox serialization.

## Property reads and reports in 0.3.0

The primary engine distinguishes an ordinary hidden-property read failure from
a failed datatype self-check or a native crash. An inaccessible property no
longer disables subsequent properties sharing its datatype. Ambiguous cached
failures from older versions are reset; native-crash markers stay blocked.

Binary property columns are omitted as a whole if a value cannot be read.
The returned report counts these columns, records up to 256 failure samples,
and flags selected geometry properties for investigation. XML omission auditing
is not implemented. Neither report creation nor the existing writer verifies
that Studio can open the result.

The API Explorer uses generated option metadata and preset values. The build
integrates it through a webpack component alias in Moonwave's generated
Docusaurus configuration; dependency source files remain untouched.

## Executor adapters in 0.4.0

Version 0.4.0 adds a narrow adapter argument to the primary source chunk.
`Executors/Potassium/saveinstance.luau` supplies canonical native functions
without global hooks or a second serializer. BinaryString reads can use its
protected raw reader before the ordinary fallback chain; dedicated presets
explicitly enable those reads. See [Potassium](POTASSIUM.md) for contracts and
the reference review. The universal entry point still uses method discovery.

## Next engine work

The next pipeline should expose preflight, write probe, inventory, extraction,
serialization, writing, validation, and reporting as measurable phases. Logs
should be buffered and repetitive failures aggregated. A backup needs evidence
about its actual output. See [the roadmap](ROADMAP.md) for unimplemented work.
