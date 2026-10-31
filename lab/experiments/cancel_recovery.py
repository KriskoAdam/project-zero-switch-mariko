"""Exhaustive bounded cancellation experiment with independent oracle."""
import itertools,json,hashlib
from pathlib import Path
from models.cancellation import TxOp,CorrectTransaction,BuggyTransaction
ROOT=Path(__file__).resolve().parents[1]
def oracle(seq):
    # Independent representation: a set of pending tokens and committed token IDs.
    pending=set(); committed=set(); next_token=0; rows=[]
    for i,op in enumerate(seq):
        if op.kind=='prepare': pending.add(next_token); next_token+=1
        elif op.kind=='cancel' and pending: pending.clear()
        elif op.kind=='resume' and pending:
            committed.update(pending); pending.clear()
        rows.append({'pending_count':len(pending),'committed_count':len(committed)})
    return rows
def run_detailed(seq,bug=True):
    a,b=CorrectTransaction(),BuggyTransaction(bug); rows=[]
    for i,op in enumerate(seq):
        x,y=a.step(op),b.step(op)
        rows.append({'index':i,'op':op.kind,'reference':x,'candidate':y,'diverged':x!=y})
    return {'diverged':any(r['diverged'] for r in rows),'rows':rows,'reference':a,'candidate':b}
def run(seq,bug=True):
    d=run_detailed(seq,bug); return d['diverged'],d['reference'],d['candidate']
def minimize(seq):
    s=list(seq); changed=True
    while changed:
        changed=False
        for i in range(len(s)):
            if run(s[:i]+s[i+1:])[0]: s=s[:i]+s[i+1:];changed=True;break
    return s
def validate(seq):
    d=run_detailed(seq,True); control=run_detailed(seq,False); expected=oracle(seq)
    ref_matches=all(r['reference']['pending']==expected[i]['pending_count'] and r['reference']['committed']==(expected[i]['committed_count']>0) for i,r in enumerate(d['rows']))
    cand_indices=[r['index'] for r in d['rows'] if r['candidate']['pending']!=expected[r['index']]['pending_count'] or r['candidate']['committed']!=(expected[r['index']]['committed_count']>0)]
    ref_indices=[r['index'] for r in d['rows'] if r['reference']['pending']!=expected[r['index']]['pending_count'] or r['reference']['committed']!=(expected[r['index']]['committed_count']>0)]
    diff_indices=[r['index'] for r in d['rows'] if r['diverged']]
    bug_off_clean=not control['diverged'] and all(not r['diverged'] for r in control['rows'])
    return {'oracle_matches_reference':ref_matches,'reference_oracle_mismatch_indices':ref_indices,'candidate_oracle_mismatch_indices':cand_indices,'candidate_differs_same_step':bool(diff_indices) and all(i in cand_indices for i in diff_indices) and not ref_indices,'reported_diff_indices':diff_indices,'bug_off_clean':bug_off_clean,'negative_control_passes':bug_off_clean}
def main(max_depth=4):
    alphabet=[TxOp(x) for x in ('prepare','cancel','resume')]; checked=0; found=None
    for n in range(max_depth+1):
        for seq in itertools.product(alphabet,repeat=n):
            checked+=1
            if run(seq)[0]: found=seq;break
        if found is not None: break
    reduced=minimize(found or []); verdict=validate(reduced); promoted=all([verdict['oracle_matches_reference'],verdict['candidate_differs_same_step'],verdict['bug_off_clean']])
    model_hash=hashlib.sha256((ROOT/'models'/'cancellation.py').read_bytes()).hexdigest(); experiment_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result={'run_id':f'cancel-model-depth-{max_depth}','evidence_level':'E2_synthetic_second_implementation' if promoted else 'E1_synthetic_model','model':'synthetic_deferred_cancel_v1','seed':0,'max_depth':max_depth,'sequences_checked_through_first_difference':checked,'bounded_search_complete':False if found is not None else True,'model_sha256':model_hash,'experiment_sha256':experiment_hash,'input':[x.kind for x in found] if found else [],'anomaly':found is not None,'minimized':[x.kind for x in reduced],'oracle_validation':verdict,'replay_diverges':run(reduced)[0],'negative_control_passes':verdict['negative_control_passes'],'scope':'model contract only; does not describe Horizon or Mariko'}
    (ROOT/'results'/'cancel_recovery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
if __name__=='__main__':main()
