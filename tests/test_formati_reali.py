import unittest
from pathlib import Path

from subfindercli import risultati

FIX = Path(__file__).parent / "fixtures"
# (file, quanti risultati, gruppi attesi: insieme, None per non controllare, "NONVUOTI")
ATTESI = [("reale.jsonl", 5, "NONVUOTI"), ("reale.txt", 2, None)]


class FormatiRealiTest(unittest.TestCase):
    """Output veri di subfinder v2.17.0: se una versione nuova cambia formato, qui si rompe."""

    def test_fixture_reali(self):
        for nome, quanti, gruppi in ATTESI:
            voci = risultati.carica(FIX / nome)
            self.assertEqual(len(voci), quanti, nome)
            if gruppi == "NONVUOTI":
                self.assertTrue(all(v.gruppo for v in voci), nome)
            elif gruppi is not None:
                self.assertEqual({v.gruppo for v in voci}, gruppi, nome)

    def test_nessun_colore_nei_risultati(self):
        for nome, _, _ in ATTESI:
            for v in risultati.carica(FIX / nome):
                self.assertNotIn(chr(27), v.testo, nome)
                self.assertNotIn(chr(27), v.chiave, nome)


if __name__ == "__main__":
    unittest.main()
