"""Offline malformed-value tests. No network calls or data writes."""
import copy,json
from pathlib import Path
from collect_demand import validate, mark_stale, stale_token_index
ROOT=Path(__file__).resolve().parent
p=max(json.loads((ROOT/'snapshots.json').read_text())['snapshots'].values(),key=lambda s:s['capturedAt'])
o,r=p['openrouter'],p['ramp']
validate(o,r,o,r)
for kind in ['duplicate-model','missing-model','negative-tokens','shares-total','nan-spend','future-date','regressed-period','missing-maker','adoption-range']:
    a,b=copy.deepcopy(o),copy.deepcopy(r)
    if kind=='duplicate-model':a['weekTopModels'][1]['model']=a['weekTopModels'][0]['model']
    elif kind=='missing-model':a['weekTopModels'].pop()
    elif kind=='negative-tokens':a['weekTopModels'][0]['tokensT']=-1
    elif kind=='shares-total':a['marketShare'][0]['share']=0
    elif kind=='nan-spend':b['spendPerEmployee']=float('nan')
    elif kind=='future-date':a['usageThrough']='2099-01-01'
    elif kind=='regressed-period':b['period']='2020-01'
    elif kind=='missing-maker':b['tokenSpend']['makers']=[x for x in b['tokenSpend']['makers'] if x['maker']!='OpenAI']
    elif kind=='adoption-range':b['adoption']['overall']=150
    try:validate(a,b,o,r)
    except ValueError:print(kind,'rejected')
    else:raise AssertionError('Accepted bad data: '+kind)
before=copy.deepcopy(r)
s=mark_stale(r,'2026-10-22T08:30:00+11:00','collection failed: simulated outage')
assert s['stale'] is True and s['staleSince']==r['capturedAt'] and s['checkedAt']=='2026-10-22T08:30:00+11:00' and r==before
print('Stale fallback marking passed')
# Ramp weekly maker index unavailable: first stale run anchors provenance to the last fresh capture.
a1={'capturedAt':'2026-10-31T08:53:28+11:00','tokenSpend':{'periodEnd':'2026-10-23','unit':'Index, not USD or tokens','makers':[{'maker':'OpenAI','index':100.0,'previousIndex':99.0}]}}
s1=stale_token_index(a1,'2026-11-01T09:26:27+11:00','simulated outage')
assert s1['stale'] is True and s1['sourceCapturedAt']=='2026-10-31T08:53:28+11:00' and s1['staleSince']=='2026-10-31T08:53:28+11:00' and s1['checkedAt']=='2026-11-01T09:26:27+11:00'
assert s1['makers']==a1['tokenSpend']['makers'] and s1['periodEnd']=='2026-10-23'
# Consecutive stale runs: provenance must not roll forward; only checkedAt advances.
s2=stale_token_index({'capturedAt':'2026-11-01T09:26:27+11:00','tokenSpend':s1},'2026-11-02T08:29:10+11:00','simulated outage')
assert s2['sourceCapturedAt']=='2026-10-31T08:53:28+11:00' and s2['staleSince']=='2026-10-31T08:53:28+11:00' and s2['checkedAt']=='2026-11-02T08:29:10+11:00'
s3=stale_token_index({'capturedAt':'2026-11-02T08:29:10+11:00','tokenSpend':s2},'2026-11-03T08:32:59+11:00','simulated outage')
assert s3['sourceCapturedAt']=='2026-10-31T08:53:28+11:00' and s3['staleSince']=='2026-10-31T08:53:28+11:00' and s3['checkedAt']=='2026-11-03T08:32:59+11:00'
assert s1['makers']==s2['makers']==s3['makers']
print('Consecutive stale runs preserve index provenance')
print('All demand safety tests passed')
