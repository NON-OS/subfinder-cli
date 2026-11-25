import tempfile
import unittest
from pathlib import Path

from subfindercli import audit


class AuditTest(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.addCleanup(self._d.cleanup)
        self.f = Path(self._d.name) / "a.jsonl"

    def _tre(self):
        for i in range(3):
            audit.registra(self.f, "evento", n=i)

    def test_catena_integra(self):
        self._tre()
        r = audit.verifica(self.f)
        self.assertTrue(r.valido)
        self.assertEqual(r.righe, 3)

    def test_file_inesistente(self):
        self.assertFalse(audit.verifica(self.f).valido)

    def test_modifica_nel_mezzo(self):
        self._tre()
        righe = self.f.read_text().splitlines()
        righe[1] = righe[1].replace('"n":1', '"n":9')
        self.f.write_text("\n".join(righe) + "\n")
        r = audit.verifica(self.f)
        self.assertFalse(r.valido)
        self.assertIn("riga 2", r.errore)

    def test_riga_cancellata(self):
        self._tre()
        righe = self.f.read_text().splitlines()
        self.f.write_text("\n".join([righe[0], righe[2]]) + "\n")
        r = audit.verifica(self.f)
        self.assertFalse(r.valido)
        self.assertIn("riga 2", r.errore)

    def test_garbage(self):
        self.f.write_text("non è json\n")
        self.assertFalse(audit.verifica(self.f).valido)

    def test_hash_concatenati(self):
        h1 = audit.registra(self.f, "a")
        h2 = audit.registra(self.f, "b")
        self.assertNotEqual(h1, h2)
        self.assertIn(h1, self.f.read_text().splitlines()[1])


if __name__ == "__main__":
    unittest.main()
