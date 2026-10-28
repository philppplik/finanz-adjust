import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import licensed_news as n
class LicensedTests(unittest.TestCase):
 def sample(self,key='heise'):
  return dict(title='KI <Test> & Datenschutz',url={'heise':'https://www.heise.de/news/ki-test-123.html','destatis':'https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/10/PD26_371_421.html','ecb':'https://www.ecb.europa.eu//press/pr/date/2026/html/ecb.pr261007~6447350434.en.html'}[key],ts=1792400790,teaser='Ein erlaubter Anriss.',license_key=key,captured_at='2026-10-19T12:00:00+00:00')
 def test_strict_hosts_and_paths(self):
  for key in ('heise','destatis','ecb'):
   i=self.sample(key);self.assertTrue(n.matches(key,i['url']))
   for url in ['javascript:alert(1)','https://heise.de.evil.test/news/a.html','https://www.cnn.com/news/a.html','http://www.heise.de/news/a.html']:
    self.assertFalse(n.matches(key,url))
  for path in ['/press/key/date/2026/html/a.html','/pub/pdf/scpwps/a.pdf','/press/blog/date/2026/html/a.html']:
   self.assertFalse(n.matches('ecb','https://www.ecb.europa.eu'+path))
 def test_escape_and_no_remote_images(self):
  s=n.body(self.sample(),'Intelligenz Welt');self.assertIn('&lt;Test&gt;',s);self.assertNotIn('<Test>',s)
  self.assertEqual(s.count('class="ln-original"'),2);self.assertIn('noopener noreferrer nofollow',s);self.assertIn('ln-leaving',s)
  self.assertNotIn('<img',s);self.assertNotIn('<iframe',s);self.assertNotIn('<script',s)
 def test_immutable_and_failure_retention(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'data';p.mkdir();i=self.sample();(p/'news-pages.json').write_text(json.dumps([i]));old=n.detail_path(i)
   with patch('urllib.request.urlopen',side_effect=OSError('offline')):self.assertEqual(n.collect(t,'iw'),[i])
   self.assertEqual(n.detail_path(n.collect(t,'iw',fetch=False)[0]),old)
 def test_no_cached_foreign_teasers(self):
  with tempfile.TemporaryDirectory() as t:
   i=dict(self.sample(),title='DAX und Zinsen: <Test> & Kurse',url='https://www.finanznachrichten.de/nachrichten/a.htm',sum='UNAPPROVED',teaser='UNAPPROVED')
   rows=n.collect(t,'fa',[i],fetch=False);self.assertEqual(rows[0]['teaser'],'');self.assertEqual(rows[0]['sum'],'')
 def test_corrupt_archive_stops_without_overwrite(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'data';p.mkdir();f=p/'news-pages.json';f.write_text('{bad')
   with self.assertRaises(ValueError):n.collect(t,'iw',fetch=False)
   self.assertEqual(f.read_text(),'{bad')
 def test_feed_filters_and_no_injected_html(self):
  rss=b'<rss><channel><item><title>Bad speech</title><link>https://www.ecb.europa.eu/press/key/date/2026/html/a.html</link><pubDate>Mon, 19 Oct 2026 10:00:00 +0200</pubDate></item></channel></rss>'
  self.assertEqual(n.parse_feed(rss,'ecb'),[])
  self.assertEqual(n.text('<p>Hallo <b>Welt</b><img src="x"><script>attack</script></p>'),'Hallo Welt')
 def test_noindex_removes_canonical(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'index.html';p.write_text('<meta name="robots" content="index,follow"><link rel="canonical" href="x">');n.noindex(p);self.assertIn('noindex,follow',p.read_text());self.assertNotIn('canonical',p.read_text())
 def test_fn_feed_headline_only_and_finance_filter(self):
  fn=(b'<rss version="2.0"><channel><item><title>DAX vor Fed: Rally oder Ausverkauf?</title>'
      b'<description>Dieser Anrisstext darf nicht uebernommen werden.</description>'
      b'<link>https://www.finanznachrichten.de/nachrichten-2026-10/69958834-dax-vor-fed-349.htm</link>'
      b'<pubDate>2026-10-28T10:50:00Z</pubDate></item>'
      b'<item><title>Timo Boll schlaegt mit seinem Promi-Team bei der Tischtennis WM</title>'
      b'<description>Sport.</description>'
      b'<link>https://www.finanznachrichten.de/nachrichten-2026-10/69958000-timo-boll-349.htm</link>'
      b'<pubDate>2026-10-28T10:39:00Z</pubDate></item>'
      b'<item><title>Bundestag stimmt ueber Haushalt ab</title>'
      b'<description>Politik.</description>'
      b'<link>https://www.finanznachrichten.de/nachrichten-2026-10/69957000-bundestag-349.htm</link>'
      b'<pubDate>2026-10-28T10:38:00Z</pubDate></item></channel></rss>')
  rows=n.parse_feed(fn,'fn','https://www.finanznachrichten.de/rss-aktien-nachrichten')
  self.assertEqual(len(rows),1)
  self.assertEqual(rows[0]['teaser'],'')
  self.assertEqual(rows[0]['sum'],'')
  self.assertEqual(rows[0]['license_key'],'fn')
  self.assertEqual(rows[0]['feed_url'],'https://www.finanznachrichten.de/rss-aktien-nachrichten')
  self.assertTrue(rows[0]['ts']>0)
 def test_finance_relevance_boundaries(self):
  for ok in ['IAB-Arbeitsmarktbarometer steigt ueber 100 Punkte','UBS stuft DEUTSCHE BANK AG auf Buy','EZB teilt 164 Millionen zu','EQS-Adhoc: EUROKAI GmbH: Erwerb der TARROS-Gruppe']:
   self.assertTrue(n.finance_relevant(ok),ok)
  for bad in ['Bundestag stimmt ueber Haushalt ab','Polizei stellt Dieb am Bremer Platz','BVB besiegt Werder im DFB-Pokal','Timo Boll schlaegt mit seinem Promi-Team','Zwei Menschen im Verdacht des illegalen Aufenthalts']:
   self.assertFalse(n.finance_relevant(bad),bad)
 def test_collect_fn_multi_feed_and_gdelt_filter(self):
  fn=(b'<rss version="2.0"><channel><item><title>DAX vor Fed: Rally?</title>'
      b'<link>https://www.finanznachrichten.de/nachrichten-2026-10/69958834-dax-349.htm</link>'
      b'<pubDate>2026-10-28T10:50:00Z</pubDate></item></channel></rss>')
  class R:
   def __init__(self,data):self.data=data
   def __enter__(self):return self
   def __exit__(*a):return False
   def read(self,n):return self.data[:n]
  calls=[]
  def fake(req,timeout=20):
   calls.append(req.full_url);return R(fn)
  with tempfile.TemporaryDirectory() as t:
   with patch('urllib.request.urlopen',side_effect=fake):
    rows=n.collect(t,'fa',[dict(title='Polizei stellt Dieb',url='https://www.finanznachrichten.de/nachrichten/x.htm',ts=1,sum='',teaser='')]) if False else None
   with patch('urllib.request.urlopen',side_effect=fake):
    rows=n.collect(t,'fa',[dict(title='Polizei stellt Dieb',url='https://www.finanznachrichten.de/nachrichten/x.htm',ts=1,sum='',teaser='')])
   self.assertEqual([r['title'] for r in rows],['DAX vor Fed: Rally?'])
   self.assertEqual(len([u for u in calls if 'finanznachrichten.de/rss-' in u]),len(n.FN_FEEDS))
   self.assertEqual(len([u for u in calls if 'destatis.de' in u]),1)
   self.assertEqual(len([u for u in calls if 'ecb.europa.eu' in u]),1)
 def test_archive_body_caps_render_not_data(self):
  rows=[dict(title='DAX Meldung %d'%k,url='https://www.finanznachrichten.de/nachrichten-2026-10/%d-a.htm'%k,ts=1792400790-k,src='FinanzNachrichten',sum='',teaser='',license_key='fn',captured_at='2026-10-28',rights_checked='2026-10-28') for k in range(600)]
  h=n.archive_body(rows,'finanz adjust')
  self.assertIn('neuesten 500 von 600 dauerhaft gesicherten',h)
  self.assertEqual(h.count('DAX Meldung'),500)
  h2=n.archive_body(rows[:3],'finanz adjust')
  self.assertIn('3 dauerhaft gesicherte Quelleninfos',h2)
if __name__=='__main__':unittest.main()
