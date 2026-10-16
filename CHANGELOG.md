# Changelog

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
