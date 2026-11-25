import tempfile
import unittest
from datetime import date
from pathlib import Path

from subfindercli import scope
from subfindercli.errors import FuoriScope, ScopeInvalido

TOML = """
[engagement]
nome = "test"
autorizzato_da = "Qualcuno, CISO, Acme"
riferimento = "ACME-2026-001"
valido_dal = 2026-11-01
valido_fino = 2026-11-30

[scope]
include = ["10.10.0.0/24", "192.168.56.10", "lab.example.org", "*.test.example.org"]
esclude = ["10.10.0.1", "vecchio.test.example.org"]
"""


def _carica(testo=TOML):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "scope.toml"
        p.write_text(testo)
        return scope.carica(p)


def _nessun_dns(_host):
    return []


class TargetTest(unittest.TestCase):
    def setUp(self):
        self.s = _carica()

    def ok(self, t):
        self.assertTrue(self.s.controlla(t, _nessun_dns).ammesso, t)

    def no(self, t):
        self.assertFalse(self.s.controlla(t, _nessun_dns).ammesso, t)

    def test_ip_dentro_la_rete(self):
        self.ok("10.10.0.77")

    def test_rete_contenuta(self):
        self.ok("10.10.0.128/25")

    def test_rete_piu_grande_dell_inclusa(self):
        self.no("10.10.0.0/16")

    def test_esclusione_batte_inclusione(self):
        self.no("10.10.0.1")

    def test_rete_che_contiene_un_escluso(self):
        self.no("10.10.0.0/24")

    def test_ip_fuori(self):
        self.no("8.8.8.8")

    def test_bit_d_host_nella_rete(self):
        self.no("10.10.0.5/24")

    def test_flag_travestito_da_target(self):
        self.no("-iL")
        self.no("--script=vuln")

    def test_range_alla_nmap(self):
        self.no("10.10.0.1-50")

    def test_hostname_esatto_e_maiuscole(self):
        self.ok("LAB.example.org.")

    def test_wildcard(self):
        self.ok("a.b.test.example.org")

    def test_wildcard_non_copre_la_radice(self):
        self.no("test.example.org")

    def test_wildcard_non_copre_suffissi_simili(self):
        self.no("evil-test.example.org")
        self.no("xtest.example.org.evil.com")

    def test_host_escluso(self):
        self.no("vecchio.test.example.org")

    def test_hostname_che_risolve_in_un_escluso(self):
        v = self.s.controlla("lab.example.org", lambda _h: ["10.10.0.1"])
        self.assertFalse(v.ammesso)
        self.assertIn("risolve", v.motivo)

    def test_ipv6_non_confusa_con_ipv4(self):
        self.no("2001:db8::1")

    def test_vuoto_e_spazi(self):
        self.no("")
        self.no("   ")

    def test_richiedi_blocca_tutto_se_uno_e_fuori(self):
        with self.assertRaises(FuoriScope) as cm:
            self.s.richiedi(["10.10.0.5", "8.8.8.8"], _nessun_dns)
        self.assertIn("8.8.8.8", str(cm.exception))


class CaricamentoTest(unittest.TestCase):
    def test_scaduto(self):
        s = _carica()
        with self.assertRaises(ScopeInvalido):
            s.verifica_validita(date(2026, 12, 1))

    def test_non_ancora_valido(self):
        s = _carica()
        with self.assertRaises(ScopeInvalido):
            s.verifica_validita(date(2026, 10, 31))

    def test_ultimo_giorno_e_valido(self):
        _carica().verifica_validita(date(2026, 11, 30))

    def test_tutto_internet_rifiutato(self):
        with self.assertRaises(ScopeInvalido):
            _carica(TOML.replace('"10.10.0.0/24"', '"0.0.0.0/0"'))

    def test_wildcard_su_tld_rifiutato(self):
        with self.assertRaises(ScopeInvalido):
            _carica(TOML.replace('"*.test.example.org"', '"*.org"'))

    def test_campo_mancante(self):
        with self.assertRaises(ScopeInvalido):
            _carica(TOML.replace('riferimento = "ACME-2026-001"\n', ""))

    def test_include_vuoto(self):
        with self.assertRaises(ScopeInvalido):
            _carica(
                TOML.replace(
                    'include = ["10.10.0.0/24", "192.168.56.10", "lab.example.org", "*.test.example.org"]',
                    "include = []",
                )
            )

    def test_toml_rotto(self):
        with self.assertRaises(ScopeInvalido):
            _carica("[engagement\n")

    def test_file_inesistente(self):
        with self.assertRaises(ScopeInvalido):
            scope.carica("/non/esiste.toml")


if __name__ == "__main__":
    unittest.main()
