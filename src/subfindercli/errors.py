"""Codici di uscita e eccezioni. I codici sono parte del contratto con gli script che ci stanno sopra."""

from __future__ import annotations

OK = 0
USO = 2  # argomenti sbagliati
FUORI_SCOPE = 3  # almeno un target non è nello scope
SCOPE_INVALIDO = 4  # file scope illeggibile, malformato o scaduto
BINARIO_ASSENTE = 5
RIFIUTATO = 6  # esecuzione richiesta ma conferma mancante
FALLITO = 7  # nmap è partito ed è uscito con errore


class ErroreCli(Exception):
    exit_code = USO


class ScopeInvalido(ErroreCli):
    exit_code = SCOPE_INVALIDO


class FuoriScope(ErroreCli):
    exit_code = FUORI_SCOPE


class BinarioAssente(ErroreCli):
    exit_code = BINARIO_ASSENTE


class Rifiutato(ErroreCli):
    exit_code = RIFIUTATO


class ArgomentoVietato(ErroreCli):
    exit_code = USO
