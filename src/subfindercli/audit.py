"""Registro di audit append-only a catena di hash.

Ogni riga è un oggetto JSON che contiene l'hash SHA-256 della riga precedente.
Se qualcuno modifica o cancella una riga in mezzo, la catena si spezza e
`verifica` lo dice. Non protegge da chi riscrive il file da capo: per quello
serve firmare o spedire il registro altrove. Vedi docs/05-audit.md.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from subfindercli import i18n

GENESI = "0" * 64


def _canonico(obj: dict[str, object]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _hash(prec: str, corpo: dict[str, object]) -> str:
    return hashlib.sha256(prec.encode() + b"\n" + _canonico(corpo)).hexdigest()


def _ultimo_hash(percorso: Path) -> str:
    if not percorso.exists() or percorso.stat().st_size == 0:
        return GENESI
    # Un registro di audit resta piccolo: leggerlo intero è più semplice
    # e meno fragile di risalire il file byte per byte.
    righe = [r for r in percorso.read_bytes().splitlines() if r.strip()]
    ultima: dict[str, object] = json.loads(righe[-1])
    valore = ultima["hash"]
    assert isinstance(valore, str)
    return valore


def registra(percorso: str | Path, evento: str, **campi: object) -> str:
    """Aggiunge una riga e ritorna il suo hash."""
    p = Path(percorso)
    p.parent.mkdir(parents=True, exist_ok=True)
    corpo = {
        "ts": datetime.now(UTC).isoformat(timespec="seconds"),
        "evento": evento,
        **campi,
    }
    prec = _ultimo_hash(p)
    nuovo_hash = _hash(prec, corpo)
    riga: dict[str, object] = {"prec": prec, "corpo": corpo, "hash": nuovo_hash}
    with p.open("ab") as f:
        f.write(_canonico(riga) + b"\n")
        f.flush()
        os.fsync(f.fileno())
    return nuovo_hash


@dataclass(frozen=True)
class EsitoVerifica:
    valido: bool
    righe: int
    errore: str = ""


def verifica(percorso: str | Path) -> EsitoVerifica:
    p = Path(percorso)
    if not p.exists():
        return EsitoVerifica(False, 0, i18n.t("au_inesistente"))
    prec = GENESI
    n = 0
    with p.open("rb") as f:
        for n, grezza in enumerate(f, start=1):
            try:
                riga = json.loads(grezza)
                corpo, h, p_dichiarato = riga["corpo"], riga["hash"], riga["prec"]
            except (json.JSONDecodeError, KeyError, TypeError):
                return EsitoVerifica(False, n, i18n.t("au_formato", n=n))
            if p_dichiarato != prec:
                return EsitoVerifica(False, n, i18n.t("au_spezzata", n=n))
            if _hash(prec, corpo) != h:
                return EsitoVerifica(False, n, i18n.t("au_alterato", n=n))
            prec = h
    return EsitoVerifica(True, n)


def oscura(argv: list[str], segreti: frozenset[str]) -> list[str]:
    """Copia di argv senza i valori dei flag che possono contenere segreti (token, header)."""
    uscita: list[str] = []
    salta = False
    for tok in argv:
        if salta:
            uscita.append("[oscurato]")
            salta = False
            continue
        if tok.startswith("-"):
            nome, uguale, _ = tok.lstrip("-").partition("=")
            if nome.lower() in segreti:
                if uguale:
                    uscita.append(tok.split("=", 1)[0] + "=[oscurato]")
                else:
                    uscita.append(tok)
                    salta = True
                continue
        uscita.append(tok)
    return uscita
