"""Replay against a separately coded small oracle and bug-disabled control."""
from .differential_engine import run_pair
from models.lifecycle import ops_from_json

def oracle(ops):
    # Different state representation: token table and monotonically allocated serial.
    serial=0; tokens={}; events=[]
    for op in ops:
        if op.kind=='open': tokens[serial]=True; events.append({'accepted':True,'handle':serial}); serial+=1
        elif op.kind=='close' and tokens.get(op.handle,False): tokens[op.handle]=False; events.append({'accepted':True})
        elif op.kind=='use': events.append({'accepted':bool(tokens.get(op.handle,False))})
        else: events.append({'accepted':False,'error':'invalid_or_stale'})
    return events

def validate(record):
    seq=ops_from_json(record['minimized_sequence']); replay=run_pair(seq,True); control=run_pair(seq,False); expected=oracle(seq)
    ref_events=[x['reference'] for x in replay['rows']]; cand_events=[x['candidate'] for x in replay['rows']]
    def matches(actual,want,op):
        keys=['accepted','error']+(['handle'] if op.kind=='open' else [])
        return all(actual.get(k)==want.get(k) for k in keys)
    reference_mismatch=[i for i,(o,a) in enumerate(zip(seq,ref_events)) if not matches(a,expected[i],o)]
    candidate_mismatch=[i for i,(o,a) in enumerate(zip(seq,cand_events)) if not matches(a,expected[i],o)]
    divergence_indices=[i for i,row in enumerate(replay['rows']) if row['diverged']]
    deletions=[run_pair(seq[:i]+seq[i+1:])['diverged'] for i in range(len(seq))]
    return {'evidence_level':'E2_synthetic_second_implementation','clean_replay_diverges':replay['diverged'],'bug_disabled_control_diverges':control['diverged'],'reference_matches_oracle':not reference_mismatch,'reference_oracle_mismatch_indices':reference_mismatch,'candidate_oracle_mismatch_indices':candidate_mismatch,'same_step_divergence_confirmed':bool(divergence_indices) and all(i in candidate_mismatch for i in divergence_indices) and not reference_mismatch,'reported_divergence_indices':divergence_indices,'one_minimal':bool(seq) and not any(deletions),'deletion_results':deletions,'counterexample':record['minimized_sequence'],'scope':'second synthetic implementation; no Horizon/Mariko inference'}
