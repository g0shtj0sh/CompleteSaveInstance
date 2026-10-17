"""Regression tests against the actual primary property-reader functions."""

from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

FIXTURE = r'''
local __BREAK = {}
local GHP = {}
local StatusText = nil
local Anonymizers = nil
local InstancesOverrides = {}
local decompileIgnoreMap = {}
local gethiddenproperty_fallback = nil
local OPTIONS = {IgnoreSpecialProperties = false}
local adapterBinaryReader
local adapterBinaryReads = {attempts = 0, successes = 0, failures = 0}
local calls = {}
local function saveExecState() end
local function ensureTextRendered() end
local function anonymize(value) return value end
local function string_find(s, p) return string.find(s, p, 1, true) end
local function index(object, key) return object[key] end
local function gethiddenproperty(_, key)
    table.insert(calls, key)
    if key == "SerializedOverrides" then error("property cannot be read") end
    if key == "SmoothGrid" then return "TERRAIN_BYTES" end
    if key == "MeshData" then return "UNION_BYTES" end
    if key == "OptionalRef" then return nil end
    error("unexpected property")
end
__FUNCTIONS__
local function prop(name, category, optional)
    return {Name = name, ValueType = "BinaryString", Category = category or "DataType", Special = true, Optional = optional}
end
assert(readProperty({}, prop("SerializedOverrides")) == __BREAK)
assert(GHP.BinaryString == "property_failed", "Ordinary failure must not poison the datatype")
assert(readProperty({}, prop("SmoothGrid")) == "TERRAIN_BYTES", "Readable terrain must survive an unrelated property failure")
assert(readProperty({}, prop("MeshData")) == "UNION_BYTES", "Readable union geometry must survive an unrelated failure")
assert(readProperty({}, prop("OptionalRef", "Class")) == nil, "Valid nil references must remain valid")
ghpDatatypeReport("BinaryString", false, true)
assert(not ghpDatatypeAllowed("BinaryString"), "Failed self-check must still disable a datatype")
GHPDatatypeState = {}
GHP.BinaryString = "crashed"
assert(not ghpDatatypeAllowed("BinaryString"), "Persisted crash markers must remain blocked")
GHPDatatypeState = {}
GHP.BinaryString = "property_failed"
assert(ghpDatatypeAllowed("BinaryString"), "A persisted property failure must not block a later run")
local ExecState = {ghpSchema = 1}
GHP = {BinaryString = "failed", string = "ok", NetAssetRef = "crashed"}
__MIGRATION__
assert(GHP.BinaryString == nil and GHP.string == "ok" and GHP.NetAssetRef == "crashed")
assert(ExecState.ghpSchema == 2)
GHP = {}
GHPDatatypeState = {}
adapterBinaryReader = function(_, key)
    if key == "SmoothGrid" then return "\0\255RAW_TERRAIN" end
    if key == "MeshData" then error("native reader rejected property") end
    if key == "EmptyGrid" then return "" end
    if key == "OptionalRef" then return false end
    return "can't get value"
end
assert(readProperty({}, prop("SmoothGrid")) == "\0\255RAW_TERRAIN", "Adapter bytes must remain unchanged")
assert(readProperty({}, prop("MeshData")) == "UNION_BYTES", "Native Lua error must fall back to the ordinary reader")
assert(readProperty({}, prop("EmptyGrid")) == "", "Empty binary data remains valid")
assert(readProperty({}, prop("OptionalRef", "Class")) == nil, "Invalid adapter return must use existing valid nil handling")
assert(readProperty({}, prop("SerializedOverrides")) == __BREAK, "Error strings must not be serialized as geometry")
assert(adapterBinaryReads.attempts == 5 and adapterBinaryReads.successes == 2 and adapterBinaryReads.failures == 3)
local overridden = {}
InstancesOverrides[overridden] = {Properties = {SmoothGrid = "OVERRIDE"}}
assert(readProperty(overridden, prop("SmoothGrid")) == "OVERRIDE", "Explicit instance override must retain precedence")
assert(adapterBinaryReads.attempts == 5)
OPTIONS.IgnoreSpecialProperties = true
assert(readProperty({}, prop("SmoothGrid")) == "TERRAIN_BYTES")
assert(adapterBinaryReads.attempts == 5, "Special-property opt-out must bypass native adapter")
print("Property-reader regression scenarios passed: unrelated failures, terrain, union data, valid nil, self-check block, crash block, persisted failure, cache migration.")
print("Adapter-reader scenarios passed: raw binary, empty data, Lua errors, wrong type, error strings, counters, opt-out.")
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--luau", default="luau")
    args = parser.parse_args()
    source = (ROOT / "saveinstance.luau").read_text(encoding="utf-8")
    functions = source.split("\tlocal function nilIsValid(", 1)[1].split("\tlocal function GetInheritedProps", 1)[0]
    functions = "local function nilIsValid(" + functions
    migration = source.split("\t\tif ExecState.ghpSchema ~= 2 then", 1)[1].split('\t\tExecState["ghp"] = GHP', 1)[0]
    migration = "if ExecState.ghpSchema ~= 2 then" + migration
    program = FIXTURE.replace("__FUNCTIONS__", functions).replace("__MIGRATION__", migration)
    cache_reader = source.split("local function loadExecutorState(", 1)[1].split("local function createStatusDisplay()", 1)[0]
    program += "\nlocal function loadExecutorState(" + cache_reader + r'''
local files = {}
local function read(path)
    if files[path] == nil then error("missing file") end
    return files[path]
end
local function decode(value) return value end
local paths = {"new", "legacy"}
assert(next(loadExecutorState(nil, decode, "executor", paths)) == nil)
files.legacy = {executor = {ghpSchema=2, ghp={BinaryString="crashed", NetAssetRef="failed"}}}
local state=loadExecutorState(read, decode, "executor", paths)
assert(state.ghp.BinaryString=="crashed" and state.ghp.NetAssetRef=="failed" and state.ghpSchema==2)
files.new = {executor = {ghpSchema=2, ghp={BinaryString="ok", string="ok"}, writer="new-setting"}}
state=loadExecutorState(read, decode, "executor", paths)
assert(state.ghp.BinaryString=="crashed", "Renaming must not reset native-crash guards")
assert(state.ghp.string=="ok" and state.writer=="new-setting", "Prefer current cache settings")
files.new = "invalid JSON shape"
assert(loadExecutorState(read, decode, "executor", paths).ghp.BinaryString=="crashed")
files.legacy = {otherExecutor={ghp={BinaryString="crashed"}}}
assert(next(loadExecutorState(read, decode, "executor", paths))==nil, "Do not mix executor or client revisions")
files.new = false
assert(next(loadExecutorState(read, function() error("bad JSON") end, "executor", paths))==nil)
print("Actual cache migration passed: legacy safety state, crash preservation, current settings, malformed files, executor isolation.")
'''
    with tempfile.TemporaryDirectory(prefix="csp-reader-tests-") as directory:
        script = Path(directory) / "reader.luau"
        script.write_text(program, encoding="utf-8")
        result = subprocess.run([args.luau, str(script)], capture_output=True, text=True)
    print(result.stdout, end="")
    if result.returncode:
        raise SystemExit(result.stderr)


if __name__ == "__main__":
    main()
