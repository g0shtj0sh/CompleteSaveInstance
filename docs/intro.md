---
sidebar_position: 1
title: Getting started
---

# CompleteSaveInstance

Archive the Roblox instances your environment can actually access, with explicit
options and evidence about the resulting file.

This distribution is in development. API documentation describes the source;
it does not certify runtime compatibility or a valid export.

## Choose a preset

Start with **DiagnosticSaveInstance** on a small authorized test place.
Use **MapSaveInstance** for a map-focused export or **ScriptsSaveInstance** for
an authorized script-focused investigation. **UltraCompleteSveInstance** is the
experimental preset we are developing for the widest accessible coverage.

The [preset guide](PRESETS.md) explains each configuration and how to run it.
All presets share the same serializer; their options and output names differ.

## Read the API

The [CompleteSaveInstance API](/api/CompleteSaveInstance) lists option types,
default values, aliases, and the exported function. It is generated from the
primary `saveinstance.luau`, without mixing in the older Lua implementation.
Use the [option index](OPTIONS.md) to find individual settings through the
site search. Both pages are generated from the same source comments.

## Verify the result

Use a small place you own or have permission to archive. Confirm the runtime's
real file workspace and a successful write/read probe. After export, verify the
output exists and inspect it in Roblox Studio. A completed function call alone
does not establish a usable backup.

See [usage](USAGE.md), [troubleshooting](TROUBLESHOOTING.md), and the
[roadmap](ROADMAP.md) for requirements, current limits, and unfinished work.
