import tempfile
import unittest
from pathlib import Path

from subfindercli import scope

TOML = """
[engagement]
nome = "t"
autorizzato_da = "Qualcuno"
riferimento = "R"
valido_dal = 2000-01-01
valido_fino = 2999-12-31

[scope]
include = ["example.org", "*.example.org", "10.0.0.0/24"]
esclude = ["admin.example.org", "10.0.0.9"]
"""


def _scope():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.toml"
        p.write_text(TOML)
        return scope.carica(p)


def nessun_dns(_h):
    return []


class UrlTest(unittest.TestCase):
    def setUp(self):
        self.s = _scope()

    def ok(self, t):
        v = self.s.controlla(t, nessun_dns, modo="url")
        self.assertTrue(v.ammesso, f"{t}: {v.motivo}")

    def no(self, t):
        self.assertFalse(self.s.controlla(t, nessun_dns, modo="url").ammesso, t)

    def test_forme_ammesse(self):
        self.ok("https://a.example.org")
        self.ok("https://a.example.org/percorso?x=1#y")
        self.ok("a.example.org:8443")
        self.ok("a.example.org")
        self.ok("http://10.0.0.5:3000/")
        self.ok("example.org")

    def test_fuori_scope(self):
        self.no("https://evil.org")
        self.no("https://a.example.org.evil.org")
        self.no("https://example.org.evil.org/a.example.org")
        self.no("http://11.0.0.5")

    def test_escluso(self):
        self.no("https://admin.example.org/login")
        self.no("http://10.0.0.9")

    def test_credenziali_nell_url(self):
        self.no("http://10.0.0.5@evil.org/")
        self.no("http://a.example.org:pass@evil.org/")
        self.no("https://user@a.example.org")

    def test_backslash_e_spazi(self):
        self.no("http://evil.org\\@a.example.org")
        self.no("https://a.example.org /x")
        self.no("https://a.example.org\\x")

    def test_schemi_non_ammessi(self):
        self.no("ftp://a.example.org")
        self.no("file:///etc/passwd")
        self.no("javascript:alert(1)")
        self.no("gopher://a.example.org")

    def test_porta_non_valida(self):
        self.no("https://a.example.org:99999")
        self.no("https://a.example.org:abc")

    def test_ipv6_e_cidr(self):
        self.no("https://[::1]/")
        self.no("10.0.0.0/24")
        self.no("10.0.0.5/24")
        self.no("192.0.2.0/25")

    def test_un_percorso_numerico_su_un_nome_non_e_un_cidr(self):
        self.ok("a.example.org/24")

    def test_vuoto_e_flag(self):
        self.no("")
        self.no("-u")
        self.no("--help")


class DominioTest(unittest.TestCase):
    def setUp(self):
        self.s = _scope()

    def controlla(self, t):
        return self.s.controlla(t, nessun_dns, modo="dominio").ammesso

    def test_ammessi(self):
        self.assertTrue(self.controlla("example.org"))
        self.assertTrue(self.controlla("a.example.org"))
        self.assertTrue(self.controlla("EXAMPLE.org."))

    def test_non_ammessi(self):
        self.assertFalse(self.controlla("10.0.0.5"))
        self.assertFalse(self.controlla("https://example.org"))
        self.assertFalse(self.controlla("example.org/x"))
        self.assertFalse(self.controlla("example.org:80"))
        self.assertFalse(self.controlla("evil.org"))
        self.assertFalse(self.controlla("admin.example.org"))


class AiutantiTest(unittest.TestCase):
    def test_estrai_host(self):
        self.assertEqual(scope.estrai_host("https://A.example.org:8443/x")[0], "a.example.org")
        self.assertEqual(scope.estrai_host("a.example.org:80")[0], "a.example.org")
        self.assertEqual(scope.estrai_host("https://[::1]:80/")[0], "::1")
        self.assertIsNone(scope.estrai_host("http://a@b")[0])

    def test_origine(self):
        self.assertEqual(scope.origine("a.example.org"), "https://a.example.org")
        self.assertEqual(scope.origine("a.example.org:8443/x"), "https://a.example.org:8443")
        self.assertEqual(scope.origine("http://a.example.org:3000/x?y"), "http://a.example.org:3000")

    def test_richiedi_blocca_tutto_se_uno_e_fuori(self):
        s = _scope()
        with self.assertRaises(scope.FuoriScope):
            s.richiedi(["https://a.example.org", "https://evil.org"], nessun_dns, modo="url")


if __name__ == "__main__":
    unittest.main()
