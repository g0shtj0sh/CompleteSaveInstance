# Contributing to CompleteSaveInstance

Keep changes focused and preserve the inherited attribution and AGPL license.
Use experiences you own or are authorized to test.

## Checks

Use Python 3.11+ and the official Luau compiler **0.742**:

```powershell
python scripts/check_repository.py
python scripts/generate_presets.py --check
python scripts/generate_option_index.py --check
python scripts/test_presets.py --luau luau
python scripts/test_property_reads.py --luau luau
python scripts/test_potassium.py --luau luau
luau-compile --null saveinstance.luau saveinstance.lua "Script Presets/DiagnosticSaveInstance.luau" "Script Presets/MapSaveInstance.luau" "Script Presets/ScriptsSaveInstance.luau" "Script Presets/UltraCompleteSveInstance.luau"
git diff --check
```

Compilation checks syntax and bytecode generation without executing the script.
Runtime changes need an authorized sample, exact options, output evidence, and
a Studio reopening check before being described as validated.

## Documentation and presets

Edit `Script Presets/presets.json` and regenerate the executable wrappers with
`python scripts/generate_presets.py`. They share the engine instead of copying it.
The mock scenarios test wrapper behavior; they do not exercise Roblox APIs.
The generator also produces `Executors/Potassium/Script Presets/` with explicit
property-reader and writer overrides. Compile those wrappers and the dedicated
entry point as well. Keep native adaptation in that entry point and the narrow
shared adapter interface; do not duplicate the serializer.

Build the website with Node 22+:

```powershell
npm ci
npm run docs:build
python scripts/check_docs_build.py
python scripts/serve_docs.py
```

Open `http://127.0.0.1:4173/CompleteSaveInstance/`. The API is extracted from the
primary Luau source only. Markdown guides live in `docs/`, the homepage in
`pages/index.js`, and the visual theme in `.moonwave/custom.css`.
The API UI lives in `website/ApiReference.jsx`; `scripts/docs.mjs` installs its
component alias in the generated site configuration. The option generator
updates both `docs/OPTIONS.md` and `website/api-data.json`.
The documentation workflow builds and checks pull requests; pushes to `main`
also deploy to GitHub Pages. Do not commit generated `build/` or `node_modules/`.
After changing source API comments, run `python scripts/generate_option_index.py`
to refresh the searchable option index. The build rejects stale generated text.

## Conventions

Preserve surrounding formatting. Avoid unrelated serializer changes. Prefer
current Luau task APIs for new code. Protect runtime-dependent operations where
appropriate, and distinguish Lua exceptions from native crashes.

The two entry points differ. Document which a change affects rather than assuming
that a mechanical translation establishes parity. Add meaningful tests for new
behavior, not tests that simply repeat the implementation.

## Reports and pull requests

Include revision, runtime version, a minimal reproduction, and expected and
observed behavior. Export bugs need file existence and Studio results. Remove
credentials and private content from attachments. New options need documented
defaults, compatibility notes, and relevant validation. Keep roadmap work marked
as planned until implementation and evidence exist.
