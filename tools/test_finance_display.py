import copy, unittest
import licensed_news as n
class DisplayTests(unittest.TestCase):
 def test_sports_wire_labels_are_not_finance(self):
  for t in ['SPORT/ROUNDUP: Bayern gewinnt und setzt Rekord','ROUNDUP 2: BVB an Tabellenspitze','BVB gewinnt Borussen-Duell','Tennis: Millionen Preisgeld im Finale']:
   self.assertFalse(n.finance_relevant(t),t)
 def test_financial_sports_company_and_economic_policy(self):
  for t in ['BVB-Aktie: Quartalsumsatz steigt','Bundestag beschliesst Haushalt mit Milliarden Investitionen','Zollpolitik belastet Aktien','Lkw-Maut-Fahrleistungsindex sinkt','Spritpreise und Preisdeckel im Bundestag','Renten-Pläne und Beitragslast']:
   self.assertTrue(n.finance_relevant(t),t)
 def test_generic_wire_and_result_not_enough(self):
  for t in ['ROUNDUP: Parteichef wiedergewaehlt','ROUNDUP: Hausarzt beklagt Impfstoffmangel','Ergebnis der Kandidatenwahl','Rekord beim Stadtfest']:
   self.assertFalse(n.finance_relevant(t),t)
 def test_display_never_deletes_archive_and_handles_legacy(self):
  a=[dict(title='SPORT/ROUNDUP: Bayern gewinnt',url='https://example.com/a',license_key='fn'),dict(title='DAX steigt',url='https://example.com/b'),dict(title='Amtliche Pressemitteilung',url='https://example.com/c',license_key='destatis')]
  old=copy.deepcopy(a);out=n.display_news(a)
  self.assertEqual(a,old);self.assertEqual([x['url'] for x in out],[a[1]['url'],a[2]['url']])
