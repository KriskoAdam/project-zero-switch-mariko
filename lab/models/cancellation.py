"""Synthetic deferred-operation cancellation contract, unrelated to any real OS."""
from dataclasses import dataclass
@dataclass(frozen=True)
class TxOp:
    kind:str
class CorrectTransaction:
    def __init__(self): self.pending=False; self.committed=False; self.events=[]
    def step(self,op):
        if op.kind=='prepare': self.pending=True
        elif op.kind=='cancel': self.pending=False
        elif op.kind=='resume' and self.pending: self.pending=False; self.committed=True
        row={'op':op.kind,'pending':self.pending,'committed':self.committed}; self.events.append(row); return row
class BuggyTransaction:
    def __init__(self,inject_bug=True): self.pending=False; self.committed=False; self.events=[]; self.inject_bug=inject_bug
    def step(self,op):
        if op.kind=='prepare': self.pending=True
        elif op.kind=='cancel':
            if not self.inject_bug: self.pending=False
        elif op.kind=='resume' and self.pending: self.pending=False; self.committed=True
        row={'op':op.kind,'pending':self.pending,'committed':self.committed}; self.events.append(row); return row
