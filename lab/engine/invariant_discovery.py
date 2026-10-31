"""Check explicit lifecycle invariants over observed synthetic traces."""
def inspect_trace(trace):
    live=set(); ever=set(); findings=[]
    for i,e in enumerate(trace):
        k=e['op']; h=e.get('handle')
        if k=='open':
            if h in ever: findings.append({'index':i,'invariant':'handle_identity_never_reused','handle':h})
            live.add(h); ever.add(h)
        elif k=='close' and e.get('accepted'): live.discard(h)
        elif k=='use' and e.get('accepted') and h not in live:
            findings.append({'index':i,'invariant':'use_requires_live_handle','handle':h})
    return findings
def discover_properties(traces):
    checks={'all_handles_unique':True,'accepted_use_is_live':True,'accepted_close_targets_issued_handle':True}
    for t in traces:
        seen=set(); live=set()
        for e in t:
            h=e.get('handle')
            if e['op']=='open':
                if h in seen: checks['all_handles_unique']=False
                seen.add(h); live.add(h)
            elif e['op']=='close' and e.get('accepted'):
                if h not in seen: checks['accepted_close_targets_issued_handle']=False
                live.discard(h)
            elif e['op']=='use' and e.get('accepted') and h not in live: checks['accepted_use_is_live']=False
    return checks
