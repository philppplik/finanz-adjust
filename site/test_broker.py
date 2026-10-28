import json,unittest
from pathlib import Path
D=json.loads((Path(__file__).resolve().parent.parent/'content/broker/brokers.json').read_text())
class T(unittest.TestCase):
    def test_data(self):
        ids=[b['id'] for b in D['brokers']];self.assertEqual(len(ids),len(set(ids)))
        for b in D['brokers']:
            self.assertTrue(b['url'].startswith('https://') and b['plv'].startswith('https://'))
            self.assertTrue(b['hinweis'])
            self.assertNotIn('aff',(b['url']+b['plv']).lower().split('?')[-1])
if __name__=='__main__':unittest.main()
