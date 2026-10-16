# Potassium API reference review

Reviewed on **2026-10-16** using the official [page index](https://docs.potassium.pro/llms.txt)
and [complete reference](https://docs.potassium.pro/llms-full.txt). All **198**
indexed pages occur in the complete reference; no indexed pages were missing.
Every section was read, including examples and caveats. Snapshot SHA-256 hashes
and per-library page counts are recorded in [reference-review.json](reference-review.json).
Downloaded reference text is not redistributed in this repository.

## Adopted APIs

- [getbspval](https://docs.potassium.pro/api-reference/Reflection%20Library/getbspval):
  raw BinaryString reader with `base64=false`, applied before ordinary property
  reads. This is relevant to Terrain grids and union/mesh binary properties.
  Preserve empty bytes; reject invalid return types and documented reader error
  strings, then continue through existing fallbacks.
- [gethiddenproperty](https://docs.potassium.pro/api-reference/Reflection%20Library/gethiddenproperty):
  explicit binding to the ordinary reader. The value is the first result; the
  hidden flag is not geometry data. Existing datatype self-checks remain active.
- [crypt.lz4compress](https://docs.potassium.pro/api-reference/Crypt%20Library/crypt.lz4compress):
  native candidate for the existing raw-block format check and benchmark. A
  function with the right name is insufficient evidence of compatible bytes.
- FileSystem's append/read/write APIs: the existing binary probe and approximately
  4 MB append writer are reused. Only Map, Scripts, and Ultra select append mode;
  Diagnostic retains the simple writer.
- Instance enumeration, nil instances, script bytecode, GUI/clipboard helpers,
  and Crypt Base64 codecs: explicit documented bindings replace heuristic
  discovery in this entry point. The universal entry point is still available.
- [identifyexecutor](https://docs.potassium.pro/api-reference/Miscellaneous%20Library/identifyexecutor):
  reject other runtimes before downloading the core and include the version in
  the export report. No device identifier is read.

## Libraries reviewed

- **Actor Library (8):** actors and their threads are not a replacement for a
  loaded instance tree. Execution across actors would require a separate merge
  and lifecycle design; it is not added speculatively.
- **Cache Library (5):** reference comparisons may help a future identity model;
  replacing or invalidating live references is unnecessary for serialization.
- **Closure Library (13):** existing loadstring usage matches the documented
  return contract. Hooking and call-stack hiding do not improve serialized data.
- **Console Library (9):** logging already uses print/warn and JSON reports;
  creating an additional console is not required.
- **Crypt Library (11):** Base64 and LZ4 are useful here. Encryption, random
  secrets, HMAC, and unrelated hashes do not increase instance coverage.
- **Debug Library (18):** stack/proto/constant inspection does not supply the
  serialized engine-property schema. Existing script extraction remains separate.
- **Drawing Library (6), DrawingImmediate Library (2), drawing objects (10):**
  these describe executor overlays and rendering, not archival data.
- **Environment Library (7):** no scan of arbitrary registry or GC tables is
  needed for the selected property-reader adaptation.
- **FileSystem Library (11):** used through the existing probe and writer.
- **Input Library (13):** simulated input is not needed for these exports.
- **Instance Library (9):** getnilinstances and GUI capabilities are bound;
  getinstances is not assumed to expose unloaded or server-only content.
- **Metatable Library (9):** no global hooks or mutations are needed.
- **Miscellaneous Library (16):** identifyexecutor and existing HTTP behavior
  are relevant. Built-in saveinstance has a different option surface and is not
  silently substituted for this serializer. Device IDs, FastFlags, and teleport
  queues do not form part of this adapter.
- **Oth Library (5), RakNet Library (6), Signal Library (8):** hooking, packet
  modification, or replicated signal firing do not address property encoding.
- **PsmSignal Library (2), Regex Library (2), WebSocket Library (1):** no extra
  event, parsing, or remote transport layer is required.
- **Reflection Library (13):** getbspval and ordinary hidden reads are adopted.
  Bulk property getters do not replace the serializer's type/schema metadata.
- **Script Library (13):** documented bytecode access and existing bounded
  decompilation are reused. Function bytecode is not silently substituted for
  a script's bytecode, and scripts are not executed to inspect them.
- **Introduction (1):** naming conventions are a baseline; capabilities must
  still be checked against the installed build.

## Deferred physical configuration

[getpcd](https://docs.potassium.pro/api-reference/Reflection%20Library/getpcd)
returns two strings: a 16-byte hash and binary data. The reference does not
specify the packing contract required by this serializer's PhysicalConfigData
field. No concatenation or replacement scheme is inferred. A future integration
needs format evidence and an independently checked Studio result.

## Validation status

The dedicated entry point, generated wrappers, and actual reader functions have
mocked regression coverage and compile with the pinned official Luau compiler.
This is API-contract validation, not an installed Potassium or Studio test.
The report records reader attempts/successes/failures; success counts do not
prove that a road or an entire place survived serialization and reopening.
