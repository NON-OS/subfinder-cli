"""Descrizione di subfinder: profili, flag vietati, formato dei risultati."""

from __future__ import annotations

from subfindercli.profili import Profilo
from subfindercli.risultati import Voce, lista, righe_json

NOME = "subfinder"
BINARIO = "subfinder"
DESCRIZIONE = "Enumerazione passiva di sottodomini con scope validato, dry-run di default e audit a catena di hash."
MODO = "dominio"
PASSA = ("file", "-dL")
UNO_EXTRA: tuple[str, ...] = ()  # solo ffuf lavora "un comando per target"
USCITA = "-o"
VERSIONE = ("-version",)
RICONOSCI = "current version"  # testo che il binario vero stampa con {VERSIONE}: distingue da programmi omonimi
INSTALLAZIONE = "Kali/Debian: sudo apt install subfinder. Ovunque con Go: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
SEGRETI: frozenset[str] = frozenset()
GRUPPO = "Fonte"
NOTA_ATTIVITA = (
    "enumerazione passiva: interroga fonti pubbliche, non contatta i target. "
    "I risultati possono comunque uscire dallo scope: filtrali con 'filtra' prima di passarli ad altri tool."
)

PROFILI = {
    p.nome: p
    for p in (
        Profilo(
            "base",
            "Solo fonti gratuite, output pulito.",
            ("-silent",),
            "basso",
            "Primo giro per vedere se il dominio ha sottodomini evidenti.",
        ),
        Profilo(
            "completo",
            "Tutte le fonti disponibili.",
            ("-all", "-silent"),
            "basso",
            "Quando il profilo base non basta. Più fonti = più tempo, e servono le chiavi API per le migliori.",
        ),
        Profilo(
            "ricorsivo",
            "Tutte le fonti, anche sui sottodomini trovati.",
            ("-all", "-recursive", "-silent"),
            "basso",
            "Per domini con molti livelli (a.b.c.dominio). Allunga molto i tempi.",
        ),
        Profilo(
            "sorgenti",
            "Come completo, ma in JSON con la fonte di ogni risultato.",
            ("-all", "-oJ", "-cs"),
            "basso",
            "Per capire quale fonte ha trovato cosa, e valutare quali chiavi API valgono la pena.",
            uscita="jsonl",
        ),
        Profilo(
            "prudente",
            "Ricorsivo con limite di richieste e di tempo.",
            ("-all", "-recursive", "-rl", "10", "-timeout", "30", "-max-time", "5", "-silent"),
            "basso",
            "Quando le fonti ti limitano o vuoi un lancio che finisca in tempi certi (5 minuti).",
        ),
    )
}

VIETATI = {
    "d": "i domini arrivano dal file validato contro lo scope",
    "domain": "i domini arrivano dal file validato contro lo scope",
    "dl": "i domini arrivano dal file validato contro lo scope",
    "list": "i domini arrivano dal file validato contro lo scope",
    "o": "l'output lo gestisce subfinder-cli",
    "output": "l'output lo gestisce subfinder-cli",
    "od": "l'output lo gestisce subfinder-cli",
    "output-dir": "l'output lo gestisce subfinder-cli",
    "up": "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato",
    "update": "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato",
}

ESEMPI_VIETATI = [["-d", "x.example.org"], ["-dL", "lista.txt"], ["-o", "x"], ["--domain=x"], ["-up"]]
ESEMPI_AMMESSI = [["-all"], ["-timeout", "30"], ["-rl", "5"]]


def voci(testo: str) -> list[Voce]:
    out = []
    for r in righe_json(testo):
        if isinstance(r, dict):
            host = str(r.get("host", "")).lower()
            fonti = lista(r.get("sources") or r.get("source"))  # "sources" nelle versioni recenti
            gruppo = str(fonti[0]) if fonti else ""
            if host:
                out.append(Voce(host, host, gruppo))
        else:
            host = r.split()[0].lower()
            out.append(Voce(host, host))
    return out


# -- lingua -------------------------------------------------------------------
# Testi tradotti, generati da l10n/. L'italiano resta quello definito sopra.
_TR_TESTI: dict[str, dict[str, str]] = {
    "en": {
        "descrizione": "Passive subdomain enumeration with a validated scope, dry-run by default and a hash-chained audit.",
        "nota_attivita": "passive enumeration: it queries public sources and does not contact the targets. The results can still fall outside the scope: filter them with 'filtra' before passing them to other tools.",
        "installazione": "Kali/Debian: sudo apt install subfinder. Anywhere with Go: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "gruppo": "Source",
    },
    "zh": {
        "descrizione": "被动子域名枚举，带作用域校验、默认 dry-run 以及哈希链审计。",
        "nota_attivita": "被动枚举：查询公开数据源，不接触目标。结果仍可能落在作用域之外：在传给其他工具之前，先用 'filtra' 过滤。",
        "installazione": "Kali/Debian：sudo apt install subfinder。任何装了 Go 的环境：go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
        "gruppo": "来源",
    },
}
_TR_PROFILI: dict[str, dict[str, list[str]]] = {
    "en": {
        "base": ["Free sources only, clean output.", "First pass to see if the domain has any obvious subdomains."],
        "completo": [
            "All available sources.",
            "When the base profile isn't enough. More sources means more time, and the best ones need API keys.",
        ],
        "ricorsivo": [
            "All sources, including on the subdomains it finds.",
            "For domains with many levels (a.b.c.domain). Adds a lot of runtime.",
        ],
        "sorgenti": [
            "Like completo, but in JSON with the source of each result.",
            "To see which source found what, and judge which API keys are worth it.",
        ],
        "prudente": [
            "Recursive, with request and time limits.",
            "When sources are rate-limiting you or you want a run that finishes within a fixed window (5 minutes).",
        ],
    },
    "zh": {
        "base": ["仅使用免费数据源，输出干净。", "第一轮侦察，查看域名是否有明显的子域名。"],
        "completo": [
            "使用所有可用的数据源。",
            "当 base 配置不够用时使用。数据源越多耗时越长，最好的数据源还需要 API 密钥。",
        ],
        "ricorsivo": ["使用所有数据源，并对找到的子域名继续递归。", "用于多级域名（a.b.c.域名）。会大幅增加耗时。"],
        "sorgenti": [
            "与 completo 相同，但以 JSON 输出，并标注每条结果的来源。",
            "用于了解哪个数据源发现了什么，并评估哪些 API 密钥值得投入。",
        ],
        "prudente": [
            "递归，但带请求数和时间限制。",
            "当数据源对你有速率限制，或你希望一次任务在确定的时间内（5 分钟）完成时使用。",
        ],
    },
}
_TR_VIETATI: dict[str, dict[str, str]] = {
    "en": {
        "i domini arrivano dal file validato contro lo scope": "domains come from the file validated against the scope",
        "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato": "updating the program is done separately, not inside an authorized run",
        "l'output lo gestisce subfinder-cli": "output is handled by subfinder-cli",
    },
    "zh": {
        "i domini arrivano dal file validato contro lo scope": "域名来自经过作用域校验的文件",
        "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato": "程序更新应单独进行，而不是在一次授权任务中进行",
        "l'output lo gestisce subfinder-cli": "输出由 subfinder-cli 管理",
    },
}
_ORIGINALI = (DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI)


def applica_lingua(lingua: str) -> None:
    """Passa testi, profili e motivi dei flag vietati alla lingua scelta. Ripartendo
    sempre dagli originali italiani, chiamarla più volte non accumula niente."""
    global DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI
    from dataclasses import replace

    DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI = _ORIGINALI
    testi = _TR_TESTI.get(lingua)
    if not testi:
        return
    DESCRIZIONE = testi["descrizione"] or DESCRIZIONE
    NOTA_ATTIVITA = testi["nota_attivita"] or NOTA_ATTIVITA
    INSTALLAZIONE = testi["installazione"] or INSTALLAZIONE
    GRUPPO = testi["gruppo"] or GRUPPO
    prof = _TR_PROFILI.get(lingua, {})
    PROFILI = {
        n: replace(p, descrizione=prof[n][0] or p.descrizione, quando=prof[n][1] or p.quando) if n in prof else p
        for n, p in PROFILI.items()
    }
    viet = _TR_VIETATI.get(lingua, {})
    VIETATI = {k: viet.get(v, v) for k, v in VIETATI.items()}
