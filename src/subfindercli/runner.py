"""Costruzione ed esecuzione del comando. Mai una shell: solo liste di argomenti."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from subfindercli import i18n, spec
from subfindercli.errors import BinarioAssente
from subfindercli.profili import Profilo
from subfindercli.scope import origine

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def trova() -> str:
    # Alcuni tool hanno nomi diversi a seconda della distro: su Kali httpx è 'httpx-toolkit'.
    alt: tuple[str, ...] = getattr(spec, "BINARI_ALT", ())
    for nome in (spec.BINARIO, *alt):
        percorso = shutil.which(nome)
        if percorso:
            return percorso
    raise BinarioAssente(i18n.t("run_non_trovato", bin=spec.BINARIO, inst=spec.INSTALLAZIONE))


def _testo_versione(binario: str) -> str:
    """Output completo di --version, senza colori. I tool ProjectDiscovery scrivono su stderr."""
    try:
        r = subprocess.run(
            [binario, *spec.VERSIONE], capture_output=True, text=True, timeout=15, check=False,
            stdin=subprocess.DEVNULL,
        )  # fmt: skip
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return _ANSI.sub("", r.stdout + "\n" + r.stderr)


def versione(binario: str) -> str:
    """La riga della versione: prima quella che contiene il testo di riconoscimento (dopo il banner), poi la prima."""
    righe = [r.strip() for r in _testo_versione(binario).splitlines() if r.strip()]
    for r in righe:
        if spec.RICONOSCI in r.lower():
            return r
    return righe[0] if righe else ""


def verifica_identita(binario: str) -> None:
    """Controlla che il binario sia davvero subfinder: a volte nel PATH c'è un programma omonimo."""
    if spec.RICONOSCI not in _testo_versione(binario).lower():
        raise BinarioAssente(
            i18n.t(
                "run_non_sembra",
                binario=binario,
                nome=spec.NOME,
                cmd=f"{spec.BINARIO} {' '.join(spec.VERSIONE)}",
                ric=spec.RICONOSCI,
                inst=spec.INSTALLAZIONE,
            )
        )


@dataclass(frozen=True)
class Comando:
    argv: tuple[str, ...]
    risultati: Path


def costruisci(
    binario: str,
    profilo: Profilo,
    target: list[str],
    extra: list[str],
    cartella: Path,
    wordlist: str = "",
) -> list[Comando]:
    if spec.PASSA[0] == "uno":
        # un comando per target (ffuf lavora su un URL alla volta)
        cmds = []
        for i, t in enumerate(target, start=1):
            url = profilo.modello.replace("{origine}", origine(t))
            out = cartella / f"risultati-{i}.json"
            argv = (
                binario, "-u", url, "-w", wordlist or profilo.wordlist,
                *profilo.args, *extra, *spec.UNO_EXTRA, spec.USCITA, str(out),
            )  # fmt: skip
            cmds.append(Comando(argv, out))
        return cmds
    file_target = cartella / "target.txt"
    out = cartella / f"risultati.{profilo.uscita}"
    argv = (binario, *profilo.args, *extra, spec.PASSA[1], str(file_target), spec.USCITA, str(out))
    return [Comando(argv, out)]


def esegui(cmds: list[Comando], target: list[str], cartella: Path) -> int:
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / "target.txt").write_text("\n".join(target) + "\n")
    for c in cmds:
        # stdin chiuso: httpx, naabu e altri leggono i target anche da li', e quelli non passano dallo scope
        rc = subprocess.run(c.argv, check=False, stdin=subprocess.DEVNULL).returncode
        if rc != 0:
            return rc
    return 0
