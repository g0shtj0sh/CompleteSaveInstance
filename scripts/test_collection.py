"""Exercise real collection of geometry nested beneath excluded ModuleScripts."""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
local function node(class,name,children)
    return {ClassName=class,Name=name,Archivable=true,
        GetChildren=function() return children or {} end,
        IsA=function(self,want) return self.ClassName==want end}
end
local mesh=node('MeshPart','Car body')
local road=node('UnionOperation','Road')
local nested=node('ModuleScript','Nested',{road})
local module=node('ModuleScript','VehicleAssets',{mesh,nested})
local wheel=node('Part','Wheel')
local root=node('Workspace','Workspace',{module,wheel})
local OPTIONS={ExcludeModuleScripts=false}
local InstancesOverrides,ClassSerializableCache={},{}
local IgnoreList,DecompileIgnore,NotCreatableFixes={},{},{}
local decompileIgnoreMap={}
local ClassList={Workspace={},ModuleScript={},MeshPart={},UnionOperation={},Part={},Folder={}}
local IgnoreNotArchivable=false
local SaveNotCreatable=true
local SaveNotCreatableWillBeEnabled=false
local TreatUnionsAsParts=false
local HasAutoRemaps=false
local ExportReport={}
local Progress={}
local function yieldIfDue() end
local function isClassSerializable() return true end
local function replaceClassName() error('Unexpected not-creatable remap') end
__COLLECT__
__REF_CHECK__
local original=collect({root})
assert(original.instCount==6 and original.entries[module].class=='ModuleScript')
IgnoreList.ModuleScript=true
local legacy=collect({root})
assert(legacy.instCount==2 and legacy.entries[mesh]==nil and legacy.entries[road]==nil,
    'Negative control: a class IgnoreList entry loses nested geometry')
IgnoreList.ModuleScript=nil
OPTIONS.ExcludeModuleScripts=true
local result=collect({root})
assert(result.instCount==original.instCount,'Excluding module code must preserve the instance tree')
for _,object in {module,nested} do
    local entry=result.entries[object]
    assert(entry.class=='Folder' and entry.tag=='Folder' and entry.propClass=='Instance')
    assert(entry.override.Properties.Name==object.Name, 'Keep container names')
    assert(entry.propClass~='ModuleScript', 'Never select ModuleScript.Source properties')
end
assert(result.entries[mesh].parent==module and result.entries[nested].parent==module)
assert(result.entries[road].parent==nested and result.entries[wheel].parent==root)
assert(result.entries[module].children[1]==mesh and result.entries[module].children[2]==nested)
assert(result.refs[module]~=nil and result.refs[road]~=nil,'Both binary parent referents survive')
assert(result.roots[1]==root and #result.ordered==6)
assert(ExportReport.moduleScriptContainers==2 and HasAutoRemaps)
assert(not refIsInvalid(module,'Instance') and not refIsInvalid(module,'Folder'))
assert(refIsInvalid(module,'ModuleScript'),'Do not write a Folder referent into a ModuleScript-only property')
InstancesOverrides={}
IgnoreList.ModuleScript=true
local explicit=collect({root})
assert(explicit.instCount==2,'Explicit IgnoreList rules still take priority')
print('Actual collection passed: default modules, negative control, preserved descendant geometry, Folder containers, hierarchy, referents, explicit ignore precedence.')
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--luau',default='luau')
    args=parser.parse_args()
    source=(ROOT/'saveinstance.luau').read_text(encoding='utf-8')
    collect='local function collect(roots)'+source.split('local function collect(roots)',1)[1].split('\tlocal pendingExtras =',1)[0]
    program=HARNESS.replace('__COLLECT__',collect)
    ref_check='local function refIsInvalid('+source.split('local function refIsInvalid(',1)[1].split('\tlocal function nilIsValid(',1)[0]
    program=program.replace('__REF_CHECK__',ref_check)
    with tempfile.TemporaryDirectory(prefix='csp-collection-') as directory:
        path=Path(directory)/'collection.luau'
        path.write_text(program,encoding='utf-8')
        result=subprocess.run([args.luau,str(path)],capture_output=True,text=True)
    print(result.stdout,end='')
    if result.returncode: raise SystemExit(result.stderr)


if __name__=='__main__': main()
