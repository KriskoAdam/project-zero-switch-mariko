"""Synthetic idempotent-request model with a lost acknowledgement."""
from dataclasses import dataclass
@dataclass(frozen=True)
class RetryOp:
    kind:str
class IdempotentReference:
    def __init__(self): self.keys=set(); self.count=0; self.awaiting=False; self.sent=False; self.events=[]
    def apply(self,kind):
        if kind=='send' and not self.sent:
            self.sent=True; self._commit_once(); self.awaiting=False
        elif kind=='lose_ack' and self.sent: self.awaiting=True
        elif kind=='retry' and self.awaiting: self._commit_once(); self.awaiting=False
        row={'op':kind,'count':self.count,'awaiting':self.awaiting}; self.events.append(row); return row
    def _commit_once(self):
        if 'request-1' not in self.keys: self.keys.add('request-1'); self.count+=1
class CandidateRetry:
    def __init__(self,inject_bug=True): self.keys=set(); self.count=0; self.awaiting=False; self.sent=False; self.events=[]; self.inject_bug=inject_bug
    def apply(self,kind):
        if kind=='send' and not self.sent:
            self.sent=True; self._commit(); self.awaiting=False
        elif kind=='lose_ack' and self.sent: self.awaiting=True
        elif kind=='retry' and self.awaiting: self._commit(); self.awaiting=False
        row={'op':kind,'count':self.count,'awaiting':self.awaiting}; self.events.append(row); return row
    def _commit(self):
        if self.inject_bug or 'request-1' not in self.keys: self.count+=1
        self.keys.add('request-1')

def run(ops,inject_bug=True):
    ref,cand=IdempotentReference(),CandidateRetry(inject_bug); rows=[]
    for i,op in enumerate(ops):
        a,b=ref.apply(op.kind),cand.apply(op.kind)
        rows.append({'index':i,'reference':a,'candidate':b,'diverged':a!=b})
    return {'rows':rows,'diverged':any(x['diverged'] for x in rows)}

def oracle(ops):
    # Independent ledger representation and transition code.
    committed={}; ack_waiting=False; first_send_seen=False; units=0; out=[]
    for op in ops:
        if op.kind=='send' and not first_send_seen:
            first_send_seen=True
            if not committed.get('request-1'): committed['request-1']=True; units=1
            ack_waiting=False
        elif op.kind=='lose_ack' and first_send_seen: ack_waiting=True
        elif op.kind=='retry' and ack_waiting:
            if not committed.get('request-1'): committed['request-1']=True; units=1
            ack_waiting=False
        out.append({'op':op.kind,'count':units,'awaiting':ack_waiting})
    return out
