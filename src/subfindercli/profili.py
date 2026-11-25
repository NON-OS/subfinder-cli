"""Struttura dei profili e filtro sugli argomenti passati a mano."""

from __future__ import annotations

from dataclasses import dataclass

from subfindercli import i18n
from subfindercli.errors import ArgomentoVietato


@dataclass(frozen=True)
class Profilo:
    nome: str
    descrizione: str
    args: tuple[str, ...]
    rumore: str  # "basso" | "medio" | "alto"
    quando: str
    richiede_root: bool = False
    uscita: str = "txt"  # estensione del file di risultati: txt, jsonl, json
    modello: str = ""  # solo per i tool che costruiscono l'URL (ffuf): "{origine}/FUZZ"
    wordlist: str = ""  # wordlist di default del profilo (ffuf)


def nome_flag(tok: str) -> str | None:
    """ "-oJ", "--oJ=x" -> "oj". None se non è un flag. Il confronto è senza maiuscole: nel dubbio si vieta."""
    if not tok.startswith("-") or tok.strip("-") == "":
        return None
    return tok.lstrip("-").split("=", 1)[0].lower()


def filtra_extra(extra: list[str], vietati: dict[str, str]) -> list[str]:
    """Rifiuta i flag vietati. Non è una sandbox: vedi docs/06-architettura.md."""
    for tok in extra:
        nome = nome_flag(tok)
        if nome is not None and nome in vietati:
            raise ArgomentoVietato(i18n.t("pr_vietato", flag=tok.split("=", 1)[0], motivo=vietati[nome]))
    return extra
