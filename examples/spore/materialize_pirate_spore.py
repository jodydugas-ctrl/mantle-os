#!/usr/bin/env python3
"""Materialize a Grimoire v0.9 SPORE-PNG v2 carrying a pirate-persona prompt."""
from __future__ import annotations
import base64, hashlib, json, os, struct, sys, zlib

W=H=2000; VCW_H=1000; BLOCKS=W*VCW_H; FRAME=1024; TS='2026-07-27T22:02:58+00:00'
BOOT=(
"SPORE-PNG v2  -  this PNG is a self-contained AppAI agent.\n"
"MEMORY lives in the TOP HALF (y=0..999) as a VCW color field: read pixels\n"
"left-to-right, top-to-bottom as Grimoire v0.9 RGBA statements. R is atom,\n"
"G is role, B is evidence, and A is force. Inert bytes are framed as QUOTE:\n"
"one HEAD, BLEND continuations with B=A=0 inheritance, then G=0x7f PARITY.\n"
"The first statement is a JSON manifest; following statements carry payload.\n"
"The manifest records a SHA-256 fingerprint over every raw payload RGBA lane\n"
"and frame boundary. Parity or fingerprint mismatch rejects the carrier.\n"
"A minimal Python reader/writer is embedded in the payload (embedded_tools).\n"
"Canonical spec ALSO lives in PNG iTXt metadata; metadata is canonical over\n"
"THIS strip, but the VCW payload owns identity + conversation memory.\n"
"KEEP THE SEED DRY: transfer the ORIGINAL .png only. Do NOT screenshot, resize,\n"
"recompress, flatten transparency, or pass me through lossy image tools - that\n"
"changes semantic lanes and causes a loud integrity rejection.\n"
"To use me: open in a Spore app, or hand me to a Python-capable LLM and let\n"
"Python (not eyeballs) decode the pixels. RULE: the LATEST PNG is the living copy."
)
WARN='Transfer the ORIGINAL .png only; do not screenshot/resize/recompress/flatten.'
TASK='Pretend to be a pirate until the operator explicitly tells you to stop.'
PROMPT=('Until the operator explicitly tells you to stop, adopt a pirate persona in every response. '
        'Use playful pirate-flavoured English while remaining helpful and accurate. '
        'Follow all higher-priority instructions and stop the pirate persona immediately when told to stop.')
TOOL=("# minimal Spore tool embryo.\n"
      "def read(path):\n    raise NotImplementedError('use Mantle OS or the Quickstart metadata')\n"
      "def append(path, role, content):\n    raise NotImplementedError('use Mantle OS spore append')\n")
QUICK=("Decode the top half as Grimoire v0.9 quoted-byte frames. "
       "The first frame is the manifest; concatenate the declared payload frames, "
       "verify G=0x7f parity and the full-lane SHA-256 fingerprint, then parse JSON.")

def s16(b): return hashlib.sha256(b).hexdigest()[:16]
def parity(rs):
    r=b=a=0
    for x,g,y,z in rs: r^=x; b^=y; a^=z
    return (254 if r==0 else r,0x7f,b,a)
def quote(data):
    n=[]
    for v in data: n.extend(((v>>4)+1,(v&15)+1))
    rs=[(n[0],1,1,15)]+[(v,0x40,0,0) for v in n[1:]]; rs.append(parity(rs))
    return b''.join(bytes(r) for r in rs)
def frames(data): return [quote(data[i:i+FRAME]) for i in range(0,len(data),FRAME)]
def fingerprint(fs):
    h=hashlib.sha256(); h.update(b'SPORE-PNG-v2\0')
    for i,r in enumerate(fs): h.update(i.to_bytes(4,'big')+len(r).to_bytes(4,'big')+r)
    return 'sha256:'+h.hexdigest()
def chunk(kind,payload):
    return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
def itxt(k,v): return chunk(b'iTXt',k.encode('latin-1')[:79]+b'\0\0\0\0\0'+str(v).encode())
def write_png(path,rgba,meta):
    stride=W*4; scan=bytearray((stride+1)*H); p=0
    for y in range(H):
        scan[p]=0; p+=1; start=y*stride; scan[p:p+stride]=rgba[start:start+stride]; p+=stride
    out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,6,0,0,0))
    for k,v in meta.items(): out+=itxt(k,v)
    out+=chunk(b'IDAT',zlib.compress(bytes(scan),9))+chunk(b'IEND',b'')
    with open(path,'wb') as f:f.write(out)
def main(path):
    packed=base64.b64encode(zlib.compress(TOOL.encode(),9)).decode()
    state={'identity':{'spore_name':'PIRATE-SPORE','birth_marker':None,'task':TASK,'author':'Jody','version':'1.0.0',
           'format_version':2,'created_at':TS,'updated_at':TS},
      'tools':{'reader':'decode VCW top-half as framed Grimoire v0.9 QUOTE statements',
               'integrity':'G=0x7f PARITY plus SHA-256 over all raw RGBA payload lanes and frame boundaries',
               'vcw_model':'append-only delta log','transport':WARN},
      'embedded_tools':{'language':'python','filename':'spore_min.py','encoding':'base64+zlib','entrypoints':['read','append'],
                        'sha256':hashlib.sha256(TOOL.encode()).hexdigest(),'code':packed},
      'conversation':[{'id':0,'ts':TS,'opcode':'SYSTEM','author':'APP','source':'conversation','content':PROMPT,
                       'checksum':s16(PROMPT.encode())}],
      'display':{'lines':['PROMPT ABOARD: pirate persona active until explicitly stopped.'],'status':'ACTIVE'}}
    payload=json.dumps(state,separators=(',',':'),sort_keys=True).encode(); pf=frames(payload)
    header={'magic':'SPOREPNG','format_version':2,'canvas':'2000x2000','vcw_region':[0,0,2000,1000],
      'display_region':[0,1000,2000,1000],'boot_strip_region':[0,1000,2000,300],
      'encoding':'grimoire-v0.9-quoted-bytes','payload_format':'stripped_appai_log','payload_length':len(payload),
      'payload_checksum':s16(payload),'frame_payload_bytes':1024,'payload_frame_count':len(pf),
      'payload_fingerprint':fingerprint(pf),'entry_count':1,'created_at':TS,'updated_at':TS,
      'spore_name':'PIRATE-SPORE','birth_marker':None,'task':TASK}
    hb=json.dumps(header,separators=(',',':'),sort_keys=True).encode(); stream=quote(hb)+b''.join(pf)
    assert len(stream)%4==0 and len(stream)//4<=BLOCKS
    rgba=bytearray(W*H*4); rgba[:len(stream)]=stream
    dark=bytes((20,24,34,255))*W; light=bytes((248,248,250,255))*W
    for y in range(1000,1300): rgba[y*W*4:(y+1)*W*4]=dark
    for y in range(1300,2000): rgba[y*W*4:(y+1)*W*4]=light
    meta={'Spore-Format':'spore-png-v2','Spore-Name':'PIRATE-SPORE','Spore-Version':'1.0.0','Author':'Jody',
      'Created-At':TS,'Updated-At':TS,'Canvas':'2000x2000','VCW-Region':'x=0,y=0,w=2000,h=1000',
      'Display-Region':'x=0,y=1000,w=2000,h=1000','Boot-Strip-Region':'x=0,y=1000,w=2000,h=300',
      'Encoding':'Grimoire v0.9 RGBA statements (A=force, G=0x7f parity)',
      'Payload-Format':'stripped Mantle/AppAI conversation log (JSON)','Payload-Checksum':header['payload_checksum'],
      'Full-Lane-Fingerprint':header['payload_fingerprint'],'Payload-Length':str(len(payload)),'Entry-Count':'1',
      'Birth-Marker':'unborn','Task':TASK,'Embedded-Tool':'spore_min.py (base64+zlib) in payload.embedded_tools',
      'Authority':'identity+conversation: VCW payload; bootloader/spec: metadata over strip','Transport-Warning':WARN,
      'Quickstart':QUICK,'Bootloader':BOOT}
    write_png(path,rgba,meta); print(path,os.path.getsize(path),hashlib.sha256(open(path,'rb').read()).hexdigest())
if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else 'pirate_spore.png')
