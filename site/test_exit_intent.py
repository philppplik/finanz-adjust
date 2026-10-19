import unittest
import exit_intent as m

class ExitIntentTests(unittest.TestCase):
    def test_attach_and_skip_reports_page(self):
        h='<html><body>x</body></html>'
        self.assertIn('id="fa-exit"', m.attach(h,'/'))
        self.assertIn('id="fa-exit"', m.attach(h,'/aktien/apple/'))
        self.assertEqual(m.attach(h,'/berichte/'), h)
    def test_accessibility_markup(self):
        s=m.SNIPPET
        self.assertIn('role="dialog"',s); self.assertIn('aria-modal="true"',s)
        self.assertIn('aria-labelledby="fa-exit-t"',s); self.assertIn('id="fa-exit-t"',s)
        self.assertIn('aria-label="Hinweis schlie',s)
        self.assertIn('id="fa-exit" hidden',s)
        self.assertIn('Escape',s); self.assertIn('Tab',s)
        self.assertIn('data-x',s)  # X + "Nein, danke" + backdrop close
    def test_links_point_to_current_report(self):
        self.assertIn('href="/berichte/aktuell.pdf"',m.SNIPPET)
        self.assertIn('href="/berichte/"',m.SNIPPET)
    def test_no_tracking_no_external_calls(self):
        s=m.SNIPPET
        self.assertNotIn('http://',s); self.assertNotIn('https://',s)
        self.assertNotIn('document.cookie',s); self.assertNotIn('localStorage',s)
        self.assertNotIn('fetch(',s); self.assertNotIn('XMLHttpRequest',s)
        self.assertNotIn('navigator.sendBeacon',s); self.assertNotIn('history.pushState',s)
    def test_once_per_session_and_armed_delay(self):
        s=m.SNIPPET
        self.assertIn('sessionStorage.getItem("fa-exit-report")',s)
        self.assertIn('sessionStorage.setItem("fa-exit-report","1")',s)
        self.assertIn('var ARM=8000',s)
        self.assertGreaterEqual(m.ARM_MS,5000)
    def test_no_fixed_layout_shift(self):
        self.assertIn('position:fixed',m.SNIPPET)

if __name__=='__main__': unittest.main()
