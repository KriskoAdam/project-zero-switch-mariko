"""Toy resource-handle lifecycle models. Entirely synthetic; not a Horizon model."""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Op:
    kind: str
    handle: int | None = None

@dataclass
class State:
    next_handle: int = 0
    live: set[int] = field(default_factory=set)
    history: list[dict] = field(default_factory=list)
    def snapshot(self):
        return {'next_handle': self.next_handle, 'live': sorted(self.live)}

class Reference:
    """Independent spec interpreter: handles are monotonically unique."""
    def __init__(self): self.state = State()
    def step(self, op):
        s=self.state; out={'op':op.kind,'handle':op.handle,'accepted':False}
        if op.kind=='open':
            h=s.next_handle; s.next_handle+=1; s.live.add(h); out.update(handle=h,accepted=True)
        elif op.kind=='close' and op.handle in s.live:
            s.live.remove(op.handle); out['accepted']=True
        elif op.kind=='use': out['accepted']=op.handle in s.live
        else: out['error']='invalid_or_stale'
        s.history.append(out); return out

class Candidate:
    """Synthetic candidate with a deliberate slot-reuse defect for detector validation."""
    def __init__(self, inject_bug=True): self.next_slot=0; self.live={}; self.free=[]; self.history=[]; self.inject_bug=inject_bug
    def step(self, op):
        out={'op':op.kind,'handle':op.handle,'accepted':False}
        if op.kind=='open':
            h=(self.free.pop(0) if self.free else self.next_slot) if self.inject_bug else self.next_slot
            if h==self.next_slot: self.next_slot+=1
            self.live[h]=True; out.update(handle=h,accepted=True)
        elif op.kind=='close' and self.live.get(op.handle,False):
            self.live[op.handle]=False
            if self.inject_bug: self.free.append(op.handle)
            out['accepted']=True
        elif op.kind=='use': out['accepted']=bool(self.live.get(op.handle,False))
        else: out['error']='invalid_or_stale'
        self.history.append(out); return out
    def snapshot(self): return {'live':sorted(h for h,v in self.live.items() if v), 'free':list(self.free)}

def ops_from_json(rows): return [Op(x['kind'],x.get('handle')) for x in rows]
