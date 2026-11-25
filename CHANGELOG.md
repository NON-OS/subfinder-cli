# Changelog

Il formato segue [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/). Le versioni seguono [SemVer](https://semver.org/lang/it/).

## [Non rilasciato]

- `runner`: supporta nomi di binario alternativi per distro (infrastruttura; usata da httpx-toolkit su Kali).

- Comando `guida`: modalità interattiva passo per passo (scope → profilo → target → anteprima → conferma), riusa lo stesso percorso di `lancia`.
- Logo NONOS allo startup (su stderr, non inquina mai stdout di `rapporto`/`filtra`).
- Istruzioni di installazione per Kali/Debian (`apt install subfinder`) oltre a Go/macOS. README con posizionamento Kali/Parrot/Linux primario.

## [0.2.0] - 2026-11-23

- Scope firmato con chiavi SSH: `scope-firma`, `scope-verifica`, `--firmatari`. Firmatario e impronta nell'audit.
- Provato con subfinder v2.17.0: flag dei profili e dei vietati confrontati con l'help vero. Aggiunti i flag pericolosi trovati.
- Lo stdin del processo figlio è chiuso.
- `doctor` e `--esegui` controllano che il binario nel PATH sia davvero subfinder.
- Parser corretti con output reali, conservati in `tests/fixtures/`.
- `mypy --strict` non trova errori in `src/`; è un job della CI.
- Copertura dei test misurata con `coverage`: la CI fallisce sotto l'85%.
- Le GitHub Action sono ancorate allo SHA del commit, non a un tag mobile; aggiunto `ruff format --check`.
- Pagina `docs/10-compatibilita.md` con ciò che è stato provato e ciò che no.

## [0.1.0]

Prima versione.

- Controllo dello scope da file TOML (dominio), con esclusioni e date di validità.
- Dry-run di default; `--esegui` richiede conferma.
- 5 profili e filtro sui flag vietati.
- Registro di audit a catena di hash, con i valori dei flag sensibili oscurati.
- Comandi `lancia`, `filtra`, `verifica`, `rapporto`, `confronta`, `profili`, `audit`, `init`, `doctor`.
- Cheatsheet shell originale in `scripts/`.
