#!/usr/bin/env python3
"""Compare two JSON SHA-256 manifests by relative path."""
import argparse,json
from pathlib import Path

def load(p):
 d=json.loads(p.read_text()); return {x['path']:x for x in d['files']}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('old',type=Path);p.add_argument('new',type=Path);p.add_argument('-o','--output',type=Path);a=p.parse_args()
 x,y=load(a.old),load(a.new); keys=sorted(x.keys()|y.keys()); rows=[]
 for k in keys:
  if k not in x: state='added'
  elif k not in y: state='removed'
  elif x[k].get('sha256')!=y[k].get('sha256'): state='changed'
  else: state='unchanged'
  if state!='unchanged': rows.append({'path':k,'status':state,'old_sha256':x.get(k,{}).get('sha256'),'new_sha256':y.get(k,{}).get('sha256')})
 out={'schema_version':1,'changes':rows};s=json.dumps(out,indent=2)+'\n'
 if a.output:a.output.write_text(s)
 else:print(s,end='')
if __name__=='__main__':main()
