# Usage

## Runtime and entry points

For experiences you own, prefer Roblox Studio's built-in export options first.
The inherited runtime expects environment-specific file, HTTP, and introspection
functions, which are not generally available in standard Scripts or LocalScripts.
Support varies by runtime; this distribution has no validated compatibility
matrix yet.

`saveinstance.luau` is the primary entry point. It returns the
`completeSaveInstance` function, which accepts an options table. Existing file
names are retained for compatibility. `saveinstance.lua` is an older variant
with a different implementation; do not assume feature parity or binary support.

## Access to the private repository

Clone with an authenticated Git client:

```powershell
gh repo clone g0shtj0sh/CompleteSaveInstance
```

Load the checked-out `saveinstance.luau` using your runtime's documented local
script facility. There is no portable local loader for every runtime. Raw URLs
for a private GitHub repository require authorized access and may otherwise
return 404. Never embed an access token in Luau code or an exported place.

The project tag pins the entry point. External helpers still load from upstream
`main` URLs; the entire dependency chain is not reproducible yet.

## First diagnostic

1. Use a small experience you own or are authorized to archive.
2. Record the source revision, Roblox version, and runtime version.
3. Find the runtime's real file workspace; relative paths are resolved there.
4. Write and read back a small unique text file using its file APIs.
5. Use the explicit configuration in the [README](../README.md#getting-started).
6. Confirm the output exists, then open and inspect it in Studio.

## Important options in the primary source

These descriptions are based on the supplied source, not runtime certification.
The inline `CustomOptions` documentation in `saveinstance.luau` gives more detail.

- `FilePath`: output name or runtime-relative path. Explicit paths can overwrite
  existing output; use a unique filename for each diagnostic.
- `mode`: `full`, `optimized`, or `scripts`; controls selected roots, without
  guaranteeing every property, object, or asset will be captured.
- `Binary`: selects binary output. `XML = true` is the inverse alias.
- `CompressionMode`: `zstd`, `lz4`, or `false`, subject to runtime capabilities.
- `Decompile` and `SaveBytecode`: require optional runtime APIs. Disable both
  initially to isolate serializer and writer behavior.
- `IgnoreSpecialProperties`: selects fallback property access paths; it is not
  a guarantee that every unusual property will be safely skipped.
- `SafeMode`: deliberately disconnects the client and can enable script
  termination and rendering changes. Leave false for initial diagnosis.
- `KillAllScripts`, `BoostFPS`, `ShutdownWhenDone`: change client behavior;
  explicitly disable all three for the first run.
- `AlternativeWritefile`: uses an append-based writer where supported. Existing
  probes and fallbacks still need validation in Roblox for this distribution.
- `ShowStatus`, `__DEBUG_MODE`: existing status display and console diagnostics.

## Verify the result

Check the exact path, existence, plausible file size, and Studio opening.
Inspect representative models, meshes, materials, UI, and authorized scripts.
A return from the function does not prove that the output is valid.

Server-only data, private DataStores, unloaded streamed instances, and restricted
assets can be absent. An asset ID is a reference, not an embedded binary asset.

## Namespace changes

Runtime globals now use `CSI`, including `CSI_scriptcache` and `CSI_placeName`.
The disk cache is `completesaveinstance_cache/`. Existing old caches are not
migrated or deleted. Avoid running both distributions against the same file.
