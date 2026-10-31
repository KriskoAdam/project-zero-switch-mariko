"""Seeded synthetic experiments with machine-readable run records."""
import hashlib,json,random,sys,time
from pathlib import Path
from models.lifecycle import Op
from .differential_engine import run_pair
from .invariant_discovery import inspect_trace
from .state_space_explorer import explore
ROOT=Path(__file__).resolve().parents[1]
def sequence(seed,n=30):
    r=random.Random(seed); kinds=['open','close','use']; live=[]; ops=[]
    for _ in range(n):
        k=r.choice(kinds)
        if k=='open': ops.append(Op(k)); live.append(None)
        else: ops.append(Op(k,r.randrange(0,4)))
    return ops
def encode(seq): return [{'kind':o.kind,'handle':o.handle} for o in seq]
def minimize(seq,with_details=False):
    """Shrink numeric handle arguments toward zero, then delete steps to 1-minimality."""
    current=list(seq); arg_reductions=[]; changes=True
    while changes:
        changes=False
        for i,op in enumerate(current):
            if op.handle is None or not isinstance(op.handle,int) or op.handle<=0: continue
            for value in sorted({0,op.handle//2}):
                if value>=op.handle: continue
                trial=current.copy(); trial[i]=Op(op.kind,value)
                if run_pair(trial)['diverged']:
                    arg_reductions.append({'index':i,'from':op.handle,'to':value,'kind':op.kind})
                    current=trial; changes=True; break
            if changes: break
        if changes: continue
        for i in range(len(current)):
            trial=current[:i]+current[i+1:]
            if run_pair(trial)['diverged']:
                current=trial; changes=True; break
    details={'sequence':current,'argument_reductions':arg_reductions,'deletion_minimal':bool(current) and not any(run_pair(current[:i]+current[i+1:])['diverged'] for i in range(len(current)))}
    return details if with_details else current
def source_hash():
    names=['models/lifecycle.py','engine/differential_engine.py','engine/state_space_explorer.py','engine/invariant_discovery.py','engine/experiment_runner.py','engine/result_validator.py']
    h=hashlib.sha256()
    for name in names: h.update(name.encode()+b'\0'+(ROOT/name).read_bytes())
    return h.hexdigest()
def main(seed=20261030,depth=5):
    exhaustive=explore(depth); chosen=exhaustive['sequence']
    if chosen is None: chosen=[]  # bounded negative-control result; random traces are a separate campaign
    diff=run_pair(chosen); trace=[r['candidate'] for r in diff['rows']]
    reduction_input=list(chosen)+[Op('use',99)] if diff['diverged'] else list(chosen)
    shrink=minimize(reduction_input,with_details=True) if diff['diverged'] else {'sequence':chosen,'argument_reductions':[],'deletion_minimal':False}
    reduced=shrink['sequence']; reduced_result=run_pair(reduced)
    record={'run_id':f'local-{seed}-{depth}','evidence_level':'E1_synthetic_model','model':'synthetic_handle_lifecycle_v1','seed':seed,'max_depth':depth,'bounded_sequences_checked':exhaustive['checked'],'bounded_search_complete':exhaustive['complete'],'model_sha256':hashlib.sha256((ROOT/'models/lifecycle.py').read_bytes()).hexdigest(),'engine_bundle_sha256':source_hash(),'anomaly':diff['diverged'],'sequence':encode(chosen),'reduction_input':encode(reduction_input),'argument_reductions':shrink['argument_reductions'],'deletion_minimal':shrink['deletion_minimal'],'minimized_sequence':encode(reduced),'minimized_reproduces':reduced_result['diverged'],'invariants':inspect_trace(trace),'differential':diff}
    out=ROOT/'results'/f"{record['run_id']}.json"; out.write_text(json.dumps(record,indent=2)+'\n'); print(json.dumps({k:v for k,v in record.items() if k not in ('differential',)},indent=2)); return record
if __name__=='__main__': main(int(sys.argv[1]) if len(sys.argv)>1 else 20261030,int(sys.argv[2]) if len(sys.argv)>2 else 5)
