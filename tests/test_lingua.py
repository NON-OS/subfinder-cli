"""Lingua: si parte in italiano, inglese e cinese su richiesta, e tutto l'output cambia."""

from __future__ import annotations

import io
import os
import string
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from subfindercli import cli, i18n, spec

SCOPE = """
[engagement]
nome = "PROVA"
autorizzato_da = "Mario Bianchi, CISO"
riferimento = "PROVA-1"
valido_dal = 2026-01-01
valido_fino = 2099-12-31

[scope]
include = ["example.org"]
"""


def _senza_nonos_lang() -> mock._patch[dict[str, str]]:
    env = {k: v for k, v in os.environ.items() if k != "NONOS_LANG"}
    return mock.patch.dict(os.environ, env, clear=True)


class TestLingua(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.scope = Path(self.dir.name) / "scope.toml"
        self.scope.write_text(SCOPE)

    def tearDown(self) -> None:
        i18n.imposta_lingua("it")
        spec.applica_lingua("it")
        self.dir.cleanup()

    def _esegui(self, *argv: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with _senza_nonos_lang(), redirect_stdout(out), redirect_stderr(err):
            try:
                rc = cli.main(list(argv))
            except SystemExit as e:
                rc = int(e.code or 0)
        return rc, out.getvalue() + err.getvalue()

    # -- scelta della lingua ---------------------------------------------------

    def test_si_parte_in_italiano_anche_con_un_locale_inglese(self) -> None:
        with _senza_nonos_lang(), mock.patch.dict(os.environ, {"LANG": "en_US.UTF-8", "LC_ALL": "en_US.UTF-8"}):
            self.assertEqual(i18n.imposta_lingua(), "it")

    def test_nonos_lang_sceglie_la_lingua(self) -> None:
        with mock.patch.dict(os.environ, {"NONOS_LANG": "zh_CN"}):
            self.assertEqual(i18n.imposta_lingua(), "zh")

    def test_il_flag_batte_la_variabile(self) -> None:
        with mock.patch.dict(os.environ, {"NONOS_LANG": "zh"}):
            self.assertEqual(i18n.imposta_lingua("en"), "en")

    def test_lingua_sconosciuta_ripiega_sull_italiano(self) -> None:
        with _senza_nonos_lang():
            self.assertEqual(i18n.imposta_lingua("fr"), "it")

    def test_forma_con_uguale(self) -> None:
        rc, testo = self._esegui("--lang=en", "profili")
        self.assertEqual(rc, 0)
        self.assertIn("noise", testo)

    # -- catalogo ------------------------------------------------------------

    def test_ogni_messaggio_ha_tre_lingue_con_gli_stessi_campi(self) -> None:
        def campi(testo: str) -> set[str]:
            return {f for _, f, _, _ in string.Formatter().parse(testo) if f}

        for chiave, voci in i18n.MSG.items():
            self.assertEqual(set(voci), {"it", "en", "zh"}, chiave)
            for lingua in ("en", "zh"):
                self.assertEqual(campi(voci[lingua]), campi(voci["it"]), f"{chiave}/{lingua}")

    def test_ogni_profilo_ha_la_traduzione(self) -> None:
        originali = spec._ORIGINALI[4]
        for lingua in ("en", "zh"):
            self.assertEqual(set(spec._TR_PROFILI[lingua]), set(originali), lingua)

    def test_ogni_flag_vietato_ha_il_motivo_tradotto(self) -> None:
        motivi = set(spec._ORIGINALI[5].values())
        for lingua in ("en", "zh"):
            self.assertEqual(motivi - set(spec._TR_VIETATI[lingua]), set(), lingua)

    # -- output --------------------------------------------------------------

    def test_profili_in_tre_lingue(self) -> None:
        for lingua, parola in (("it", "rumore"), ("en", "noise"), ("zh", "噪声")):
            rc, testo = self._esegui("--lang", lingua, "profili")
            self.assertEqual(rc, 0, lingua)
            self.assertIn(parola, testo, lingua)

    def test_motivo_di_scope_tradotto(self) -> None:
        attesi = (
            ("it", "hostname non presente tra gli inclusi"),
            ("en", "hostname not among the included ones"),
            ("zh", "主机名不在包含列表中"),
        )
        for lingua, frase in attesi:
            rc, testo = self._esegui("--lang", lingua, "verifica", "altro.invalid", "--scope", str(self.scope))
            self.assertEqual(rc, 3, lingua)
            self.assertIn(frase, testo, lingua)

    def test_flag_vietato_tradotto(self) -> None:
        vietato = spec.ESEMPI_VIETATI[0]
        profilo = next(iter(spec.PROFILI))
        attesi = (("it", "non è ammesso"), ("en", "is not allowed"), ("zh", "不被允许"))
        for lingua, frase in attesi:
            argv = ["--lang", lingua, "lancia", profilo, "example.org", "--scope", str(self.scope), "--", *vietato]
            rc, testo = self._esegui(*argv)
            self.assertEqual(rc, 2, lingua)
            self.assertIn(frase, testo, lingua)

    def test_help_tradotto_anche_nelle_parti_di_argparse(self) -> None:
        for lingua, parola in (("it", "opzioni"), ("en", "options"), ("zh", "选项")):
            rc, testo = self._esegui("--lang", lingua, "--help")
            self.assertEqual(rc, 0, lingua)
            self.assertIn(parola, testo, lingua)

    def test_modello_di_scope_nella_lingua_scelta(self) -> None:
        attesi = (("it", "Compilalo a mano"), ("en", "Fill it in by hand"), ("zh", "手工填写"))
        for lingua, frase in attesi:
            nuovo = Path(self.dir.name) / f"scope-{lingua}.toml"
            rc, _ = self._esegui("--lang", lingua, "init", str(nuovo))
            self.assertEqual(rc, 0, lingua)
            testo = nuovo.read_text()
            self.assertIn(frase, testo, lingua)
            self.assertIn("[engagement]", testo, lingua)
            self.assertIn("autorizzato_da =", testo, lingua)

    def test_si_torna_all_italiano(self) -> None:
        nome = next(iter(spec.PROFILI))
        italiano = spec._ORIGINALI[4][nome].descrizione
        self._esegui("--lang", "en", "profili")
        self.assertNotEqual(spec.PROFILI[nome].descrizione, italiano)
        self._esegui("profili")
        self.assertEqual(spec.PROFILI[nome].descrizione, italiano)


if __name__ == "__main__":
    unittest.main()
