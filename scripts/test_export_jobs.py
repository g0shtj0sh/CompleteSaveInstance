"""Run actual job/deadline and chunk-builder functions with a deterministic scheduler."""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
local now, events, order = 0, {}, 0
local task = {}
local os = {clock=function() return now end}
local function schedule(thread, at)
    order += 1
    table.insert(events,{thread=thread,at=at,order=order})
end
function task.defer(f, ...)
    local args=table.pack(...)
    local thread=coroutine.create(function() f(table.unpack(args,1,args.n)) end)
    schedule(thread,now+0.001)
    return thread
end
function task.spawn(f, ...)
    local args=table.pack(...)
    local thread=coroutine.create(function() f(table.unpack(args,1,args.n)) end)
    local ok,wait=coroutine.resume(thread)
    assert(ok,tostring(wait))
    if type(wait)=="table" and wait.seconds then schedule(thread,now+wait.seconds) end
    return thread
end
function task.delay(delay,f)
    local thread=coroutine.create(f)
    schedule(thread,now+delay)
    return thread
end
local cancelled={}
function task.cancel(thread) cancelled[thread]=true end
function task.wait(seconds) return coroutine.yield({seconds=seconds or 0.01}) end
local function pump(duration)
    local stop=now+duration
    local iterations=0
    while #events>0 do
        table.sort(events,function(a,b) return a.at==b.at and a.order<b.order or a.at<b.at end)
        if events[1].at>stop then break end
        local event=table.remove(events,1)
        now=math.max(now,event.at)
        if not cancelled[event.thread] and coroutine.status(event.thread)~="dead" then
            local ok,wait=coroutine.resume(event.thread)
            assert(ok,tostring(wait))
            if type(wait)=="table" and wait.seconds then schedule(event.thread,now+wait.seconds) end
        end
        iterations+=1
        assert(iterations<100000,"Scheduler runaway")
    end
    now=stop
end
local function publishProgress() end
local lastYield=now
__TIMEOUT__
local fast=makeTimeoutHandler(0.5,function(value) return value end)
local fastDuration
task.defer(function()
    local fastStart=now
    for i=1,100 do
        local ok,value=fast(i)
        assert(ok and value==i)
    end
    fastDuration=now-fastStart
end)
pump(2)
assert(fastDuration==0,"Immediate jobs must not require a scheduler tick per script")
local zeroCalled=false
local zeroOk,_,zeroTimeout=makeTimeoutHandler(0,function() zeroCalled=true end)()
assert(not zeroOk and zeroTimeout and not zeroCalled,"A zero deadline must not start native work")
local concurrent=makeTimeoutHandler(0.5,function(value) task.wait(0.03);return value end)
local first,second
task.defer(function() first=table.pack(concurrent("first")) end)
task.defer(function() second=table.pack(concurrent("second")) end)
pump(0.8)
assert(first and first[1] and first[2]=="first","Concurrent calls must not overwrite a shared pending job")
assert(second and second[1] and second[2]=="second")
local result
task.defer(function() result=table.pack(makeTimeoutHandler(0.2,function() return nil,"tail",nil end)()) end)
pump(0.3)
assert(result.n==4 and result[1] and result[2]==nil and result[3]=="tail")
local timedOut
task.defer(function() timedOut=table.pack(makeTimeoutHandler(0.05,function() task.wait(5);return "late" end,"timeout marker")()) end)
pump(0.1)
assert(timedOut[1]==false and timedOut[2]=="timeout marker" and timedOut[3]==true)
local timeoutValue=timedOut
pump(6)
assert(timedOut==timeoutValue and timedOut[2]=="timeout marker","Late worker must not publish a stale result")
task.defer(function() result=table.pack(makeTimeoutHandler(0.05,function() now+=1;return "late native result" end)()) end)
pump(2)
assert(result[1]==false and result[3]==true,"A native call returning after its deadline must not be accepted as on-time success")
task.defer(function() result=table.pack(makeTimeoutHandler(0.2,function() error("native Lua error") end)()) end)
pump(0.3)
assert(not result[1] and string.find(result[2],"native Lua error",1,true))
local ok,value=makeTimeoutHandler(-1,function() return "unbounded" end)()
assert(ok and value=="unbounded")
print("Actual job handler passed: 100 immediate jobs without scheduler ticks, concurrent requests, trailing nils, yielding/zero timeouts, late result, errors, disabled timeout.")

local OPTIONS={BytecodeTimeout=0.2}
local reads=0
local function getscriptbytecode(script)
    reads+=1
    if script.Name=="bad" then error("unreadable bytecode") end
    if script.Name=="costly" then now+=0.02 end
    if script.Name=="waiting" then task.wait(0.15) end
    return "BYTES_"..script.Name
end
local StatusText={Text="Saving"}
local IsLoading, LoadingText=false,nil
local frameWaits=0
local WorkBudgetSeconds=0.004
lastYield=now
local function yieldFrame() frameWaits+=1;task.wait();lastYield=now end
local function ensureSpinner() end
local function setProgress() end
local function warn() end
local ExportReport={scriptJobs={bytecodeCalls=0,decompileCalls=0,failed=0,timedOut=0,failures={}}}
__YIELDIFDUE__
__LOADING__
__SCRIPT_JOB__
__BYTECODE__
local a,b,bad={Name="a"},{Name="b"},{Name="bad"}
task.defer(function()
    assert(select(2,getbytecode(a))=="BYTES_a")
    assert(select(2,getbytecode(a))=="BYTES_a")
    assert(select(2,getbytecode(b))=="BYTES_b")
    assert(not getbytecode(bad))
    assert(not getbytecode(bad))
end)
pump(1)
assert(reads==3,"Bytecode cache must avoid duplicate native reads, including repeated failures")
print("Actual bytecode wrapper passed: per-instance success and failure memoization.")

local immediateBatchDuration,immediateBatchWaits
task.defer(function()
    lastYield=now
    local started,waits=now,frameWaits
    for i=1,100 do assert(select(2,getbytecode({Name="batch"..i}))=="BYTES_batch"..i) end
    immediateBatchDuration,immediateBatchWaits=now-started,frameWaits-waits
end)
pump(3)
assert(immediateBatchDuration==0 and immediateBatchWaits==0,"Fast bytecode jobs must not force a UI frame per script")
local slicedWaits
task.defer(function()
    lastYield=now
    local waits=frameWaits
    for _=1,20 do assert(select(2,getbytecode({Name="costly"}))=="BYTES_costly") end
    slicedWaits=frameWaits-waits
end)
pump(3)
assert(slicedWaits and slicedWaits>0 and slicedWaits<20,"CPU work must yield periodically without waiting for every script")
assert(StatusText.Text=="Saving" and IsLoading==false)
assert(ExportReport.scriptJobs.bytecodeSeconds>=0.39 and ExportReport.scriptJobs.bytecodeSeconds<0.5)
local asyncWaits
task.defer(function()
    lastYield=now
    local waits=frameWaits
    assert(select(2,getbytecode({Name="waiting"}))=="BYTES_waiting")
    assert(select(2,getbytecode({Name="after-wait"}))=="BYTES_after-wait")
    asyncWaits=frameWaits-waits
end)
pump(1)
assert(asyncWaits==0,"A yielding job must not force another work-slice frame wait before the next call")
print("Actual UI/job/bytecode pipeline passed: 100 fast jobs without frame waits, periodic yields for CPU work, no redundant yield after async work, timing counters, status restoration.")

local ScriptCache, DecompileJobless = true, false
local ldeccache, ldecompile = {}, nil
local EXECUTOR_NAME, __DEBUG_MODE = "Potassium", nil
OPTIONS.DecompileTimeout=0.2
local decompileCalls, decompileTarget, failDecompile = 0, nil, false
local function decompile(target)
    decompileCalls+=1
    decompileTarget=target
    if failDecompile then error("decompiler unavailable") end
    return "return 42"
end
__DECOMPILE__
local source
task.defer(function() source=ldecompile(a) end)
pump(1)
assert(source=="return 42" and decompileTarget=="BYTES_a", "Potassium must reuse the cached bytecode overload")
task.defer(function() assert(ldecompile(a)=="return 42") end)
pump(1)
assert(decompileCalls==1,"Successful source must be cached")
ldeccache.BYTES_a="--[[ Failed to decompile. Reason:\nold timeout\n]]"
task.defer(function() assert(ldecompile(a)=="return 42") end)
pump(1)
assert(decompileCalls==2,"Old cached failure must be retried")
EXECUTOR_NAME="Other runtime"
task.defer(function() assert(ldecompile(b)=="return 42") end)
pump(1)
assert(decompileTarget==b,"Other runtimes retain the Instance overload")
local retry={Name="retry"}
failDecompile=true
task.defer(function() source=ldecompile(retry) end)
pump(1)
assert(string.find(source,"Failed to decompile",1,true) and ldeccache.BYTES_retry==nil)
failDecompile=false
task.defer(function() assert(ldecompile(retry)=="return 42") end)
pump(1)
assert(ldeccache.BYTES_retry=="return 42","Failed output must not poison the source cache")
print("Actual decompilation passed: Potassium bytecode overload, ordinary Instance overload, success caching, failed-cache retries.")

local ExportReport={compression={bypassedSource=0,bypassedLarge=0,failed=0}}
local function setProgress() end
local function setMeter() end
__CHUNK__
local raw=string.rep("X",32)
local function chunk(value)
    return {len=#value,buf=buffer.fromstring(value),tostring=function() return value end}
end
local calls=0
local function compress() calls+=1;return "ZIP" end
local c=buildChunk("PROP",chunk(raw),compress,"Source")
assert(c.tailLen==#raw and calls==0 and buffer.readu32(c.buf,4)==0)
c=buildChunk("PROP",chunk(string.rep("X",8*1024*1024+1)),compress,"SmoothGrid")
assert(c.tailLen==8*1024*1024+1 and calls==0)
c=buildChunk("PROP",chunk(raw),compress,"Name")
assert(c.str=="ZIP" and buffer.readu32(c.buf,4)==3 and buffer.readu32(c.buf,8)==32)
for _,badCompressor in {function() error("compressor error") end,function() return "" end,function() return 42 end} do
    c=buildChunk("PROP",chunk(raw),badCompressor,"Name")
    assert(c.tailLen==#raw and buffer.readstring(c.tailBuf,0,c.tailLen)==raw)
    assert(buffer.readu32(c.buf,4)==0 and buffer.readu32(c.buf,8)==#raw)
end
assert(ExportReport.compression.bypassedSource==1 and ExportReport.compression.bypassedLarge==1 and ExportReport.compression.failed==3)
print("Actual chunk builder passed: raw source/large chunks, native failure fallback, valid uncompressed headers, compression preservation.")
'''

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--luau",default="luau")
    parser.add_argument("--source",type=Path,default=ROOT/"saveinstance.luau")
    args=parser.parse_args()
    source=args.source.read_text(encoding="utf-8-sig")
    timeout=source.split("\tlocal function makeTimeoutHandler(",1)[1].split("\tlocal decompileIgnoreMap",1)[0]
    timeout=timeout.split("\tlocal function runScriptJob",1)[0]
    yielding=source.split("\tlocal function yieldIfDue()",1)[1].split("\tlocal IsLoading",1)[0]
    loading=source.split("\tlocal function run_with_loading(",1)[1].split("\tlocal function makeTimeoutHandler",1)[0]
    script_job=source.split("\tlocal function runScriptJob(",1)[1].split("\tlocal decompileIgnoreMap",1)[0]
    bytecode=source.split("\tlocal getbytecode\n",1)[1].split("\tlocal SaveBytecode",1)[0]
    decompile=source.split("\telseif decompile then\n",1)[1].split('\telse\n\t\tldecompile = function()\n\t\t\treturn "-- Your Executor',1)[0]
    chunk=source.split("\t\tlocal function buildChunk(",1)[1].split("\t\tlocal compress = CompressionMode",1)[0]
    program=HARNESS.replace("__TIMEOUT__","local function makeTimeoutHandler("+timeout).replace("__YIELDIFDUE__","local function yieldIfDue()"+yielding).replace("__LOADING__","local function run_with_loading("+loading).replace("__SCRIPT_JOB__","local function runScriptJob("+script_job).replace("__BYTECODE__","local getbytecode\n"+bytecode).replace("__DECOMPILE__",decompile).replace("__CHUNK__","local function buildChunk("+chunk)
    with tempfile.TemporaryDirectory(prefix="csp-export-jobs-") as directory:
        path=Path(directory)/"jobs.luau"
        path.write_text(program,encoding="utf-8")
        result=subprocess.run([args.luau,str(path)],capture_output=True,text=True)
    print(result.stdout,end="")
    if result.returncode: raise SystemExit(result.stderr)

if __name__=="__main__": main()
