import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from subfindercli import cli, errors, firma
from subfindercli.errors import ScopeInvalido

SCOPE = """
[engagement]
nome = "t"
autorizzato_da = "Qualcuno"
riferimento = "REF-1"
valido_dal = 2000-01-01
valido_fino = 2999-12-31

[scope]
include = ["example.org", "*.example.org", "10.0.0.0/24"]
"""

OK = "example.org"
PROFILO = "completo"


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = cli.main(list(args))
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


def nuova_chiave(nome: str) -> str:
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", nome], check=True)
    tipo, corpo = Path(nome + ".pub").read_text().split()[:2]
    return f"{tipo} {corpo}"


@unittest.skipUnless(shutil.which("ssh-keygen"), "serve ssh-keygen")
class FirmaTest(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.addCleanup(self._d.cleanup)
        self.cwd = os.getcwd()
        os.chdir(self._d.name)
        self.addCleanup(os.chdir, self.cwd)
        Path("scope.toml").write_text(SCOPE)
        pubblica = nuova_chiave("cliente")
        Path("firmatari").write_text(f'cliente@example.org namespaces="{firma.NAMESPACE}" {pubblica}\n')

    def test_firma_e_verifica(self):
        sig = firma.firma("scope.toml", "cliente")
        chi = firma.verifica(Path("scope.toml").read_bytes(), sig, "firmatari")
        self.assertEqual(chi.identita, "cliente@example.org")
        self.assertTrue(chi.impronta.startswith("SHA256:"))

    def test_scope_modificato_dopo_la_firma(self):
        sig = firma.firma("scope.toml", "cliente")
        manomesso = Path("scope.toml").read_bytes() + b'\n# include = ["0.0.0.0/1"]\n'
        with self.assertRaises(ScopeInvalido):
            firma.verifica(manomesso, sig, "firmatari")

    def test_chiave_non_ammessa(self):
        nuova_chiave("intruso")
        sig = firma.firma("scope.toml", "intruso")
        with self.assertRaises(ScopeInvalido):
            firma.verifica(Path("scope.toml").read_bytes(), sig, "firmatari")

    def test_firma_fatta_per_un_altro_scopo(self):
        subprocess.run(
            ["ssh-keygen", "-Y", "sign", "-f", "cliente", "-n", "git", "scope.toml"],
            check=True, capture_output=True,
        )  # fmt: skip
        with self.assertRaises(ScopeInvalido):
            firma.verifica(Path("scope.toml").read_bytes(), "scope.toml.sig", "firmatari")

    def test_firma_mancante(self):
        with self.assertRaises(ScopeInvalido):
            firma.verifica(b"x", "non-c-e.sig", "firmatari")

    def test_non_sovrascrive_una_firma_esistente(self):
        firma.firma("scope.toml", "cliente")
        with self.assertRaises(ScopeInvalido):
            firma.firma("scope.toml", "cliente")

    def test_lancia_con_scope_firmato_e_l_audit_ricorda_chi_ha_firmato(self):
        self.assertEqual(run("scope-firma", "scope.toml", "--chiave", "cliente")[0], errors.OK)
        rc, out, _ = run(
            "lancia", PROFILO, OK, "--scope", "scope.toml", "--firmatari", "firmatari", "--audit", "a.jsonl"
        )
        self.assertEqual(rc, errors.OK, out)
        self.assertIn("Firma    : valida", out)
        registro = Path("a.jsonl").read_text()
        self.assertIn("cliente@example.org", registro)
        self.assertIn("SHA256:", registro)

    def test_lancia_con_scope_manomesso_non_parte_e_non_logga(self):
        run("scope-firma", "scope.toml", "--chiave", "cliente")
        with open("scope.toml", "a") as f:
            f.write("\n# ritoccato\n")
        rc, _, err = run(
            "lancia", PROFILO, OK, "--scope", "scope.toml", "--firmatari", "firmatari", "--audit", "a.jsonl"
        )
        self.assertEqual(rc, errors.SCOPE_INVALIDO)
        self.assertIn("firma non valida", err)
        self.assertFalse(Path("a.jsonl").exists())

    def test_senza_firmatari_la_firma_non_e_richiesta(self):
        rc, *_ = run("lancia", PROFILO, OK, "--scope", "scope.toml", "--audit", "a.jsonl")
        self.assertEqual(rc, errors.OK)

    def test_scope_verifica_da_riga_di_comando(self):
        run("scope-firma", "scope.toml", "--chiave", "cliente")
        rc, out, _ = run("scope-verifica", "scope.toml", "--firmatari", "firmatari")
        self.assertEqual(rc, errors.OK)
        self.assertIn("cliente@example.org", out)

    def test_verifica_e_filtra_accettano_la_firma(self):
        run("scope-firma", "scope.toml", "--chiave", "cliente")
        self.assertEqual(run("verifica", OK, "--scope", "scope.toml", "--firmatari", "firmatari")[0], errors.OK)
        with open("scope.toml", "a") as f:
            f.write("# x\n")
        self.assertEqual(
            run("verifica", OK, "--scope", "scope.toml", "--firmatari", "firmatari")[0], errors.SCOPE_INVALIDO
        )


if __name__ == "__main__":
    unittest.main()
