"""Exercise preset preflight and output evidence in a mocked Luau runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HARNESS = r'''
local presetSource = __PRESET_SOURCE__
local successes = 0
local potassium = __POTASSIUM__
local expectedCorePath = potassium and "CompleteSavePlace/Executors/Potassium/saveinstance.luau" or "CompleteSavePlace/saveinstance.luau"
local expectedCoreUrl = potassium and "/v0.6.0/Executors/Potassium/saveinstance.luau" or "/v0.6.0/saveinstance.luau"
local function scenario(kind)
    local files, messages = {}, {}
    local capturedReport
    local capturedProgress, runtimeParameters
    local localReads, remoteReads = 0, 0
    local called = false
    local env = setmetatable({}, { __index = getfenv() })
    env.game = { PlaceId = 123 }
    env.game.GetService = function(_, name)
        assert(name == "HttpService")
        return {JSONEncode = function(_, value)
            if value.phase then capturedProgress=value else capturedReport=value end
            return "REPORT_JSON"
        end}
    end
    env.game.HttpGet = function(_, url)
        remoteReads += 1
        assert(string.find(url, expectedCoreUrl, 1, true), "Selected engine must be pinned")
        if kind == "missing-core" then error("network unavailable") end
        return "MOCK_CORE"
    end
    env.print = function(message) table.insert(messages, message) end
    env.warn = env.print
    env.writefile = function(path, content)
        if kind == "probe-error" then error("disk unavailable") end
        if kind == "report-write-error" and string.find(path, ".report.json", 1, true) then error("report disk error") end
        if kind == "progress-write-error" and string.find(path, ".progress.json", 1, true) then error("checkpoint disk error") end
        files[path] = kind == "corrupt-probe" and "wrong content" or content
    end
    env.readfile = function(path)
        if path == expectedCorePath then
            localReads += 1
            if kind == "missing-core" or kind == "remote-core" or kind == "local-core-missing" then error("core missing") end
            return "MOCK_CORE"
        end
        return files[path]
    end
    env.delfile = function(path) files[path] = nil end
    env.isfile = function(path) return files[path] ~= nil end
    env.loadstring = function(source, name)
        assert(source == "MOCK_CORE", "Unexpected core contents")
        if kind == "compile-error" then return nil, "mock syntax error" end
        return function(parameters)
            runtimeParameters=parameters
            assert(type(parameters.onProgress)=="function", "Wrapper must forward the progress sink")
            if kind == "bad-core" then return {} end
            return function(options)
                called = true
                runtimeParameters.onProgress({phase="scripts",detail={operation="decompile",path="ReplicatedStorage.ExampleModule"}})
                assert(options.SafeMode == false and options.KillAllScripts == false)
                assert(options.ShutdownWhenDone == false and options.BoostFPS == false)
                if __NO_MODULES__ then
                    assert(#options.IgnoreList == 1 and options.IgnoreList[1] == "ModuleScript", "Exclude ModuleScripts from collection")
                    assert(options.Decompile and options.SaveBytecode, "Keep extraction enabled for other script classes")
                end
                if potassium then assert(options.IgnoreSpecialProperties == false, "Potassium must enable its native reader") end
                assert(string.find(options.FilePath, "_123_", 1, true))
                if kind == "runtime-error" then error("serializer failed") end
                if kind ~= "missing-output" then files[options.FilePath] = "mock output" end
                if kind == "legacy-core" then return nil end
                if kind == "engine-reported-error" then return {ok=false, error="internal engine failure", engineVersion="0.6.0"} end
                return {ok=true, engineVersion="0.6.0", validation="unverified", criticalGeometryOmissions=kind=="geometry-omission" and 2 or 0}
            end
        end
    end
    if kind == "missing-api" then env.writefile = false end
    if kind == "no-isfile" then env.isfile = false end
    local scriptSource = presetSource
    if kind == "local-core" or kind == "local-core-missing" then
        scriptSource = string.gsub(scriptSource, "local USE_LOCAL_CORE = false", "local USE_LOCAL_CORE = true")
    end
    local execute = assert(loadstring(scriptSource, "preset under test"))
    setfenv(execute, env)
    local ok = pcall(execute)
    local text = table.concat(messages, "\n")
    local shouldFail = kind == "missing-api" or kind == "probe-error" or kind == "corrupt-probe"
        or kind == "missing-core" or kind == "local-core-missing" or kind == "compile-error" or kind == "bad-core" or kind == "runtime-error" or kind == "engine-reported-error"
    assert(ok ~= shouldFail, "Unexpected scenario outcome: " .. kind)
    if called then
        assert(capturedProgress.phase=="scripts" and capturedProgress.detail.path=="ReplicatedStorage.ExampleModule")
        assert(capturedReport.progressPath)
        if kind ~= "progress-write-error" then
            assert(files[capturedReport.progressPath], "Progress must exist even after an export exception")
        end
        assert(capturedReport.lastProgress.detail.path=="ReplicatedStorage.ExampleModule")
    end
    if kind == "success" or kind == "remote-core" then
        assert(localReads == 0 and remoteReads == 1, "Default must not silently load a stale local core")
        assert(capturedReport.sourceOrigin and string.find(capturedReport.sourceOrigin, "/v0.6.0/", 1, true))
    elseif kind == "local-core" or kind == "local-core-missing" then
        assert(localReads == 1 and remoteReads == 0, "Local development must use only its explicit source")
    end
    if kind == "success" or kind == "remote-core" or kind == "local-core" then
        assert(called and string.find(text, "Output exists:", 1, true))
        assert(string.find(text, "validity is unverified", 1, true))
    elseif kind == "missing-output" then
        assert(called and string.find(text, "Output not found:", 1, true))
        assert(not string.find(text, "Output exists:", 1, true))
    elseif kind == "no-isfile" then
        assert(called and string.find(text, "existence remains unverified", 1, true))
    elseif kind == "geometry-omission" then
        assert(capturedReport.criticalGeometryOmissions==2 and capturedReport.outputExists==true)
        assert(string.find(text, "geometry/terrain property columns were omitted", 1, true))
    elseif kind == "legacy-core" then
        assert(capturedReport.engineVersion=="unknown" and string.find(text, "outdated local CORE_PATH", 1, true))
    elseif kind == "report-write-error" then
        assert(string.find(text, "Could not write diagnostic report", 1, true) and called)
    elseif kind == "progress-write-error" then
        assert(string.find(text, "Could not write progress checkpoint", 1, true) and called)
        assert(capturedReport.ok and files[capturedReport.outputPath], "Checkpoint failure must not abort the export")
    elseif kind ~= "runtime-error" and kind ~= "engine-reported-error" then
        assert(not called, "Exporter must not run after failed preflight")
    end
    for path in files do assert(not string.find(path, "CSP_WriteProbe_", 1, true), "Probe was not cleaned up") end
    successes += 1
end
for _, kind in {"success", "remote-core", "local-core", "local-core-missing", "missing-api", "probe-error", "corrupt-probe", "missing-core", "compile-error", "bad-core", "runtime-error", "missing-output", "no-isfile", "geometry-omission", "legacy-core", "report-write-error", "progress-write-error", "engine-reported-error"} do
    scenario(kind)
end
print("Preset runtime scenarios passed: " .. successes)
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--luau", default="luau", help="official Luau interpreter executable")
    args = parser.parse_args()
    catalog = json.loads((ROOT / "Script Presets/presets.json").read_text(encoding="utf-8"))
    options = {preset["id"]: preset["options"] for preset in catalog["presets"]}
    expected = dict(options["UltraCompleteSavePlace"], IgnoreList=["ModuleScript"])
    assert options["UltraNoModuleScripts"] == expected, "Only ModuleScript selection should differ from Ultra"
    files = sorted((ROOT / "Script Presets").glob("*.luau")) + sorted((ROOT / "Executors/Potassium/Script Presets").glob("*.luau"))
    if not files:
        raise SystemExit("No generated presets to test")
    for path in files:
        source = path.read_text(encoding="utf-8")
        if "]====]" in source:
            raise SystemExit("Preset contains a reserved test harness delimiter")
        harness = HARNESS.replace("__PRESET_SOURCE__", "[====[" + source + "]====]").replace("__POTASSIUM__", "true" if "Potassium" in path.parts else "false")
        harness = harness.replace("__NO_MODULES__", "true" if path.stem == "UltraNoModuleScripts" else "false")
        with tempfile.TemporaryDirectory(prefix="csp-preset-tests-") as directory:
            script = Path(directory) / "preset-test.luau"
            script.write_text(harness, encoding="utf-8")
            result = subprocess.run([args.luau, str(script)], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(f"{path.name}:\n{result.stdout}\n{result.stderr}")
        print(f"{path.relative_to(ROOT)}: {result.stdout.strip()}")
    print("Mock checks do not validate the actual Roblox engine or Studio output.")


if __name__ == "__main__":
    main()
