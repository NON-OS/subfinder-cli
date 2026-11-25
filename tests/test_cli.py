import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from subfindercli import cli, errors, spec

SCOPE = """
[engagement]
nome = "t"
autorizzato_da = "Qualcuno"
riferimento = "REF-1"
valido_dal = 2000-01-01
valido_fino = 2999-12-31

[scope]
include = ["example.org", "*.example.org", "10.0.0.0/24"]
esclude = ["admin.example.org", "10.0.0.9"]
"""

OK = "example.org"
FUORI = "altro.org"
ESEMPIO = "a.example.org\nb.example.org\n"
PROFILO = "completo"


def run(*args, stdin=None):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            if stdin is not None:
                with mock.patch("sys.stdin", io.StringIO(stdin)):
                    rc = cli.main(list(args))
            else:
                rc = cli.main(list(args))
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


def finto_binario(cartella: Path) -> None:
    """Un eseguibile che scrive i risultati d'esempio dove il programma gli chiede di scrivere."""
    p = cartella / spec.BINARIO
    p.write_text(
        f'#!/bin/sh\nif [ "$1" = "{spec.VERSIONE[0]}" ]; then echo "{spec.RICONOSCI} v0"; exit 0; fi\n'
        'prev=""\nfor a in "$@"; do\n'
        f'  if [ "$prev" = "{spec.USCITA}" ]; then /bin/cat > "$a" <<\'FINE\'\n{ESEMPIO}\nFINE\n  fi\n'
        '  prev="$a"\ndone\nexit 0\n'
    )
    p.chmod(0o755)


class CliTest(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.addCleanup(self._d.cleanup)
        d = Path(self._d.name)
        self.bin = d / "bin"
        self.bin.mkdir()
        self.scope = str(d / "scope.toml")
        Path(self.scope).write_text(SCOPE)
        self.audit = str(d / "a.jsonl")
        self.wl = d / "wordlist.txt"
        self.wl.write_text("admin\n")
        self.extra = ["--wordlist", str(self.wl)] if spec.PASSA[0] == "uno" else []
        self.cwd = os.getcwd()
        os.chdir(d)
        self.addCleanup(os.chdir, self.cwd)
        vecchio = os.environ["PATH"]
        os.environ["PATH"] = str(self.bin)  # solo il finto eseguibile, se c'è
        self.addCleanup(os.environ.__setitem__, "PATH", vecchio)

    def lancia(self, *target, tool=(), **kw):
        """tool: flag da passare dopo '--' (vanno per ultimi, altrimenti inghiottono --scope)."""
        coda = ["--", *tool] if tool else []
        return run("lancia", PROFILO, *target, "--scope", self.scope, "--audit", self.audit, *self.extra, *coda, **kw)

    # -- dry-run e scope -------------------------------------------------

    def test_dry_run_senza_binario_e_senza_output(self):
        rc, out, _ = self.lancia(OK)
        self.assertEqual(rc, errors.OK)
        self.assertIn("Dry-run", out)
        self.assertIn("anteprima", out)
        self.assertFalse(Path("out").exists())
        self.assertIn('"evento":"dry_run"', Path(self.audit).read_text())

    def test_fuori_scope_esce_con_3_e_non_logga(self):
        rc, _, err = self.lancia(OK, FUORI)
        self.assertEqual(rc, errors.FUORI_SCOPE)
        self.assertIn(FUORI, err)
        self.assertFalse(Path(self.audit).exists())

    def test_verifica(self):
        self.assertEqual(run("verifica", OK, "--scope", self.scope)[0], errors.OK)
        self.assertEqual(run("verifica", FUORI, "--scope", self.scope)[0], errors.FUORI_SCOPE)

    def test_flag_vietato_dopo_doppio_trattino(self):
        rc, _, err = self.lancia(OK, tool=spec.ESEMPI_VIETATI[0])
        self.assertEqual(rc, errors.USO)
        self.assertIn("non è ammesso", err)

    def test_ogni_flag_vietato_di_esempio_e_rifiutato(self):
        for esempio in spec.ESEMPI_VIETATI:
            rc, *_ = self.lancia(OK, tool=esempio)
            self.assertEqual(rc, errors.USO, esempio)

    def test_scope_mancante(self):
        rc, *_ = run("verifica", OK, "--scope", "nope.toml")
        self.assertEqual(rc, errors.SCOPE_INVALIDO)

    # -- esecuzione ------------------------------------------------------

    def test_esegui_senza_binario_esce_con_5(self):
        rc, *_ = self.lancia(OK, "--esegui", "--conferma")
        self.assertEqual(rc, errors.BINARIO_ASSENTE)

    def test_trova_un_binario_con_nome_alternativo(self):
        """Su Kali httpx si chiama 'httpx-toolkit': il wrapper deve trovarlo lo stesso."""
        from subfindercli import runner

        if not getattr(spec, "BINARI_ALT", ()):
            self.skipTest("questo tool non ha nomi di binario alternativi")
        alt = self.bin / spec.BINARI_ALT[0]
        alt.write_text("#!/bin/sh\nexit 0\n")
        alt.chmod(0o755)
        self.assertEqual(runner.trova(), str(alt))

    def test_un_programma_omonimo_viene_rifiutato(self):
        """Nel PATH può esserci un altro programma con lo stesso nome (httpx Python, per esempio)."""
        p = self.bin / spec.BINARIO
        p.write_text("#!/bin/sh\necho 'un altro programma, versione 0.28'\nexit 0\n")
        p.chmod(0o755)
        rc, _, err = self.lancia(OK, "--esegui", "--conferma")
        self.assertEqual(rc, errors.BINARIO_ASSENTE)
        self.assertIn("non sembra", err)
        self.assertFalse(Path(self.audit).exists())
        rc, _, err = run("doctor")
        self.assertEqual(rc, errors.BINARIO_ASSENTE)

    def test_esegui_senza_conferma_in_ambiente_non_interattivo(self):
        finto_binario(self.bin)
        rc, _, err = self.lancia(OK, "--esegui")
        self.assertEqual(rc, errors.RIFIUTATO)
        self.assertIn("conferma", err)
        self.assertIn('"evento":"rifiutato"', Path(self.audit).read_text())

    def test_esecuzione_completa_audit_e_rapporto(self):
        finto_binario(self.bin)
        rc, out, _ = self.lancia(OK, "--esegui", "--conferma", "--out", "risultati_prova")
        self.assertEqual(rc, errors.OK, out)
        eventi = [json.loads(r)["corpo"]["evento"] for r in Path(self.audit).read_text().splitlines()]
        self.assertEqual(eventi, ["avviata", "conclusa"])
        self.assertEqual(run("audit", self.audit)[0], errors.OK)
        rc, out, _ = run("rapporto", "risultati_prova")
        self.assertEqual(rc, errors.OK)
        self.assertIn(f"{2} risultati", out)
        rc, out, _ = run("rapporto", "risultati_prova", "--formato", "json")
        self.assertEqual(json.loads(out)["riepilogo"]["totale"], 2)

    def test_i_target_arrivano_da_stdin(self):
        rc, out, _ = self.lancia("-", stdin=f"# commento\n{OK}\n\n{OK}\n")
        self.assertEqual(rc, errors.OK)
        self.assertEqual(out.count("  ok  "), 1)  # il doppione è eliminato

    def test_valori_sensibili_oscurati_nell_audit(self):
        if "h" not in spec.SEGRETI:
            self.skipTest("questo tool non ha flag con segreti")
        rc, *_ = self.lancia(OK, tool=("-H", "Authorization: Bearer SEGRETISSIMO"))
        self.assertEqual(rc, errors.OK)
        self.assertNotIn("SEGRETISSIMO", Path(self.audit).read_text())
        self.assertIn("oscurato", Path(self.audit).read_text())

    def test_stdin_non_arriva_al_tool(self):
        """httpx e naabu leggono target anche da stdin: se arrivassero, aggirerebbero lo scope."""
        import subprocess
        import sys

        d = Path(self._d.name)
        script = d / "bin" / spec.BINARIO
        script.write_text(
            f'#!/bin/sh\nif [ "$1" = "{spec.VERSIONE[0]}" ]; then echo "{spec.RICONOSCI} v0"; exit 0; fi\n'
            "/bin/cat > stdin_visto\nexit 0\n"
        )
        script.chmod(0o755)
        env = dict(os.environ, PYTHONPATH=str(Path(cli.__file__).parents[1]))
        r = subprocess.run(
            [sys.executable, "-m", "subfindercli", "lancia", PROFILO, OK, "--scope", self.scope,
             "--audit", self.audit, *self.extra, "--esegui", "--conferma", "--out", "o"],
            input="evil.example.org\n", capture_output=True, text=True, env=env, cwd=d,
        )  # fmt: skip
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((d / "stdin_visto").read_text(), "")

    # -- filtra, init, profili, confronta -----------------------------------

    def test_filtra_lascia_solo_cio_che_e_nello_scope(self):
        rc, out, err = run("filtra", "--scope", self.scope, stdin=f"{OK}\n{FUORI}\n")
        self.assertEqual(rc, errors.OK)
        self.assertEqual(out.split(), [OK])
        self.assertIn("1 scartati", err)

    def test_init_non_sovrascrive(self):
        self.assertEqual(run("init", "nuovo.toml")[0], errors.OK)
        self.assertEqual(run("init", "nuovo.toml")[0], errors.USO)

    def test_il_modello_di_init_e_valido_ma_non_autorizza_nulla(self):
        run("init", "m.toml")
        rc, *_ = run("verifica", FUORI, "--scope", "m.toml")
        self.assertIn(rc, (errors.FUORI_SCOPE, errors.SCOPE_INVALIDO))

    def test_profili_elenca_tutto(self):
        rc, out, _ = run("profili")
        self.assertEqual(rc, errors.OK)
        for nome in spec.PROFILI:
            self.assertIn(nome, out)

    def test_confronta_due_cartelle(self):
        finto_binario(self.bin)
        self.lancia(OK, "--esegui", "--conferma", "--out", "a")
        self.lancia(OK, "--esegui", "--conferma", "--out", "b")
        rc, out, _ = run("confronta", "a", "b", "--exit-code")
        self.assertEqual((rc, out.strip()), (0, "Nessuna differenza."))


class BannerTest(unittest.TestCase):
    def test_a_mani_vuote_mostra_logo_e_suggerimento(self):
        rc, out, err = run()
        self.assertEqual(rc, errors.OK)
        self.assertIn("scope-first", err)
        self.assertIn("guida", err)


class GuidaTest(unittest.TestCase):
    def setUp(self):
        self._d = tempfile.TemporaryDirectory()
        self.addCleanup(self._d.cleanup)
        self.cwd = os.getcwd()
        os.chdir(self._d.name)
        self.addCleanup(os.chdir, self.cwd)
        Path("scope.toml").write_text(SCOPE)
        Path("wl.txt").write_text("admin\n")  # per i tool "uno" (ffuf)

    def _inputs(self, profilo, target, esegui):
        seq = ["scope.toml", profilo, target]
        if spec.PASSA[0] == "uno":
            seq.append("wl.txt")
        seq.append(esegui)
        return seq

    def guida(self, inputs):
        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", side_effect=inputs):
            return run("guida")

    def test_non_interattivo_rifiutato(self):
        with mock.patch("sys.stdin.isatty", return_value=False):
            rc, _, err = run("guida")
        self.assertEqual(rc, errors.USO)
        self.assertIn("interattivo", err)

    def test_dry_run_non_lancia_niente(self):
        rc, out, _ = self.guida(self._inputs(PROFILO, OK, "no"))
        self.assertEqual(rc, errors.OK, out)
        self.assertIn("Dry-run", out)
        self.assertFalse(Path("out").exists())

    def test_target_fuori_scope(self):
        rc, _, _ = self.guida(self._inputs(PROFILO, FUORI, "no"))
        self.assertEqual(rc, errors.FUORI_SCOPE)

    def test_profilo_scelto_per_numero(self):
        rc, out, _ = self.guida(self._inputs("1", OK, "no"))
        self.assertEqual(rc, errors.OK, out)

    def test_profilo_sbagliato(self):
        rc, _, err = self.guida(["scope.toml", "profilo-che-non-esiste"])
        self.assertEqual(rc, errors.USO)
        self.assertIn("profilo", err)

    def test_scope_mancante_offre_di_crearlo(self):
        Path("scope.toml").unlink()
        rc, _, _ = self.guida(["scope.toml", "s"])
        self.assertEqual(rc, errors.OK)
        self.assertTrue(Path("scope.toml").exists())


if __name__ == "__main__":
    unittest.main()
