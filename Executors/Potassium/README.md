# CompleteSaveInstance for Potassium

Dedicated API bindings and presets, sharing the primary serializer.

Use the [documentation and copy buttons](https://g0shtj0sh.github.io/CompleteSaveInstance/docs/POTASSIUM/)
or execute this versioned Ultra loader:

```lua
loadstring(game:HttpGet(
    "https://raw.githubusercontent.com/g0shtj0sh/CompleteSaveInstance/v0.5.1/Executors/Potassium/Script%20Presets/UltraCompleteSveInstance.luau",
    true
))()
```

- [UltraNoModuleScripts](Script%20Presets/UltraNoModuleScripts.luau): Ultra excluding ModuleScripts and their descendants.
- [UltraCompleteSveInstance](Script%20Presets/UltraCompleteSveInstance.luau): experimental full coverage.
- [DiagnosticSaveInstance](Script%20Presets/DiagnosticSaveInstance.luau): property/writer diagnosis without scripts or compression.
- [MapSaveInstance](Script%20Presets/MapSaveInstance.luau): full-root scene export without script extraction.
- [ScriptsSaveInstance](Script%20Presets/ScriptsSaveInstance.luau): script-focused mode.
- [saveinstance.luau](saveinstance.luau): dedicated entry point returning the exporter function.
- [API review](API_REVIEW.md): reviewed reference, adopted APIs, and deferred features.

The adapter identifies Potassium and passes explicit native functions to the
shared engine. It attempts `getbspval` with `base64=false` for raw BinaryString
properties, including Terrain and union data when readable. Invalid values
and Lua failures fall back to the ordinary property reader.

Presets enable special property reads. Map, Scripts, and Ultra also enable
the existing append writer. Native `crypt.lz4compress` must pass the engine's
existing block-format check before selection. Reports include profile,
executor version, capabilities, and binary-read counters.

Since 0.4.2, script jobs reuse cached bytecode and presets write a
`<output-path>.progress.json` checkpoint while running. Preserve it if the client
freezes before producing a final report. Lua deadlines cannot preempt a blocked
native call. Source columns and chunks over 8 MiB are stored uncompressed,
preserving their data at the cost of potentially larger files.

No general-purpose globals are overwritten. Both stages download code pinned
to v0.5.1; inherited helper dependencies remain unpinned. Local adapter
development also requires changing its core URL if the shared engine is local.
Regenerate presets with `python scripts/generate_presets.py` at repository root.

Compilation and mocked regression checks pass; installed Potassium behavior
and Studio reopening still require testing. Native crashes cannot be caught
with `pcall`. Use only experiences you own or are authorized to archive.
