import unittest,tempfile,json
from pathlib import Path
from calculators import TOOLS,build_calculators
class CalculatorsTests(unittest.TestCase):
 def test_static_pages(self):
  with tempfile.TemporaryDirectory() as d:
   pages={};urls=[]
   def page(path,title,desc,body,*a,**kw):pages[path]=body;return 'https://finanz-adjust.de'+path
   build_calculators(page,urls,d,'https://finanz-adjust.de')
   self.assertEqual(len(pages),9);self.assertEqual(len(urls),9)
   for tool in TOOLS:
    html=pages['/rechner/'+tool['slug']+'/']
    self.assertIn('So rechnet',html);self.assertIn('Häufige Fragen',html)
    self.assertIn('id="calc-controls" disabled',html);self.assertIn('Keine Anlage-',html);self.assertIn(tool['formula'],html.replace('&gt;','>'))
    for field in tool['fields']:self.assertIn('name="'+field[0]+'"',html)
 def test_glossary_links_resolve(self):
  slugs={x['slug'] for x in json.loads((Path(__file__).resolve().parent.parent/'content/glossary.json').read_text())['entries']}
  for t in TOOLS:
   for g in t['gloss']:self.assertIn(g,slugs)
 def test_no_storage_or_network_in_scripts(self):
  for name in ['calculators.js','calculator-math.js']:
   text=(Path(__file__).parent/name).read_text()
   for bad in ['fetch(','localStorage','sessionStorage','document.cookie','XMLHttpRequest','eval(']:self.assertNotIn(bad,text)
if __name__=='__main__':unittest.main()
