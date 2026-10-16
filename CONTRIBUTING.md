# Contributing to CompleteSaveInstance

Keep changes focused and preserve the inherited attribution and AGPL license.
Use experiences you own or are authorized to test.

## Checks

Use Python 3.11+ and the official Luau compiler **0.742**:

```powershell
python scripts/check_repository.py
luau-compile --null saveinstance.luau saveinstance.lua
git diff --check
```

Compilation checks syntax and bytecode generation without executing the script.
Runtime changes need an authorized sample, exact options, output evidence, and
a Studio reopening check before being described as validated.

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
