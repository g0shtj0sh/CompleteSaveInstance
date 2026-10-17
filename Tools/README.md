# Metadata development tools

These dumpers support property coverage investigations and future Roblox API
updates. The exporter does not run them. Run `Run Dumpers.py` to regenerate
metadata using the shared helper in `common/`; individual Luau probes need a
compatible runtime.

Generated `Dump` files and the API metadata cache are intentionally ignored.
They are observations from a particular Roblox revision, not source inputs or
compatibility guarantees. Historical snapshots remain recoverable in Git.

Property-format references for future work:

- [rbx-dom custom properties](https://github.com/rojo-rbx/rbx-dom/blob/master/rbx_dom_lua/src/customProperties.lua)
- [rbx-dom patches](https://github.com/rojo-rbx/rbx-dom/tree/master/patches)
- [Roblox file-format property patches](https://github.com/MaximumADHD/Roblox-File-Format/blob/main/Plugins/GenerateApiDump/PropertyPatches.lua)
