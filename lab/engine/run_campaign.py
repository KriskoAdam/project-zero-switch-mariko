"""Run reproducible A-G synthetic campaign and append evidence records."""
import json,random,hashlib
from pathlib import Path
from .hypothesis_generator import generate,derive_from_result
from .hypothesis_ranker import rank
from .experiment_runner import main
from .result_validator import validate
from .discovery_database import record
from models.lifecycle import Op
from .differential_engine import run_pair
from .state_space_explorer import explore
from experiments.lost_ack_retry import main as run_retry_experiment
from experiments.cancel_recovery import main as run_cancel_experiment
ROOT=Path(__file__).resolve().parents[1]
def run():
    (ROOT/'results'/'execution.jsonl').write_text('')
    (ROOT/'results'/'ranked_hypotheses.json').write_text(json.dumps(rank(),indent=2)+'\n')
    runs=[]; validations=[]; cancellation=run_cancel_experiment(4)
    depth3_complete=explore(3,stop_at_first=False)
    depth3_first=explore(3,stop_at_first=True)
    retry=run_retry_experiment(4)
    for seed,depth in [(10,2),(20261030,3),(77,5)]:
        r=main(seed,depth); v=validate(r); record(r,v); runs.append(r); validations.append(v)
    generated=[]
    for r in runs: generated.extend(derive_from_result(r))
    (ROOT/'hypotheses'/'followups.json').write_text(json.dumps(generated,indent=2)+'\n')
    # Additional seeded property-based-style negative control: 200 independent traces, bug off.
    passed=0; mismatches=[]
    for seed in range(200):
        rng=random.Random(seed); ops=[]
        for _ in range(32):
            kind=rng.choice(('open','close','use')); ops.append(Op(kind,None if kind=='open' else rng.randrange(8)))
        result=run_pair(ops,False)
        if result['diverged']: mismatches.append(seed)
        else: passed+=1
    # Metamorphic check: two valid closes commute when applied to different live handles.
    a=[Op('open'),Op('open'),Op('close',0),Op('close',1)]
    b=[Op('open'),Op('open'),Op('close',1),Op('close',0)]
    metamorphic=(run_pair(a,False)['reference_state']['live']==run_pair(b,False)['reference_state']['live'])
    out={'campaign':'PROJECT_ZERO local synthetic model campaign','evidence_level':'E1_with_E2_oracle_replay','source_hash':runs[0]['engine_bundle_sha256'],'cancellation_experiment':cancellation,'retry_experiment':retry,'depth3_exhaustive':{'complete':depth3_complete['complete'],'distinct_sequences_checked':depth3_complete['checked'],'anomalous_sequences':len(depth3_complete['findings']),'first_find_previous_count':depth3_first['checked'],'additional_sequences_after_first_find':depth3_complete['checked']-depth3_first['checked']},'cycles':[{'run_id':r['run_id'],'seed':r['seed'],'depth':r['max_depth'],'source_sha256':r['engine_bundle_sha256'],'model_sha256':r['model_sha256'],'search_complete':r['bounded_search_complete'],'checked_before_stop':r['bounded_sequences_checked'],'anomaly':r['anomaly'],'minimized':r['minimized_sequence'],'validation':v} for r,v in zip(runs,validations)],'seeded_negative_control':{'sequences':200,'operations_each':32,'passed':passed,'mismatches':mismatches},'metamorphic_independent_close_commutativity':metamorphic,'next_experiment':'synthetic cancellation/rollback interleavings, selected because oracle-confirmed handle-reuse defect was isolated to allocation identity; explore a separate failure/cleanup invariant.'}
    (ROOT/'results'/'campaign_summary.json').write_text(json.dumps(out,indent=2)+'\n')
    with (ROOT/'results'/'execution.jsonl').open('a') as f: f.write(json.dumps(out)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__': run()
