"""Transparent heuristic ranking; scores prioritize falsifiability and safe local tests."""
from .hypothesis_generator import generate
def score(h):
    return 3*int(h.get('testable',False))+2*int(h.get('synthetic_safe',False))+int(h.get('cross_discipline',False))-int(h.get('needs_target_artifact',False))
def rank(items=None): return sorted(items or generate(),key=lambda h:(score(h),h['id']),reverse=True)
if __name__=='__main__':
    for h in rank(): print(f"{score(h):2} {h['id']} — {h['claim']}")
