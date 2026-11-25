"""Lettura del file di scope e verifica dei target.

La regola di fondo: un target è ammesso solo se lo scope lo nomina in modo
esplicito. Nel dubbio si rifiuta. Gli hostname non vengono mai risolti per
"allargare" lo scope, solo per scoprire se finiscono dentro un'esclusione.
"""

from __future__ import annotations

import ipaddress
import re
import socket
import tomllib
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from subfindercli import i18n
from subfindercli.errors import FuoriScope, ScopeInvalido

Rete = ipaddress.IPv4Network | ipaddress.IPv6Network

_LABEL = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)$")

Resolver = Callable[[str], list[str]]


def _risolvi_di_sistema(host: str) -> list[str]:
    try:
        info = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return []
    return sorted({str(i[4][0]) for i in info})


@dataclass(frozen=True)
class Verdetto:
    target: str
    ammesso: bool
    motivo: str
    risolti: tuple[str, ...] = ()


@dataclass
class Scope:
    nome: str
    autorizzato_da: str
    riferimento: str
    valido_dal: date
    valido_fino: date
    reti_incluse: list[Rete] = field(default_factory=list)
    reti_escluse: list[Rete] = field(default_factory=list)
    host_inclusi: list[str] = field(default_factory=list)
    host_esclusi: list[str] = field(default_factory=list)

    # -- validità temporale -------------------------------------------------

    def verifica_validita(self, oggi: date | None = None) -> None:
        oggi = oggi or date.today()
        if oggi < self.valido_dal:
            raise ScopeInvalido(i18n.t("sc_non_ancora", nome=self.nome, dal=self.valido_dal, oggi=oggi))
        if oggi > self.valido_fino:
            raise ScopeInvalido(i18n.t("sc_scaduto", nome=self.nome, fino=self.valido_fino, oggi=oggi))

    # -- verifica dei target -------------------------------------------------

    def controlla(self, target: str, resolver: Resolver = _risolvi_di_sistema, modo: str = "host") -> Verdetto:
        """modo: "host" (IP, CIDR, hostname), "dominio" (solo hostname), "url" (URL, host:port, host)."""
        grezzo = target.strip()
        if not grezzo:
            return Verdetto(target, False, i18n.t("sc_vuoto"))
        if grezzo.startswith("-"):
            return Verdetto(target, False, i18n.t("sc_flag"))
        if modo == "url":
            return self._controlla_url(target, grezzo, resolver)
        if modo == "dominio":
            if _come_rete(grezzo) is not None:
                return Verdetto(target, False, i18n.t("sc_dominio_no_ip"))
            nome = _normalizza_host(grezzo)
            if nome is None:
                return Verdetto(target, False, i18n.t("sc_dominio_valido"))
            return self._controlla_host(grezzo, nome, resolver)

        rete = _come_rete(grezzo)
        if rete is not None:
            return self._controlla_rete(grezzo, rete)

        nome = _normalizza_host(grezzo)
        if nome is None:
            return Verdetto(
                target,
                False,
                i18n.t("sc_formato"),
            )
        return self._controlla_host(grezzo, nome, resolver)

    def _controlla_url(self, target: str, grezzo: str, resolver: Resolver) -> Verdetto:
        if "://" not in grezzo:
            # "10.0.0.0/24" per urlsplit è l'host 10.0.0.0 con percorso /24, ma i tool Go lo
            # espandono come CIDR e colpiscono 254 host: il controllo guarderebbe l'host sbagliato.
            testa, _, coda = grezzo.partition("/")
            if coda.isdigit():
                try:
                    ipaddress.ip_address(testa)
                except ValueError:
                    pass
                else:
                    return Verdetto(target, False, i18n.t("sc_cidr_url"))
        host, errore = estrai_host(grezzo)
        if host is None:
            return Verdetto(target, False, errore)
        v = self.controlla(host, resolver, modo="host")
        return Verdetto(target, v.ammesso, i18n.t("sc_host", host=host, motivo=v.motivo), v.risolti)

    def _controlla_rete(self, target: str, rete: Rete) -> Verdetto:
        for esclusa in self.reti_escluse:
            if rete.version == esclusa.version and rete.overlaps(esclusa):
                return Verdetto(target, False, i18n.t("sc_sovrappone", esclusa=esclusa))
        for inclusa in self.reti_incluse:
            if self._stessa_famiglia_e_contenuta(rete, inclusa):
                return Verdetto(target, True, i18n.t("sc_dentro", inclusa=inclusa))
        return Verdetto(target, False, i18n.t("sc_non_in_rete"))

    @staticmethod
    def _stessa_famiglia_e_contenuta(rete: Rete, inclusa: Rete) -> bool:
        # subnet_of richiede che le due reti siano della stessa versione IP: il controllo
        # di self.version sopra lo garantisce a runtime, ma non basta a mypy per restringere
        # il tipo dell'unione, quindi lo facciamo esplicitamente qui.
        if isinstance(rete, ipaddress.IPv4Network) and isinstance(inclusa, ipaddress.IPv4Network):
            return rete.subnet_of(inclusa)
        if isinstance(rete, ipaddress.IPv6Network) and isinstance(inclusa, ipaddress.IPv6Network):
            return rete.subnet_of(inclusa)
        return False

    def _controlla_host(self, target: str, nome: str, resolver: Resolver) -> Verdetto:
        if any(_host_combacia(nome, p) for p in self.host_esclusi):
            return Verdetto(target, False, i18n.t("sc_host_escluso"))

        risolti = tuple(resolver(nome)) if self.reti_escluse else ()
        for ip in risolti:
            addr = ipaddress.ip_address(ip)
            for esclusa in self.reti_escluse:
                if addr.version == esclusa.version and addr in esclusa:
                    return Verdetto(target, False, i18n.t("sc_risolve_escl", ip=ip, esclusa=esclusa), risolti)

        for modello in self.host_inclusi:
            if _host_combacia(nome, modello):
                return Verdetto(target, True, i18n.t("sc_combacia", modello=modello), risolti)
        return Verdetto(target, False, i18n.t("sc_host_non_incl"), risolti)

    def richiedi(
        self, target: Iterable[str], resolver: Resolver = _risolvi_di_sistema, modo: str = "host"
    ) -> list[Verdetto]:
        """Valida tutti i target. Se anche uno solo è fuori scope, non parte niente."""
        esiti = [self.controlla(t, resolver, modo) for t in target]
        fuori = [e for e in esiti if not e.ammesso]
        if fuori:
            righe = "\n".join(f"  {e.target}: {e.motivo}" for e in fuori)
            raise FuoriScope(i18n.t("sc_fuori", righe=righe))
        return esiti


# -- helper ---------------------------------------------------------------


def estrai_host(testo: str) -> tuple[str | None, str]:
    """Ricava l'host da "https://host:8443/x", "host:8443" o "host". Rifiuta i trucchi sull'URL."""
    if any(c in testo for c in " \t\\@"):
        return None, i18n.t("sc_url_trucchi")
    try:
        if "://" in testo:
            parti = urlsplit(testo)
            if parti.scheme not in ("http", "https"):
                return None, i18n.t("sc_url_schema", scheme=parti.scheme)
        else:
            parti = urlsplit("//" + testo)
        host = parti.hostname
        parti.port  # noqa: B018  (solleva ValueError se la porta è fuori intervallo)
    except ValueError:
        return None, i18n.t("sc_url_malformato")
    if not host:
        return None, i18n.t("sc_url_no_host")
    return host, ""


def origine(testo: str) -> str:
    """ "host:8443/x" -> "https://host:8443". Se manca lo schema si assume https."""
    if "://" in testo:
        p = urlsplit(testo)
        return f"{p.scheme}://{p.netloc}"
    return "https://" + testo.split("/", 1)[0]


def _come_rete(testo: str) -> Rete | None:
    # strict=True: "10.0.0.5/24" con bit d'host accesi viene rifiutato.
    # Nmap lo accetta e scansiona l'intera /24: troppo ambiguo per uno strumento di scope.
    try:
        return ipaddress.ip_network(testo, strict=True)
    except ValueError:
        return None


def _normalizza_host(testo: str) -> str | None:
    nome = testo.lower().rstrip(".")
    if not nome or len(nome) > 253:
        return None
    if any(c in nome for c in "/:*?\\ "):
        return None
    return nome if all(_LABEL.match(parte) for parte in nome.split(".")) else None


def _host_combacia(nome: str, modello: str) -> bool:
    if modello.startswith("*."):
        return nome.endswith("." + modello[2:])
    return nome == modello


# -- caricamento ----------------------------------------------------------


def _data(valore: object, chiave: str) -> date:
    if isinstance(valore, date):
        return valore
    raise ScopeInvalido(i18n.t("sc_data_toml", chiave=chiave))


def _stringa(sezione: dict[str, object], chiave: str) -> str:
    v = sezione.get(chiave)
    if not isinstance(v, str) or not v.strip():
        raise ScopeInvalido(i18n.t("sc_campo_mancante", chiave=chiave))
    return v.strip()


def carica(percorso: str | Path, grezzo: bytes | None = None) -> Scope:
    """Legge lo scope. Se passi i byte già letti (per averli verificati con la firma) usa quelli."""
    p = Path(percorso)
    try:
        dati = tomllib.loads((grezzo if grezzo is not None else p.read_bytes()).decode("utf-8"))
    except FileNotFoundError:
        raise ScopeInvalido(i18n.t("sc_non_trovato", p=p)) from None
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        raise ScopeInvalido(i18n.t("sc_toml", p=p, e=e)) from None

    eng = dati.get("engagement")
    sco = dati.get("scope")
    if not isinstance(eng, dict) or not isinstance(sco, dict):
        raise ScopeInvalido(i18n.t("sc_sezioni"))

    scope = Scope(
        nome=_stringa(eng, "nome"),
        autorizzato_da=_stringa(eng, "autorizzato_da"),
        riferimento=_stringa(eng, "riferimento"),
        valido_dal=_data(eng.get("valido_dal"), "engagement.valido_dal"),
        valido_fino=_data(eng.get("valido_fino"), "engagement.valido_fino"),
    )
    if scope.valido_fino < scope.valido_dal:
        raise ScopeInvalido(i18n.t("sc_date_invertite"))

    _riempi(scope, sco.get("include"), incluso=True)
    _riempi(scope, sco.get("esclude", []), incluso=False)
    if not scope.reti_incluse and not scope.host_inclusi:
        raise ScopeInvalido(i18n.t("sc_include_vuoto"))
    return scope


def _riempi(scope: Scope, voci: object, *, incluso: bool) -> None:
    campo = "include" if incluso else "esclude"
    if not isinstance(voci, list) or not all(isinstance(v, str) for v in voci):
        raise ScopeInvalido(i18n.t("sc_campo_lista", campo=campo))
    for voce in voci:
        voce = voce.strip()
        try:
            rete = ipaddress.ip_network(voce, strict=True)
        except ValueError:
            rete = None
        if rete is not None:
            if incluso and rete.prefixlen == 0:
                raise ScopeInvalido(i18n.t("sc_tutto_internet", voce=voce))
            (scope.reti_incluse if incluso else scope.reti_escluse).append(rete)
            continue
        modello = voce.lower().rstrip(".")
        base = modello[2:] if modello.startswith("*.") else modello
        if _normalizza_host(base) is None:
            raise ScopeInvalido(i18n.t("sc_voce_non_valida", campo=campo, voce=repr(voce)))
        if incluso and modello.startswith("*.") and "." not in base:
            raise ScopeInvalido(i18n.t("sc_wildcard_tld", voce=voce))
        (scope.host_inclusi if incluso else scope.host_esclusi).append(modello)
