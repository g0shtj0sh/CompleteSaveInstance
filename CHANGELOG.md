# Changelog

## 0.4.0 — 2026-10-16

- Added direct runnable-script copy buttons to all preset sections and the API
  Explorer, with Universal/Potassium selection and manual clipboard fallback.
- Added `Executors/Potassium/` with a dedicated entry point and four generated
  presets sharing the primary serializer.
- Added native raw BinaryString reads through getbspval, explicit API bindings,
  native LZ4 candidate validation, and profile/capability/read-counter reports.
- Enabled the existing append writer for Potassium Map, Scripts, and Ultra.
- Reviewed all 198 pages in the official Potassium reference and documented
  adopted APIs and deferred integrations without duplicating its source text.
- Expanded mock coverage to both sets of presets and adapter contracts.

Installed Potassium behavior and the missing road still require a fresh Roblox
export and Studio inspection. The universal path retains its existing fallbacks.

## 0.3.0 — 2026-10-16

- Replaced the API's large type block with a searchable option explorer,
  category filters, preset comparisons, and copyable configurations. Redesigned
  the developer homepage and responsive theme.
- Fixed primary-engine hidden-property failures incorrectly disabling later
  reads of the same datatype. Retained self-check and native-crash guards.
- Added a primary-engine report with collected class counts and omitted binary
  property columns, plus a JSON sidecar from every preset wrapper.
- Presets now download the pinned engine by default; local development is an
  explicit opt-in. Source identity and engine version are recorded.
- Added reader regression coverage and expanded wrapper mock scenarios.

The missing road in the reported export still requires a new Roblox export
and Studio inspection. XML property omission auditing is not implemented.

## 0.2.0 — 2026-10-16

- Public repository and public GitHub Pages documentation.
- Moonwave API reference generated from the primary Luau source, with guides,
  local search, responsive homepage, and the CompleteSaveInstance theme.
- Added `Script Presets`: DiagnosticSaveInstance, MapSaveInstance,
  ScriptsSaveInstance, and the experimental UltraCompleteSveInstance target.
- Presets share the engine, prefer local source, and otherwise use the
  `v0.2.0` engine. Each includes a basic write/read probe and explicit output
  evidence without claiming file validity.
- Generated catalog checks, 44 mocked wrapper scenarios, preset compilation,
  built-site checks, and automatic documentation deployment.

Ultra's export behavior remains unverified in Roblox and Studio; this milestone
establishes the configuration we will diagnose, not a complete-backup guarantee.

## 0.1.0 — 2026-10-16

First CompleteSaveInstance foundation, based on the supplied upstream snapshot.

- New identity, logo, README banner, and Moonwave assets.
- Updated project links, examples, documentation classes, and function names.
- Dedicated `CSI` global namespace and `completesaveinstance_cache/` disk cache.
- English and French presentation, usage, troubleshooting, architecture, roadmap.
- Issue forms, contribution guide, repository validation, and compilation CI.
- Preserved original license, required attribution, and source import history.

This milestone does not certify runtime compatibility or a successful Studio
export. Serializer and writer redesign remain future work.
