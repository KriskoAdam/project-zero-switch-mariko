"""Bounded exhaustive exploration; no state canonicalization/pruning."""
from collections import deque
from models.lifecycle import Op
from .differential_engine import run_pair

def enumerate_sequences(max_depth=5):
    alphabet=[Op('open'),Op('use',0),Op('close',0)]
    q=deque([()]); seen=set()
    while q:
        seq=q.popleft()
        if seq in seen: continue
        seen.add(seq); yield seq
        if len(seq)<max_depth:
            for op in alphabet: q.append(seq+(op,))

def explore(max_depth=5,inject_bug=True,stop_at_first=True):
    checked=0; findings=[]
    for seq in enumerate_sequences(max_depth):
        checked+=1; result=run_pair(seq,inject_bug)
        if result['diverged']:
            findings.append({'sequence':seq,'result':result})
            if stop_at_first: return {'checked':checked,'sequence':seq,'result':result,'findings':findings,'complete':False,'stop_reason':'first_difference'}
    return {'checked':checked,'sequence':findings[0]['sequence'] if findings else None,'result':findings[0]['result'] if findings else None,'findings':findings,'complete':True,'stop_reason':'bound_exhausted'}
