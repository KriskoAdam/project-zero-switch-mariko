"""Deterministic hypothesis catalog and evidence-derived follow-up prompts."""
import json
from pathlib import Path
CATALOG=Path(__file__).resolve().parents[1]/'hypotheses'/'catalog.json'
def generate(limit=None):
    items=json.loads(CATALOG.read_text())
    return items[:limit] if limit else items
def derive_from_result(result):
    if result.get('anomaly'):
        return [{'id':'followup-minimized-'+result['run_id'],'area':'model-falsification','claim':'Does the minimized trace still fail after eliminating each operation independently?','test':'Replay every one-operation deletion and each single-parameter mutation.','status':'generated_from_synthetic_result'}]
    return [{'id':'followup-bound-'+result['run_id'],'area':'coverage','claim':'Does increasing the state-space bound reveal a new transition class?','test':'Repeat with depth + 1 and a distinct deterministic seed.','status':'generated_from_synthetic_result'}]
if __name__=='__main__': print(json.dumps(generate(),indent=2))
