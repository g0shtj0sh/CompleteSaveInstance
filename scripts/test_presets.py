"""Exercise preset preflight and output evidence in a mocked Luau runtime."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HARNESS = r'''
local presetSource = __PRESET_SOURCE__
local successes = 0
local function scenario(kind)
    local files, messages = {}, {}
    local called = false
    local env = setmetatable({}, { __index = getfenv() })
    env.game = { PlaceId = 123 }
    env.game.HttpGet = function(_, url)
        assert(string.find(url, "/v0.2.0/saveinstance.luau", 1, true), "Core must be pinned")
        if kind == "missing-core" then error("network unavailable") end
        return "MOCK_CORE"
    end
    env.print = function(message) table.insert(messages, message) end
    env.warn = env.print
    env.writefile = function(path, content)
        if kind == "probe-error" then error("disk unavailable") end
        files[path] = kind == "corrupt-probe" and "wrong content" or content
    end
    env.readfile = function(path)
        if path == "CompleteSaveInstance/saveinstance.luau" then
            if kind == "missing-core" or kind == "remote-core" then error("core missing") end
            return "MOCK_CORE"
        end
        return files[path]
    end
    env.delfile = function(path) files[path] = nil end
    env.isfile = function(path) return files[path] ~= nil end
    env.loadstring = function(source, name)
        assert(source == "MOCK_CORE", "Unexpected core contents")
        if kind == "compile-error" then return nil, "mock syntax error" end
        return function()
            if kind == "bad-core" then return {} end
            return function(options)
                called = true
                assert(options.SafeMode == false and options.KillAllScripts == false)
                assert(options.ShutdownWhenDone == false and options.BoostFPS == false)
                assert(string.find(options.FilePath, "_123_", 1, true))
                if kind == "runtime-error" then error("serializer failed") end
                if kind ~= "missing-output" then files[options.FilePath] = "mock output" end
            end
        end
    end
    if kind == "missing-api" then env.writefile = false end
    if kind == "no-isfile" then env.isfile = false end
    local execute = assert(loadstring(presetSource, "preset under test"))
    setfenv(execute, env)
    local ok = pcall(execute)
    local text = table.concat(messages, "\n")
    local shouldFail = kind == "missing-api" or kind == "probe-error" or kind == "corrupt-probe"
        or kind == "missing-core" or kind == "compile-error" or kind == "bad-core" or kind == "runtime-error"
    assert(ok ~= shouldFail, "Unexpected scenario outcome: " .. kind)
    if kind == "success" or kind == "remote-core" then
        assert(called and string.find(text, "Output exists:", 1, true))
        assert(string.find(text, "validity is unverified", 1, true))
    elseif kind == "missing-output" then
        assert(called and string.find(text, "Output not found:", 1, true))
        assert(not string.find(text, "Output exists:", 1, true))
    elseif kind == "no-isfile" then
        assert(called and string.find(text, "existence remains unverified", 1, true))
    elseif kind ~= "runtime-error" then
        assert(not called, "Exporter must not run after failed preflight")
    end
    for path in files do assert(not string.find(path, "CSI_WriteProbe_", 1, true), "Probe was not cleaned up") end
    successes += 1
end
for _, kind in {"success", "remote-core", "missing-api", "probe-error", "corrupt-probe", "missing-core", "compile-error", "bad-core", "runtime-error", "missing-output", "no-isfile"} do
    scenario(kind)
end
print("Preset runtime scenarios passed: " .. successes)
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--luau", default="luau", help="official Luau interpreter executable")
    args = parser.parse_args()
    files = sorted((ROOT / "Script Presets").glob("*.luau"))
    if not files:
        raise SystemExit("No generated presets to test")
    for path in files:
        source = path.read_text(encoding="utf-8")
        if "]====]" in source:
            raise SystemExit("Preset contains a reserved test harness delimiter")
        harness = HARNESS.replace("__PRESET_SOURCE__", "[====[" + source + "]====]")
        with tempfile.TemporaryDirectory(prefix="csi-preset-tests-") as directory:
            script = Path(directory) / "preset-test.luau"
            script.write_text(harness, encoding="utf-8")
            result = subprocess.run([args.luau, str(script)], capture_output=True, text=True)
        if result.returncode:
            raise SystemExit(f"{path.name}:\n{result.stdout}\n{result.stderr}")
        print(f"{path.name}: {result.stdout.strip()}")
    print("Mock checks do not validate the actual Roblox engine or Studio output.")


if __name__ == "__main__":
    main()
