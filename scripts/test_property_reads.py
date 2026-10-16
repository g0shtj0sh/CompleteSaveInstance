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
print("Property-reader regression scenarios passed: unrelated failures, terrain, union data, valid nil, self-check block, crash block, persisted failure, cache migration.")
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
    with tempfile.TemporaryDirectory(prefix="csi-reader-tests-") as directory:
        script = Path(directory) / "reader.luau"
        script.write_text(program, encoding="utf-8")
        result = subprocess.run([args.luau, str(script)], capture_output=True, text=True)
    print(result.stdout, end="")
    if result.returncode:
        raise SystemExit(result.stderr)


if __name__ == "__main__":
    main()
