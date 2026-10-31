#!/usr/bin/env python3
"""Read-only SHA-256 and format metadata for ELF/Mach-O/PE using LIEF."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import lief

def inspect(path: Path) -> dict:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    obj=lief.parse(str(path))
    out={'path':str(path.resolve()),'size':path.stat().st_size,'sha256':h.hexdigest(),'lief_version':lief.__version__,'format':'unknown','architectures':[],'entrypoint':None,'sections':[],'symbols':[],'parse_note':None}
    if obj is None:
        out['parse_note']='LIEF did not recognize this file; hash and size only.'
        return out
    if isinstance(obj, lief.ELF.Binary):
        out['format']='ELF'; out['entrypoint']=int(obj.entrypoint)
        out['architectures']=[str(obj.header.machine_type)]
        out['sections']=[{'name':s.name,'size':int(s.size),'virtual_address':int(s.virtual_address),'type':str(s.type)} for s in obj.sections]
        out['symbols']=[{'name':s.name,'value':int(s.value),'type':str(s.type),'binding':str(s.binding)} for s in obj.symtab_symbols if s.name]
    elif isinstance(obj, lief.MachO.FatBinary):
        out['format']='Mach-O Universal'
        for b in obj:
            out['architectures'].append(str(b.header.cpu_type))
            out['sections'].extend({'architecture':str(b.header.cpu_type),'name':s.name,'size':int(s.size),'virtual_address':int(s.virtual_address)} for s in b.sections)
            out['symbols'].extend({'architecture':str(b.header.cpu_type),'name':s.name,'value':int(s.value)} for s in b.symbols if s.name)
    elif isinstance(obj, lief.MachO.Binary):
        out['format']='Mach-O'; out['architectures']=[str(obj.header.cpu_type)]; out['entrypoint']=int(obj.entrypoint)
        out['sections']=[{'name':s.name,'size':int(s.size),'virtual_address':int(s.virtual_address)} for s in obj.sections]
        out['symbols']=[{'name':s.name,'value':int(s.value)} for s in obj.symbols if s.name]
    elif isinstance(obj, lief.PE.Binary):
        out['format']='PE'; out['architectures']=[str(obj.header.machine)]; out['entrypoint']=int(obj.optional_header.addressof_entrypoint)
        out['sections']=[{'name':s.name,'size':int(s.size),'virtual_address':int(s.virtual_address)} for s in obj.sections]
        out['symbols']=[{'name':s.name} for s in obj.exported_functions if s]
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('binary',type=Path); p.add_argument('-o','--output',type=Path); a=p.parse_args()
    if not a.binary.is_file(): p.error(f'not a file: {a.binary}')
    result=inspect(a.binary); data=json.dumps(result,indent=2)+'\n'
    if a.output: a.output.write_text(data)
    else: print(data,end='')
if __name__=='__main__': main()
