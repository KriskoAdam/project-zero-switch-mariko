"""SQLite run ledger for reproducible synthetic observations."""
import json,sqlite3
from pathlib import Path
DB=Path(__file__).resolve().parents[1]/'results'/'discoveries.sqlite3'
def record(run,validation):
    db=sqlite3.connect(DB); db.execute('CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, evidence_level TEXT, model TEXT, seed INTEGER, model_sha256 TEXT, anomaly INTEGER, payload TEXT, validation TEXT)')
    db.execute('INSERT OR REPLACE INTO runs VALUES(?,?,?,?,?,?,?,?)',(run['run_id'],run['evidence_level'],run['model'],run['seed'],run['model_sha256'],int(run['anomaly']),json.dumps(run),json.dumps(validation))); db.commit(); db.close()
