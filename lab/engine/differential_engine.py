"""Compare externally visible events and normalized semantic states of two toy models."""
from models.lifecycle import Reference,Candidate

def run_pair(ops,inject_bug=True):
    ref,cand=Reference(),Candidate(inject_bug=inject_bug); rows=[]
    for op in ops:
        a=ref.step(op); b=cand.step(op)
        ref_state={'next_handle':ref.state.next_handle,'live':sorted(ref.state.live)}
        cand_state={'next_handle':cand.next_slot,'live':sorted(h for h,v in cand.live.items() if v)}
        fields=['accepted','error']
        if op.kind=='open': fields.append('handle')
        event_diff=any(a.get(k)!=b.get(k) for k in fields)
        state_diff=ref_state!=cand_state
        rows.append({'operation':op.kind,'input_handle':op.handle,'reference':a,'candidate':b,'reference_state':ref_state,'candidate_state':cand_state,'event_diverged':event_diff,'state_diverged':state_diff,'diverged':event_diff or state_diff})
    return {'diverged':any(x['diverged'] for x in rows),'rows':rows,'reference_state':{'next_handle':ref.state.next_handle,'live':sorted(ref.state.live)},'candidate_state':cand.snapshot()}
