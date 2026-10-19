"""Public ECB CSV only. Preserve raw metadata and dates; never fabricate missing data."""
from pathlib import Path
import csv,io,datetime,urllib.request,math
ROOT=Path(__file__).resolve().parent.parent/'content/comparisons'
SERIES=[('overnight','Täglich fällige Einlagen','M.DE.B.L21.A.R.A.2250.EUR.N'),('fixed','Einlagen mit Laufzeit bis 1 Jahr','M.DE.B.L22.F.R.A.2250.EUR.N'),('credit','Konsumkredite: effektiver Jahreszins','M.DE.B.A2B.A.C.A.2250.EUR.N')]
def parse_csv(text,key):
    rows=list(csv.DictReader(io.StringIO(text)))
    valid=[]
    for r in rows:
        if r.get('KEY')!='MIR.'+key or r.get('UNIT')!='PCPA' or r.get('UNIT_MULT')!='0':raise ValueError('Wrong series or unit')
        if not r.get('OBS_VALUE') or r.get('OBS_STATUS') in ('M','L'):continue
        value=float(r['OBS_VALUE'])
        if not math.isfinite(value) or not -20<=value<=100:raise ValueError('Invalid rate')
        datetime.datetime.strptime(r['TIME_PERIOD'],'%Y-%m')
        valid.append(r)
    if len(valid)<2:raise ValueError('Insufficient observations')
    return sorted(valid,key=lambda r:r['TIME_PERIOD'])
def load_series(refresh=False):
    result=[]
    for slug,label,key in SERIES:
        path=ROOT/(key+'.csv');url='https://data-api.ecb.europa.eu/service/data/MIR/'+key+'?format=csvdata&lastNObservations=13'
        if refresh:
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'FA statistics importer; public ECB data'})
                with urllib.request.urlopen(req,timeout=8) as response:text=response.read(1000000).decode('utf-8-sig')
                parse_csv(text,key);path.write_text(text)
            except Exception as ex:print('ECB update unavailable, keeping dated snapshot:',slug,type(ex).__name__)
        try:rows=parse_csv(path.read_text(),key)
        except (OSError,ValueError):continue
        result.append(dict(slug=slug,label=label,key=key,rows=rows,download=url))
    return result
if __name__=='__main__':
    for s in load_series(refresh=True):print(s['slug'],s['rows'][-1]['TIME_PERIOD'],s['rows'][-1]['OBS_VALUE'])
