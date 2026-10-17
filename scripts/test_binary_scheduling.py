"""Check actual binary encoders against recorded bytes and across cooperative yields."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'scripts/fixtures/binary-encoder-digests.json'
HARNESS=r'''
local function index(value,key) return value[key] end
local function frame(x,y,z,rot)
    local result={x=x,y=y,z=z,rot=rot}
    function result:GetComponents()
        local r=self.rot or {1,0,0,0,1,0,0,0,1}
        return self.x,self.y,self.z,table.unpack(r)
    end
    return result
end
local CFrame={identity=frame(0,0,0)}
local SecurityCapabilities={new=function() return {} end}
local Enum={ContentSourceType={Uri='Uri'}}
__ENCODERS__
local Buffer={}
Buffer.__index=Buffer
function Buffer:reserve(count)
    if self.len+count>buffer.len(self.buf) then
        local nextBuffer=buffer.create(math.max(self.len+count,buffer.len(self.buf)*2))
        buffer.copy(nextBuffer,0,self.buf,0,self.len)
        self.buf=nextBuffer
    end
end
function Buffer:allocRegion(count) self:reserve(count);local at=self.len;self.len+=count;return at end
function Buffer:writeu8(v) local at=self:allocRegion(1);buffer.writeu8(self.buf,at,v) end
function Buffer:writeu16(v) local at=self:allocRegion(2);buffer.writeu16(self.buf,at,v) end
function Buffer:writeu32(v) local at=self:allocRegion(4);buffer.writeu32(self.buf,at,v) end
function Buffer:writei16(v) local at=self:allocRegion(2);buffer.writei16(self.buf,at,v) end
function Buffer:writestring(v) self:reserve(#v);buffer.writestring(self.buf,self.len,v);self.len+=#v end
function Buffer:writeLenString(v) self:writeu32(#v);self:writestring(v) end
local n=1025
local factories={
    string=function(i) return 'item\0'..(i%13) end,
    bool=function(i) return i%3==0 end,
    int=function(i) return (i%2==0 and -1 or 1)*i*777 end,
    float=function(i) return (i-512)/7 end,
    double=function(i) return (i-512)/13 end,
    int64=function(i) return (i%2==0 and -1 or 1)*i*4294967 end,
    UDim=function(i) return {Scale=i/1024,Offset=-i} end,
    UDim2=function(i) return {X={Scale=i/1024,Offset=i},Y={Scale=-i/512,Offset=-i}} end,
    Ray=function(i) return {Origin={X=i,Y=-i,Z=i/3},Direction={X=0.5,Y=-0.25,Z=1}} end,
    Faces=function(i) return {Right=i%2==0,Top=i%3==0,Back=true,Front=false,Bottom=i%5==0} end,
    Axes=function(i) return {X=i%2==0,Y=i%3==0,Z=true} end,
    BrickColor=function(i) return {Number=i%2048} end,
    Color3=function(i) return {R=(i%255)/255,G=0.5,B=0.25} end,
    Color3uint8=function(i) return {R=(i%255)/255,G=0.5,B=0.25} end,
    Vector2=function(i) return {X=i/7,Y=-i/3} end,
    Vector3=function(i) return {X=i/7,Y=-i/3,Z=i/9} end,
    Vector2int16=function(i) return {X=i,Y=-i} end,
    Vector3int16=function(i) return {X=i,Y=-i,Z=i*2} end,
    CFrame=function(i) return frame(i,-i,i/3,i%2==0 and {0.6,0,0.8,0,1,0,-0.8,0,0.6} or nil) end,
    OptionalCoordinateFrame=function(i) if i%4~=0 then return frame(i,-i,0) end end,
    Enum=function(i) return {Value=i%7} end,
    NumberSequence=function(i) return {Keypoints={{Time=0,Value=i,Envelope=0},{Time=1,Value=-i,Envelope=0.2}}} end,
    ColorSequence=function(i) return {Keypoints={{Time=0,Value={R=0.5,G=0.25,B=0}},{Time=1,Value={R=1,G=0.5,B=0.25}}}} end,
    NumberRange=function(i) return {Min=-i,Max=i} end,
    Rect=function(i) return {Min={X=-i,Y=-i/2},Max={X=i,Y=i/3}} end,
    PhysicalProperties=function(i) if i%4~=0 then return {Density=1,Friction=0.5,Elasticity=0.2,FrictionWeight=1,ElasticityWeight=2,AcousticAbsorption=0.1} end end,
    UniqueId=function(i) return string.format('%016x%08x%08x',i*71,i*91,i) end,
    Font=function(i) return {Family='rbxasset://family'..i%3,Weight={Value=400},Style={Value=i%2}} end,
    SecurityCapabilities=function(i) return i%2==0 and 'Restricted | RunClientScript' or 'RunServerScript' end,
    Content=function(i) return {SourceType=i%3==0 and 'None' or 'Uri',Uri='rbxassetid://'..i} end,
    SharedString=function(i) return 'SHARED'..i%7 end,
    Referent=function(i) if i%3~=0 then return {key=i} end end,
}
local function encode(name,factory,cooperative)
    local values,refs={},{}
    for i=1,n do values[i]=factory(i);if values[i] then refs[values[i]]=i*7 end end
    local context=name=='SharedString' and {count=0,hashes={},order={}} or refs
    local sbuf=setmetatable({buf=buffer.create(64),len=0},Buffer)
    local yields=0
    if cooperative then sbuf.yieldIfDue=function() yields+=1;coroutine.yield('budget') end end
    local worker=coroutine.create(function() Binary_Encoders[name](sbuf,values,n,context) end)
    while coroutine.status(worker)~='dead' do
        local ok,message=coroutine.resume(worker)
        assert(ok,name..': '..tostring(message))
    end
    return buffer.readstring(sbuf.buf,0,sbuf.len),yields
end
for name,factory in factories do
    local expected=encode(name,factory,false)
    local actual,yields=encode(name,factory,true)
    assert(actual==expected,name..': scheduling changed encoded bytes')
    if __REQUIRE_YIELDS__ then assert(yields>0,name..': large columns must cooperate with scheduler') end
    local hex=string.gsub(actual,'.',function(char) return string.format('%02x',string.byte(char)) end)
    print(name..'\t'..hex)
end
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--luau',default='luau')
    parser.add_argument('--source',type=Path,default=ROOT/'saveinstance.luau')
    parser.add_argument('--record',action='store_true',help='Explicitly record a reviewed baseline revision')
    args=parser.parse_args()
    source=args.source.read_text(encoding='utf-8')
    encoders='local Type_Ids ='+source.split('local Type_Ids =',1)[1].split('local ESCAPES_PATTERN',1)[0]
    program=HARNESS.replace('__ENCODERS__',encoders).replace('__REQUIRE_YIELDS__','false' if args.record else 'true')
    with tempfile.TemporaryDirectory(prefix='csp-binary-scheduling-') as directory:
        path=Path(directory)/'encoders.luau'
        path.write_text(program,encoding='utf-8')
        result=subprocess.run([args.luau,str(path)],capture_output=True,text=True)
    if result.returncode: raise SystemExit(result.stderr)
    digests={}
    for line in result.stdout.splitlines():
        name,hex_bytes=line.split('\t',1)
        data=bytes.fromhex(hex_bytes)
        digests[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    if args.record:
        FIXTURE.parent.mkdir(parents=True,exist_ok=True)
        FIXTURE.write_text(json.dumps({'baseline':'v0.4.4','sourceHash':hashlib.sha256(source.encode()).hexdigest(),'valuesPerColumn':1025,'encoders':digests},indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print('Recorded binary baseline:',len(digests),'encoder fixtures')
    else:
        expected=json.loads(FIXTURE.read_text(encoding='utf-8'))['encoders']
        if digests!=expected: raise SystemExit('Binary encoder output differs from recorded v0.4.4 bytes')
        print(f'Actual binary encoders passed: {len(digests)} types x 1025 values; exact v0.4.4 bytes preserved across cooperative yields.')


if __name__=='__main__': main()
