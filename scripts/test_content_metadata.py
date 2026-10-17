"""Exercise the real metadata selector with conflicting mesh Content metadata."""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r'''
__ARRAY__
__EXCEPTIONS__
local NotScriptableFixes = {}
local RiskyServicesDisabled = {Reflection=false}
local REFLECTION_FILTER = {}
local service = {ReflectionService={GetPropertiesOfClass=function()
    return {{Name='MeshContent',Serialized=false},{Name='TextureContent',Serialized=false},
        {Name='Content',Serialized=false},{Name='OtherContent',Serialized=false}}
end}}
local function buildMetadata(API_Dump)
__SELECTOR__
end
local function property(name,canLoad,canSave,valueType)
    return {Name=name,MemberType='Property',Serialization={CanLoad=canLoad,CanSave=canSave},
        ValueType={Name=valueType or 'Content',Category='DataType'}}
end
local function fixture(canSave)
    return {
        {Name='Instance',Members={property('Name',true,true,'string'),property('SourceAssetId',true,true,'int64')}},
        {Name='MeshPart',Superclass='Instance',Members={property('MeshContent',true,canSave),
            property('TextureContent',true,canSave),property('OtherContent',true,true)}},
        {Name='PartOperation',Superclass='Instance',Members={property('Content',true,canSave)}},
    }
end
local function has(classes,className,name)
    for _,p in classes[className].Properties do if p.Name==name then return true end end
    return false
end
for _,canSave in {true,false} do
    local result=buildMetadata(fixture(canSave))
    assert(has(result,'MeshPart','MeshContent') and has(result,'MeshPart','TextureContent'))
    assert(has(result,'PartOperation','Content'))
    assert(not has(result,'MeshPart','OtherContent'),'Do not whitelist unrelated Content properties')
    assert(has(result,'Instance','Name') and not has(result,'Instance','SourceAssetId'))
end
local nonLoadable=fixture(true)
nonLoadable[2].Members[1].Serialization.CanLoad=false
assert(not has(buildMetadata(nonLoadable),'MeshPart','MeshContent'),'CanLoad remains required')
ClassPropertyExceptions.Whitelist={}
local old=buildMetadata(fixture(true))
assert(not has(old,'MeshPart','MeshContent') and not has(old,'PartOperation','Content'),
    'Negative control must reproduce Reflection dropping modern mesh references')
print('Actual metadata selection passed: modern mesh references, Reflection conflict, API flags, CanLoad, unrelated filtering, blacklist, negative control.')
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--luau', default='luau')
    args = parser.parse_args()
    source = (ROOT / 'saveinstance.luau').read_text(encoding='utf-8')
    array = 'local function arrayToDict(' + source.split('local function arrayToDict(', 1)[1].split('local GLOBAL_ENV =', 1)[0]
    exceptions = 'local ClassPropertyExceptions = arrayToDict(' + source.split('local ClassPropertyExceptions = arrayToDict(', 1)[1].split('-- Minimal valid CSGPHS', 1)[0]
    selector = 'local classList = {}' + source.split('local classList = {}', 1)[1].split('\t\treturn classList\n\tend', 1)[0] + '\nreturn classList'
    program = HARNESS.replace('__ARRAY__', array).replace('__EXCEPTIONS__', exceptions).replace('__SELECTOR__', selector)
    with tempfile.TemporaryDirectory(prefix='csp-content-') as directory:
        path = Path(directory) / 'metadata.luau'
        path.write_text(program, encoding='utf-8')
        result = subprocess.run([args.luau, str(path)], capture_output=True, text=True)
    print(result.stdout, end='')
    if result.returncode:
        raise SystemExit(result.stderr)


if __name__ == '__main__':
    main()
