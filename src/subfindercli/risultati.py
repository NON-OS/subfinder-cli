"""Lettura dei risultati, riepilogo e confronto. Il formato lo conosce spec.voci()."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from subfindercli import i18n
from subfindercli.errors import ErroreCli

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


class RisultatiIllegibili(ErroreCli):
    pass


@dataclass(frozen=True)
class Voce:
    chiave: str  # identifica il risultato: serve al confronto
    testo: str  # come lo mostriamo
    gruppo: str = ""  # per il riepilogo: severità, status code, host...


def carica(percorso: str | Path) -> list[Voce]:
    p = Path(percorso)
    if p.is_dir():
        files = sorted(f for f in p.iterdir() if f.name.startswith("risultati") and f.is_file())
        if not files:
            raise RisultatiIllegibili(i18n.t("ri_nessun_file", p=p))
    elif p.is_file():
        files = [p]
    else:
        raise RisultatiIllegibili(i18n.t("ri_non_trovato", p=p))
    from subfindercli import spec  # import tardivo: spec importa questo modulo

    voci: list[Voce] = []
    for f in files:
        # alcuni tool (dnsx) scrivono i colori ANSI anche nei file di output
        voci += spec.voci(_ANSI.sub("", f.read_text(errors="replace")))
    unici = {v.chiave: v for v in voci}  # niente doppioni
    return list(unici.values())


@dataclass
class Riepilogo:
    totale: int
    per_gruppo: dict[str, int]


def riepiloga(voci: list[Voce]) -> Riepilogo:
    c = Counter(v.gruppo for v in voci if v.gruppo)
    return Riepilogo(len(voci), dict(c.most_common()))


def a_testo(voci: list[Voce]) -> str:
    r = riepiloga(voci)
    righe = [i18n.t("ri_totale", n=r.totale)]
    righe += [f"  {g}: {n}" for g, n in r.per_gruppo.items()]
    if voci:
        righe.append("")
        righe += [v.testo for v in sorted(voci, key=lambda v: v.chiave)]
    return "\n".join(righe)


def a_markdown(voci: list[Voce], titolo: str) -> str:
    from subfindercli import spec  # import tardivo: spec importa questo modulo

    r = riepiloga(voci)
    righe = [f"# {titolo}", "", i18n.t("ri_totale_md", n=r.totale), ""]
    if r.per_gruppo:
        righe += ["| " + spec.GRUPPO + " | " + i18n.t("ri_quanti") + " |", "|---|---|"]
        righe += [f"| {g} | {n} |" for g, n in r.per_gruppo.items()]
        righe.append("")
    righe += ["```text"] + [v.testo for v in sorted(voci, key=lambda v: v.chiave)] + ["```"]
    return "\n".join(righe)


def a_json(voci: list[Voce]) -> str:
    return json.dumps(
        {"riepilogo": asdict(riepiloga(voci)), "risultati": [asdict(v) for v in voci]},
        indent=2,
        ensure_ascii=False,
    )


@dataclass
class Differenze:
    nuovi: list[Voce]
    spariti: list[Voce]

    def vuoto(self) -> bool:
        return not (self.nuovi or self.spariti)


def confronta(vecchi: list[Voce], nuovi: list[Voce]) -> Differenze:
    a = {v.chiave: v for v in vecchi}
    b = {v.chiave: v for v in nuovi}
    return Differenze(
        nuovi=[b[k] for k in sorted(b.keys() - a.keys())],
        spariti=[a[k] for k in sorted(a.keys() - b.keys())],
    )


def differenze_a_testo(d: Differenze) -> str:
    if d.vuoto():
        return i18n.t("ri_nessuna_diff")
    return "\n".join([f"+ {v.testo}" for v in d.nuovi] + [f"- {v.testo}" for v in d.spariti])


def sotto_dict(v: object) -> dict[str, object]:
    """v.get(chiave) su un dict[str, object] torna 'object': qui lo si restringe, o si prende {}."""
    return v if isinstance(v, dict) else {}


def lista(v: object) -> list[object]:
    """Come sotto_dict, ma per i campi che possono essere una lista (es. le fonti di un host)."""
    return v if isinstance(v, list) else []


def righe_json(testo: str) -> list[dict[str, object] | str]:
    """Ogni riga non vuota: un dict se è JSON, altrimenti la stringa così com'è."""
    out: list[dict[str, object] | str] = []
    for riga in testo.splitlines():
        riga = riga.strip()
        if not riga:
            continue
        if riga.startswith("{"):
            try:
                oggetto = json.loads(riga)
            except json.JSONDecodeError:
                out.append(riga)
                continue
            if isinstance(oggetto, dict):
                out.append(oggetto)
                continue
        out.append(riga)
    return out
