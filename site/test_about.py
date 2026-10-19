import unittest,tempfile,json
from pathlib import Path
from about import build_about
class AboutTest(unittest.TestCase):
    def test_render_and_source_counts(self):
        captured=[]
        def page(path,title,desc,body,ld,**kwargs):
            captured.append((path,body,ld));return 'https://finanz-adjust.de'+path
        with tempfile.TemporaryDirectory() as d:
            urls=[];build_about(page,urls,[{},{}],[{}, {}, {}],d,'https://finanz-adjust.de')
            path,body,ld=captured[0]
            self.assertEqual(path,'/ueber-uns/')
            self.assertIn('<strong>3</strong><h3>Glossarbegriffe',body)
            self.assertIn('<strong>2</strong><h3>Redaktionelle Beiträge',body)
            self.assertIn('mailto:philipp.l.paulik@gmail.com',body)
            self.assertNotIn('tel:',body)
            self.assertIn('AboutPage',json.dumps(ld))
            self.assertTrue((Path(d)/'about.css').exists())
            for path in ['/rechner/','/vergleiche/','/glossar/','/heatmap/','/berichte/','/korrekturen/','/transparenz/','/impressum/']:
                self.assertIn('href="'+path+'"',body)
if __name__=='__main__':unittest.main()
