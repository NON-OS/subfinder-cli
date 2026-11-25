import json
import tempfile
import unittest
from pathlib import Path

from subfindercli import risultati, spec
from subfindercli.risultati import RisultatiIllegibili

ESEMPIO = "a.example.org\nb.example.org\n"


def file_con(testo, nome="risultati.txt"):
    d = Path(tempfile.mkdtemp())
    (d / nome).write_text(testo)
    return d


class LetturaTest(unittest.TestCase):
    def test_conta_i_risultati(self):
        self.assertEqual(len(spec.voci(ESEMPIO)), 2)

    def test_vuoto_e_spazzatura_non_rompono_niente(self):
        self.assertEqual(spec.voci(""), [])
        spec.voci("\n\n   \n")
        spec.voci("{non json\n")
        spec.voci("[1, 2, 3]")
        spec.voci('{"x": 1}\n')

    def test_carica_cartella_e_file(self):
        d = file_con(ESEMPIO)
        self.assertEqual(len(risultati.carica(d)), 2)
        self.assertEqual(len(risultati.carica(d / "risultati.txt")), 2)

    def test_cartella_senza_risultati(self):
        with self.assertRaises(RisultatiIllegibili):
            risultati.carica(tempfile.mkdtemp())

    def test_percorso_inesistente(self):
        with self.assertRaises(RisultatiIllegibili):
            risultati.carica("/non/esiste")

    def test_i_doppioni_si_eliminano(self):
        d = file_con(ESEMPIO)
        (d / "risultati-2.txt").write_text(ESEMPIO)
        self.assertEqual(len(risultati.carica(d)), 2)


class RiepilogoTest(unittest.TestCase):
    def test_formati(self):
        voci = spec.voci(ESEMPIO)
        self.assertIn(f"{2} risultati", risultati.a_testo(voci))
        self.assertIn("# Rapporto", risultati.a_markdown(voci, "Rapporto prova"))
        self.assertEqual(json.loads(risultati.a_json(voci))["riepilogo"]["totale"], 2)

    def test_confronto(self):
        voci = spec.voci(ESEMPIO)
        d = risultati.confronta(voci[:1], voci)
        self.assertEqual(len(d.nuovi), len(voci) - 1)
        self.assertEqual(d.spariti, [])
        self.assertTrue(risultati.confronta(voci, voci).vuoto())
        self.assertIn("Nessuna differenza", risultati.differenze_a_testo(risultati.confronta(voci, voci)))
        self.assertIn("+ ", risultati.differenze_a_testo(d))

    def test_confronto_con_spariti(self):
        voci = spec.voci(ESEMPIO)
        d = risultati.confronta(voci, voci[:1])
        self.assertEqual(len(d.spariti), len(voci) - 1)
        self.assertIn("- ", risultati.differenze_a_testo(d))


class AiutantiTest(unittest.TestCase):
    """sotto_dict, lista e righe_json: usati per leggere un campo JSON senza dare per
    scontato il suo tipo. Il bersaglio scrive l'output, quindi un campo che dovrebbe
    essere un dict o una lista può essere benissimo una stringa, un numero o mancare."""

    def test_sotto_dict(self):
        self.assertEqual(risultati.sotto_dict({"a": 1}), {"a": 1})
        self.assertEqual(risultati.sotto_dict("non un dict"), {})
        self.assertEqual(risultati.sotto_dict(None), {})
        self.assertEqual(risultati.sotto_dict([1, 2]), {})
        self.assertEqual(risultati.sotto_dict(42), {})

    def test_lista(self):
        self.assertEqual(risultati.lista([1, 2]), [1, 2])
        self.assertEqual(risultati.lista("non una lista"), [])
        self.assertEqual(risultati.lista(None), [])
        self.assertEqual(risultati.lista({"a": 1}), [])

    def test_righe_json_righe_miste(self):
        testo = '{"a": 1}\ntesto semplice\n{non valido come json\n[1, 2, 3]\n\n   \n{"b": 2}'
        r = risultati.righe_json(testo)
        self.assertEqual(r[0], {"a": 1})
        self.assertEqual(r[1], "testo semplice")
        self.assertEqual(r[2], "{non valido come json")
        self.assertEqual(r[3], "[1, 2, 3]")  # JSON valido ma non un oggetto: resta testo
        self.assertEqual(r[4], {"b": 2})
        self.assertEqual(len(r), 5)  # le righe vuote non producono voci


if __name__ == "__main__":
    unittest.main()
