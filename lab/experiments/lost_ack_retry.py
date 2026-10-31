"""Bounded synthetic test of retrying an idempotent request after lost ACK."""
import itertools,json,hashlib
from pathlib import Path
from models.retry import RetryOp,run,oracle
ROOT=Path(__file__).resolve().parents[1]
def minimize(ops):
    s=list(ops); changed=True
    while changed:
        changed=False
        for i in range(len(s)):
            if run(s[:i]+s[i+1:])['diverged']: s=s[:i]+s[i+1:];changed=True;break
    return s
def main(max_depth=4):
    alphabet=[RetryOp(k) for k in ('send','lose_ack','retry')]; checked=0; hits=[]
    for n in range(max_depth+1):
        for seq in itertools.product(alphabet,repeat=n):
            checked+=1; d=run(seq)
            if d['diverged']: hits.append((seq,d))
    selected=next((s for s,d in hits if len(s)<=max_depth),None); reduced=minimize(selected or [])
    replay=run(reduced); control=run(reduced,False); expected=oracle(reduced)
    ref_ok=all(x['reference']==expected[i] for i,x in enumerate(replay['rows']))
    cand_bad=[i for i,x in enumerate(replay['rows']) if x['candidate']!=expected[i]]
    diff=[i for i,x in enumerate(replay['rows']) if x['diverged']]
    bug_off=not control['diverged']
    promote=bool(selected) and ref_ok and bug_off and bool(diff) and all(i in cand_bad for i in diff)
    root_hash=hashlib.sha256((ROOT/'models'/'retry.py').read_bytes()).hexdigest(); exp_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result={'run_id':f'lost-ack-retry-depth-{max_depth}','model':'synthetic_idempotent_retry_v1','seed':0,'max_depth':max_depth,'sequences_checked':checked,'search_complete':True,'anomalous_sequences':len(hits),'source_sha256':exp_hash,'model_sha256':root_hash,'input':[x.kind for x in selected] if selected else [],'minimized':[x.kind for x in reduced],'reference_matches_oracle':ref_ok,'candidate_differs_same_step':bool(diff) and all(i in cand_bad for i in diff),'bug_off_clean':bug_off,'evidence_level':'E2_synthetic_second_implementation' if promote else 'E1_synthetic_model','scope':'synthetic contract only; intentionally faulty candidate; no Horizon/Switch/Mariko evidence'}
    (ROOT/'results'/'lost_ack_retry.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()
