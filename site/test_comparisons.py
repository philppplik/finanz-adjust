import unittest,json,datetime,tempfile
from pathlib import Path
from comparisons import build_comparisons,stale_banner,DATA
from comparisons_data import load_series,parse_csv,SERIES
class ComparisonTests(unittest.TestCase):
 def test_stats(self):
  s=load_series();self.assertEqual(len(s),3)
  for x in s:
   self.assertGreaterEqual(len(x['rows']),2);self.assertEqual(x['rows'][-1]['UNIT'],'PCPA')
 def test_bad_units(self):
  key=SERIES[0][2];text=(DATA/(key+'.csv')).read_text();self.assertRaises(ValueError,parse_csv,text.replace('PCPA','EUR'),key)
 def test_license_and_provenance(self):
  x=json.loads((DATA/'conditions-2026-10-19.json').read_text());self.assertEqual(x['lizenz'],'CC BY 4.0')
  for b in x['broker']:self.assertTrue(b['konditionenQuelle']['url'].startswith('https://'));self.assertIn('geprueftAm',b['konditionenQuelle'])
 def test_age(self):
  self.assertEqual(stale_banner('2026-10-19',datetime.date(2026,10,19)),'');self.assertIn('Historischer',stale_banner('2026-10-19',datetime.date(2027,1,1)))
 def test_pages(self):
  with tempfile.TemporaryDirectory() as d:
   pages={};urls=[]
   def page(path,title,desc,body,*args,**kwargs):pages[path]=body;return 'https://finanz-adjust.de'+path
   build_comparisons(page,urls,d,'https://finanz-adjust.de');self.assertEqual(len(urls),4)
   for path,body in pages.items():
    self.assertIn('EZB-Statistiken' if 'zinsmonitor' in path else 'CC BY 4.0',body)
    if 'zinsmonitor' not in path:self.assertIn('keine Affiliate',body)
   self.assertIn('Preisquelle laut Datensatz',pages['/vergleiche/depot/']);self.assertIn('APRC',pages['/vergleiche/zinsmonitor/'])
 def test_scripts_local(self):
  for name in ['comparisons.js','comparison-math.js']:
   text=(Path(__file__).parent/name).read_text()
   for x in ['fetch(','localStorage','sessionStorage','document.cookie','eval(']:self.assertNotIn(x,text)
if __name__=='__main__':unittest.main()
