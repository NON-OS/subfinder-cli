"""Firma e verifica dello scope con le chiavi SSH, tramite ssh-keygen.

Perché: un file di scope è una dichiarazione. Se a firmarlo è chi ha l'autorità di
autorizzare, diventa una prova: il programma si rifiuta di partire con uno scope
modificato dopo la firma, o firmato da una chiave che non conosce. Nessuna dipendenza:
ssh-keygen c'è su macOS e su qualunque Linux con OpenSSH.

La firma è staccata (scope.toml.sig) e vale solo per questo programma: il namespace
della firma è "subfinder-cli", quindi una firma fatta per un altro scopo non è accettata.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from subfindercli import i18n
from subfindercli.errors import ScopeInvalido

NAMESPACE = "subfinder-cli"
_FP = re.compile(r"(SHA256:[A-Za-z0-9+/=]+)")


@dataclass(frozen=True)
class Firmatario:
    identita: str
    impronta: str  # SHA256:... della chiave pubblica che ha firmato


def _ssh_keygen() -> str:
    p = shutil.which("ssh-keygen")
    if not p:
        raise ScopeInvalido(i18n.t("fi_no_keygen"))
    return p


def percorso_firma(scope: str | Path) -> Path:
    return Path(str(scope) + ".sig")


def firma(scope: str | Path, chiave: str | Path) -> Path:
    """Crea scope.toml.sig. Se la chiave ha una passphrase, ssh-keygen la chiede sul terminale."""
    s = Path(scope)
    if not s.is_file():
        raise ScopeInvalido(i18n.t("sc_non_trovato", p=s))
    sig = percorso_firma(s)
    if sig.exists():
        raise ScopeInvalido(i18n.t("fi_sig_esiste", sig=sig))
    r = subprocess.run(
        [_ssh_keygen(), "-Y", "sign", "-f", str(chiave), "-n", NAMESPACE, str(s)],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    if r.returncode != 0 or not sig.exists():
        raise ScopeInvalido(i18n.t("fi_non_riuscita", err=r.stderr.strip() or i18n.t("fi_errore_ignoto")))
    return sig


def verifica(dati: bytes, sig: str | Path, firmatari: str | Path) -> Firmatario:
    """Controlla la firma di `dati` contro il file dei firmatari ammessi (formato allowed_signers).

    Si verifica sugli stessi byte che poi vengono letti come TOML: niente finestra tra
    controllo e uso in cui il file possa cambiare.
    """
    sig, firmatari = Path(sig), Path(firmatari)
    if not sig.is_file():
        raise ScopeInvalido(i18n.t("fi_non_trovata", sig=sig))
    if not firmatari.is_file():
        raise ScopeInvalido(i18n.t("fi_firmatari_nf", f=firmatari))
    kg = _ssh_keygen()

    chi = subprocess.run(
        [kg, "-Y", "find-principals", "-f", str(firmatari), "-s", str(sig)],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    righe = [r.strip() for r in chi.stdout.splitlines() if r.strip()]
    if chi.returncode != 0 or not righe:
        raise ScopeInvalido(i18n.t("fi_nessuno"))

    r = subprocess.run(
        [kg, "-Y", "verify", "-f", str(firmatari), "-I", righe[0], "-n", NAMESPACE, "-s", str(sig)],
        input=dati, capture_output=True, check=False,
    )  # fmt: skip
    if r.returncode != 0:
        raise ScopeInvalido(i18n.t("fi_non_valida"))
    m = _FP.search(r.stdout.decode(errors="replace"))
    return Firmatario(righe[0], m.group(1) if m else "")
