#!/usr/bin/env python3
"""Inventory ARM64 instructions from an ELF or Mach-O executable segment (read-only)."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import lief
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('binary',type=Path); p.add_argument('--max-instructions',type=int,default=10000); p.add_argument('--max-bytes',type=int,default=4*1024*1024); p.add_argument('-o','--output',type=Path); a=p.parse_args()
    if a.max_instructions<1 or a.max_bytes<4: p.error('limits must be positive and max-bytes at least 4')
    raw=a.binary.read_bytes(); obj=lief.parse(str(a.binary))
    if obj is None: p.error('unsupported or malformed binary')
    bins=list(obj) if isinstance(obj,lief.MachO.FatBinary) else [obj]
    candidates=[]
    for b in bins:
        arch=str(b.header.machine_type) if isinstance(b,lief.ELF.Binary) else str(b.header.cpu_type) if isinstance(b,lief.MachO.Binary) else ''
        if 'AARCH64' not in arch.upper() and 'ARM64' not in arch.upper(): continue
        if isinstance(b,lief.ELF.Binary):
            for s in b.segments:
                if s.type==lief.ELF.Segment.TYPE.LOAD and int(s.flags)&int(lief.ELF.Segment.FLAGS.X): candidates.append((int(s.virtual_address),bytes(s.content)))
        elif isinstance(b,lief.MachO.Binary):
            for s in b.sections:
                if s.size and (s.flags & lief.MachO.Section.FLAGS.PURE_INSTRUCTIONS or '__text' in s.name): candidates.append((int(s.virtual_address),bytes(s.content)))
    md=Cs(CS_ARCH_ARM64,CS_MODE_ARM); ins=[]; total=0
    for base,blob in candidates:
        blob=blob[:max(0,a.max_bytes-total)]
        for i in md.disasm(blob,base):
            ins.append({'address':hex(i.address),'mnemonic':i.mnemonic,'operands':i.op_str})
            total+=i.size
            if len(ins)>=a.max_instructions or total>=a.max_bytes: break
        if len(ins)>=a.max_instructions or total>=a.max_bytes: break
    import capstone
    out={'path':str(a.binary.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'capstone_version':'.'.join(map(str,capstone.cs_version())),'instruction_count':len(ins),'decoded_bytes':total,'limits':{'max_instructions':a.max_instructions,'max_bytes':a.max_bytes},'instructions':ins,'note':'Static disassembly only; undecoded gaps/data and unvisited segments are not evidence of absence.'}
    data=json.dumps(out,indent=2)+'\n'
    if a.output:a.output.write_text(data)
    else:print(data,end='')
if __name__=='__main__':main()
