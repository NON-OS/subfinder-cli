import unittest

from subfindercli import audit, spec
from subfindercli.errors import ErroreCli
from subfindercli.profili import filtra_extra, nome_flag


class FiltroTest(unittest.TestCase):
    def test_flag_vietati_di_esempio(self):
        for esempio in spec.ESEMPI_VIETATI:
            with self.assertRaises(ErroreCli, msg=str(esempio)):
                filtra_extra(list(esempio), spec.VIETATI)

    def test_flag_ammessi_di_esempio(self):
        for esempio in spec.ESEMPI_AMMESSI:
            self.assertEqual(filtra_extra(list(esempio), spec.VIETATI), list(esempio))

    def test_maiuscole_trattini_e_uguale(self):
        nome = next(iter(spec.VIETATI))
        for forma in (f"-{nome.upper()}", f"--{nome}", f"-{nome}=x", f"--{nome.upper()}=x"):
            with self.assertRaises(ErroreCli, msg=forma):
                filtra_extra([forma], spec.VIETATI)

    def test_nome_flag(self):
        self.assertEqual(nome_flag("-X"), "x")
        self.assertEqual(nome_flag("--Foo=bar"), "foo")
        self.assertIsNone(nome_flag("-"))
        self.assertIsNone(nome_flag("80"))
        self.assertIsNone(nome_flag("--"))

    def test_i_valori_non_sono_flag(self):
        filtra_extra(["valore", "80", "-"], spec.VIETATI)


class ProfiliTest(unittest.TestCase):
    def test_campi_completi(self):
        for p in spec.PROFILI.values():
            self.assertTrue(p.descrizione and p.quando, p.nome)
            self.assertIn(p.rumore, {"basso", "medio", "alto"}, p.nome)
            self.assertIn(p.uscita, {"txt", "jsonl", "json"}, p.nome)

    def test_nomi_coerenti(self):
        for chiave, p in spec.PROFILI.items():
            self.assertEqual(chiave, p.nome)

    def test_profili_che_costruiscono_l_url(self):
        for p in spec.PROFILI.values():
            if spec.PASSA[0] == "uno":
                self.assertIn("{origine}", p.modello, p.nome)
                self.assertTrue(p.wordlist, p.nome)
            else:
                self.assertEqual(p.modello, "", p.nome)

    def test_nessun_flag_vietato_in_spec_vuoto(self):
        self.assertTrue(spec.VIETATI)
        self.assertTrue(spec.ESEMPI_VIETATI and spec.ESEMPI_AMMESSI)


class OscuraTest(unittest.TestCase):
    S = frozenset({"h", "header"})

    def test_valore_separato(self):
        self.assertEqual(audit.oscura(["x", "-H", "a: b", "-t", "1"], self.S), ["x", "-H", "[oscurato]", "-t", "1"])

    def test_valore_con_uguale(self):
        self.assertEqual(audit.oscura(["--header=a: b"], self.S), ["--header=[oscurato]"])

    def test_senza_segreti_non_cambia_niente(self):
        self.assertEqual(audit.oscura(["-t", "1"], self.S), ["-t", "1"])


if __name__ == "__main__":
    unittest.main()
