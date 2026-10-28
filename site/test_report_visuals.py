import unittest
import report_visuals as V


class ReportVisualsTest(unittest.TestCase):
    def test_spark_handles_short_and_flat(self):
        self.assertIn('–', V.spark([]))
        self.assertIn('<polyline', V.spark([5, 5, 5]))

    def test_logo_stocks_render_img_others_monogram(self):
        intel = V.mark({'sym': 'INTC'})
        self.assertIn('data:image/png;base64', intel)
        apple = V.mark({'sym': 'AAPL'})
        self.assertIn('<img', apple)  # Apple hat seit 28.10. ein echtes Logo
        mu = V.mark({'sym': 'MU'})
        self.assertNotIn('<img', mu)
        self.assertIn('MU', mu)

    def test_news_icons_are_local_data_uris(self):
        item = {'url': 'https://www.fool.com/x', 'title': 't', 'ts': 0}
        self.assertNotIn('http', V.src_icon(item).split('src="')[1].split('"')[0][:5])
        self.assertNotIn('tagesschau', V.news_rows([item]))

    def test_stock_href_links_known_tickers_only(self):
        self.assertEqual('/aktien/apple/', V.stock_href({'sym': 'AAPL'}))
        self.assertEqual('/aktien/sap/', V.stock_href({'sym': 'SAP.DE'}))
        self.assertEqual('/aktien/bmw-xetra/', V.stock_href({'sym': 'BMW.DE'}))
        for sym in ['^GDAXI', 'EURUSD=X', 'GC=F', 'BTC-USD', 'NOPE']:
            self.assertIsNone(V.stock_href({'sym': sym}), sym)

    def test_breadth_counts(self):
        out = V.breadth([{'pct': 1}, {'pct': -1}, {'pct': -2}])
        self.assertIn('<b>1</b> im Plus', out)
        self.assertIn('<b>2</b> im Minus', out)


if __name__ == '__main__':
    unittest.main()
