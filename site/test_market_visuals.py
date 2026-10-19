import unittest
import market_visuals as MV

Q = [{'sym': 'AAPL', 'name': 'Apple', 'pct': 1.0, 'price': 100.0, 'chg': 1.0},
     {'sym': 'MSFT', 'name': 'Microsoft', 'pct': -2.0, 'price': 200.0, 'chg': -4.0},
     {'sym': 'ZZZZ', 'name': 'Other', 'pct': 0.0, 'price': 5.0, 'chg': 0.0}]


class MarketVisualsTest(unittest.TestCase):
    def test_breadth_counts_and_empty(self):
        out = MV.breadth(Q)
        self.assertIn('<b>1</b> im Plus', out)
        self.assertIn('<b>1</b> im Minus', out)
        self.assertIn('<b>1</b> unverändert', out)
        self.assertEqual(MV.breadth([]), '')
        self.assertEqual(MV.home_block([]), '')

    def test_movers_link_known_and_plain_unknown(self):
        out = MV.movers(Q)
        self.assertIn('href="/aktien/apple/"', out)
        self.assertIn('Größte Gewinner', out)

    def test_heat_tiles_sorted_and_escaped(self):
        q = [dict(Q[1], name='A<b>')] + [Q[0]]
        out = MV.heat_tiles(q)
        self.assertLess(out.index('Apple'), out.index('A&lt;b&gt;'))

    def test_german_numbers(self):
        self.assertEqual(MV._num(1234.5), '1.234,50')
        self.assertEqual(MV._sg(-1.234), '-1,23')
        self.assertEqual(MV._sg(1.0), '+1,00')

    def test_stock_spark_only_with_history(self):
        self.assertEqual(MV.stock_spark_panel({'ticker': 'NOPE'}), '')


if __name__ == '__main__':
    unittest.main()
