"""Exercise actual progress models, GUI construction, refresh throttling and append counters."""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
local now=0
local os={clock=function() return now end}
local function dim(scale,offset) return {Scale=scale,Offset=offset} end
local UDim2={new=function(xs,xo,ys,yo) return {X=dim(xs,xo),Y=dim(ys,yo)} end}
function UDim2.fromScale(x,y) return UDim2.new(x,0,y,0) end
function UDim2.fromOffset(x,y) return UDim2.new(0,x,0,y) end
local UDim={new=dim}
local Vector2={new=function(x,y) return {X=x,Y=y} end}
local Color3={fromRGB=function(r,g,b) return {R=r,G=g,B=b} end}
local Enum={Font={Code='Code'},TextXAlignment={Left='Left'},TextTruncate={AtEnd='AtEnd'}}
local created={}
local Instance={new=function(class)
    local object={ClassName=class}
    table.insert(created,object)
    return object
end}
__VIEW_AND_GUI__
local display=createStatusDisplay()
assert(display.status.Parent==display.caption.Parent)
assert(display.fill.Parent.Parent==display.status.Parent)
assert(display.fill.Parent.Position.Y.Offset > display.status.Position.Y.Offset+display.status.Size.Y.Offset)
assert(display.gui.ResetOnSpawn==false and display.gui.IgnoreGuiInset)
local view=progressView({phase='scripts',meter={label='ModuleScript.Source',completed=25,total=100}},0)
assert(view.fraction==0.25 and not view.indeterminate and string.find(view.text,'25 / 100',1,true))
local idle={phase='collect',meter={label='Collecting instances',completed=42}}
local a,b=progressView(idle,0.2),progressView(idle,0.9)
assert(a.indeterminate and a.fraction==b.fraction and a.offset~=b.offset)
assert(a.text==b.text and not string.find(a.text,'%',1,true),'Unknown totals must not invent percentages')
assert(progressView({phase='collect',meter={label='Empty',completed=0,total=0}},1).indeterminate)
assert(progressView({phase='completed'},1).fraction==1)
local failed=progressView({phase='failed',meter={label='Writing bytes',completed=3,total=10}},1)
assert(failed.failed and failed.fraction==0.3 and not failed.indeterminate)

local renders=0
local nativeRender=renderStatusDisplay
renderStatusDisplay=function(...) renders+=1;return nativeRender(...) end
local ExportReport={engineVersion='test'}
local writes=0
local RuntimeAdapter={onProgress=function(progress)
    writes+=1
    assert(progress.engineVersion=='test')
end}
local ProgressDisplay=display
__PROGRESS_STATE__
local meter=setMeter('ModuleScript.Source',10,40)
setProgress('read-property',{},true)
refreshProgressDisplay(true)
assert(display.fill.Size.X.Scale==0.25)
local before=renders
meter.completed=20
for _=1,20 do publishProgress(true) end
assert(writes>=20 and renders==before,'Disk checkpoints must not force a GUI render per job')
now=0.05
refreshProgressDisplay(false)
assert(display.fill.Size.X.Scale==0.25)
now=0.11
refreshProgressDisplay(false)
assert(display.fill.Size.X.Scale==0.5 and renders==before+1)
RuntimeAdapter.onProgress=function() error('checkpoint unavailable') end
assert(pcall(setProgress,'scripts',{},true))
setProgress('failed',{},true)
assert(display.fill.Size.X.Scale==0.5 and display.fill.BackgroundColor3.R==255)
setProgress('completed',{},true)
assert(display.fill.Size.X.Scale==1)
print('Actual progress UI passed: hierarchy below status, real counters, unknown totals, failures, throttled refresh, protected checkpoints, completion.')

local function budgetFor(value)
    local OPTIONS={WorkBudgetMs=value}
    local ExportReport={}
__WORK_BUDGET__
    return WorkBudgetSeconds,ExportReport.workBudgetMs
end
assert(budgetFor(nil)==0.004 and budgetFor(0)==0.001 and budgetFor(100)==0.016)
assert(budgetFor(0/0)==0.004 and budgetFor(false)==0.004 and budgetFor('10')==0.004)
local seconds,reported=budgetFor(2)
assert(seconds==0.002 and reported==2)
print('Actual work budget passed: 4ms default, numeric validation, 1-16ms clamp, report value.')

local objects={{Name='one'},{Name='two'},{Name='three'}}
local ctx={entries={}}
for _,object in objects do ctx.entries[object]={class='ModuleScript'} end
local __BREAK='unavailable'
local mode='success'
local function yieldIfDue() end
local function readProperty(object)
    local at=object==objects[1] and 1 or object==objects[2] and 2 or 3
    assert(Progress.meter.completed==at-1,'A source entry must not count as completed before its read returns')
    setProgress('scripts',{path=object.Name},true)
    if at==2 and mode=='error' then error('unreadable source') end
    if at==2 and mode=='unavailable' then return __BREAK end
    return 'source_'..object.Name
end
__READ_ALL__
local values=readAll(objects,{Name='Source'})
assert(values[3]=='source_three' and Progress.meter.completed==3 and Progress.meter.total==3)
assert(Progress.meter.label=='ModuleScript.Source')
mode='error'
local missing,at,reason=readAll(objects,{Name='Source'})
assert(missing==nil and at==2 and Progress.meter.completed==2 and string.find(reason,'read_error',1,true))
mode='unavailable'
missing,at,reason=readAll(objects,{Name='Source'})
assert(missing==nil and at==2 and Progress.meter.completed==2 and reason=='unavailable_after_fallbacks')
print('Actual column meter passed: source jobs retain the stage total, post-read counts, and partial errors never imply full coverage.')

local function writerScenario(chunks,failAt)
    local writeTotal=0
    for _,chunk in chunks do writeTotal+=#chunk end
    local writeMeter={completed=0,total=writeTotal}
    local placename='fixture.rbxl'
    local parts,actualBytes,attempts,publishes={},0,0,0
    local task={wait=function() end}
    local function writefile(path,value) assert(path==placename and value=='') end
    local function appendfile(path,value)
        assert(path==placename)
        assert(writeMeter.completed==actualBytes,'Never claim bytes before the native append returns')
        attempts+=1
        if attempts==failAt then error('disk failure') end
        table.insert(parts,value)
        actualBytes+=#value
    end
    local function publishProgress()
        publishes+=1
        assert(writeMeter.completed==actualBytes and actualBytes<=writeTotal)
    end
    local function run_with_loading(_,_,_,f,...) return f(...) end
    local function run()
__APPEND_WRITER__
    end
    local ok=pcall(run)
    if failAt then
        assert(not ok and writeMeter.completed==actualBytes and actualBytes<writeTotal)
    else
        assert(ok and writeMeter.completed==writeTotal)
        assert(table.concat(parts)==table.concat(chunks),'Chunk batching must preserve exact file bytes')
        assert(publishes==#parts)
    end
end
local chunks={string.rep('a',100000),string.rep('b',5000000),string.rep('c',9300000),string.rep('d',123456),''}
writerScenario(chunks)
writerScenario(chunks,2)
writerScenario({})
print('Actual append writer passed: exact bytes across small/large batches, post-write progress, partial failure, empty output.')

local IsLoading,LoadingThread=true,{}
local cancelled,disconnected=0,0
local task={cancel=function() cancelled+=1 end}
local Connections={{Disconnect=function() disconnected+=1 end},{Disconnect=function() disconnected+=1 end}}
local GLOBAL_ENV={fixture=true}
local placename='fixture'
__CLEANUP__
Cleanup()
assert(not IsLoading and LoadingThread==nil and cancelled==1 and disconnected==2 and GLOBAL_ENV.fixture==nil)
print('Actual cleanup passed: spinner cancellation and connection release, including the progress heartbeat.')
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--luau',default='luau')
    args=parser.parse_args()
    source=(ROOT/'saveinstance.luau').read_text(encoding='utf-8')
    view='local function progressView('+source.split('local function progressView(',1)[1].split('--[=[',1)[0]
    state='local progressStarted ='+source.split('\tlocal progressStarted =',1)[1].split('\tlocal OPTIONS =',1)[0]
    writer='local SEGMENT_SIZE ='+source.split('\t\t\tlocal SEGMENT_SIZE =',1)[1].split('\t\telseif writefile then',1)[0]
    cleanup='local function Cleanup()'+source.split('\tlocal function Cleanup()',1)[1].split('\tdo\n\t\tlocal Players',1)[0]
    budget='local WorkBudgetMs ='+source.split('\tlocal WorkBudgetMs =',1)[1].split('\tlocal function yieldFrame()',1)[0]
    read_all='local function readAll('+source.split('\t\tlocal function readAll(',1)[1].split('\t\tlocal function buildChunk',1)[0]
    program=HARNESS.replace('__VIEW_AND_GUI__',view).replace('__PROGRESS_STATE__',state).replace('__WORK_BUDGET__',budget).replace('__READ_ALL__',read_all).replace('__APPEND_WRITER__',writer).replace('__CLEANUP__',cleanup)
    with tempfile.TemporaryDirectory(prefix='csp-progress-ui-') as directory:
        path=Path(directory)/'progress.luau'
        path.write_text(program,encoding='utf-8')
        result=subprocess.run([args.luau,str(path)],capture_output=True,text=True)
    print(result.stdout,end='')
    if result.returncode: raise SystemExit(result.stderr)


if __name__=='__main__': main()
