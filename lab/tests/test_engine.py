import sys,unittest,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from engine.state_space_explorer import explore
from engine.differential_engine import run_pair
from engine.experiment_runner import minimize
from engine.result_validator import validate
from engine.invariant_discovery import discover_properties
from engine.hypothesis_generator import generate
from models.lifecycle import Op
from models.retry import RetryOp,run as retry_run,oracle as retry_oracle
from experiments.lost_ack_retry import main as retry_main
from models.cancellation import TxOp
from experiments.cancel_recovery import run as cancel_run, minimize as cancel_minimize

class DiscoveryEngineTests(unittest.TestCase):
 def test_invariant_checker_falsifies_invalid_close_contract(self):
  trace=[[{'op':'close','handle':7,'accepted':True}]]
  self.assertFalse(discover_properties(trace)['accepted_close_targets_issued_handle'])
 def test_catalog_has_forty_distinct_hypotheses(self):
  rows=generate(); self.assertGreaterEqual(len(rows),40); self.assertEqual(len({x['id'] for x in rows}),len(rows))
 def test_exhaustive_depth_three_checks_all_distinct_sequences(self):
  first=explore(3,stop_at_first=True); full=explore(3,stop_at_first=False)
  self.assertEqual(first['checked'],20); self.assertEqual(full['checked'],40); self.assertTrue(full['complete'])
  self.assertEqual(full['checked']-first['checked'],20); self.assertGreaterEqual(len(full['findings']),1)
 def test_explorer_finds_planted_model_defect(self):
  r=explore(max_depth=4); self.assertTrue(r['result']['diverged']); self.assertLessEqual(len(r['sequence']),3)
 def test_clean_candidate_is_differentially_equivalent_bounded(self):
  from engine.state_space_explorer import enumerate_sequences
  for seq in enumerate_sequences(4): self.assertFalse(run_pair(seq,False)['diverged'],seq)
 def test_minimizer_returns_deletion_minimal_counterexample(self):
  seq=[Op('open'),Op('close',0),Op('open'),Op('use',0),Op('use',9)]
  detail=minimize(seq,with_details=True); m=detail['sequence']; self.assertTrue(run_pair(m)['diverged']); self.assertEqual(len(m),3)
  probe=[Op('open'),Op('close',0),Op('open'),Op('use',99)]
  reduced=minimize(probe,with_details=True); self.assertEqual(reduced['sequence'],probe[:3]); self.assertIn({'index':3,'from':99,'to':0,'kind':'use'},reduced['argument_reductions']); self.assertTrue(reduced['deletion_minimal'])
  for i in range(len(m)): self.assertFalse(run_pair(m[:i]+m[i+1:])['diverged'])
 def test_validator_replays_and_bug_off_control_passes(self):
  r=explore(4); record={'minimized_sequence':[{'kind':o.kind,'handle':o.handle} for o in minimize(r['sequence'])]}
  v=validate(record); self.assertTrue(v['clean_replay_diverges']); self.assertFalse(v['bug_disabled_control_diverges']); self.assertTrue(v['reference_matches_oracle']); self.assertTrue(v['same_step_divergence_confirmed']); self.assertTrue(v['one_minimal'])
 def test_seeded_property_sequences_match_when_bug_disabled(self):
  for seed in range(200):
   r=random.Random(seed); ops=[]
   for _ in range(20):
    k=r.choice(['open','close','use']); ops.append(Op(k,None if k=='open' else r.randrange(0,7)))
   self.assertFalse(run_pair(ops,False)['diverged'],f'seed={seed}')
 def test_cancellation_model_finds_and_minimizes_distinct_anomaly(self):
  import itertools
  alphabet=[TxOp(k) for k in ('prepare','cancel','resume')]
  found=None
  for n in range(4):
   for seq in itertools.product(alphabet,repeat=n):
    if cancel_run(seq)[0]: found=seq; break
   if found is not None: break
  self.assertEqual([x.kind for x in cancel_minimize(found)],['prepare','cancel'])
  self.assertFalse(cancel_run(cancel_minimize(found),False)[0])
  from experiments.cancel_recovery import validate as cancel_validate
  cv=cancel_validate(cancel_minimize(found)); self.assertTrue(cv['oracle_matches_reference']); self.assertTrue(cv['candidate_differs_same_step']); self.assertTrue(cv['bug_off_clean'])
 def test_lost_ack_retry_experiment_has_oracle_and_negative_control(self):
  r=retry_main(4); self.assertEqual(r['minimized'],['send','lose_ack','retry']); self.assertTrue(r['reference_matches_oracle']); self.assertTrue(r['candidate_differs_same_step']); self.assertTrue(r['bug_off_clean']); self.assertTrue(r['search_complete'])
 def test_close_order_commutes_for_distinct_resources(self):
  a=[Op('open'),Op('open'),Op('close',0),Op('close',1)]
  b=[Op('open'),Op('open'),Op('close',1),Op('close',0)]
  ra,rb=run_pair(a,False),run_pair(b,False)
  self.assertEqual(ra['reference_state']['live'],rb['reference_state']['live'])
  self.assertFalse(ra['diverged']); self.assertFalse(rb['diverged'])

if __name__=='__main__': unittest.main()
