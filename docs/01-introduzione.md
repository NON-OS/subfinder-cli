# Introduzione

🌐 **Italiano** · [English](en/01-introduzione.md) · [中文](zh/01-introduzione.md)

Questo strumento nasce da uno script shell che usavo per ricordarmi i comandi di subfinder: scelte di flag, ordine di lavoro, note su cosa conviene fare e cosa no. Era un appunto eseguibile. Funzionava, ma aveva un difetto: bastava sbagliare una variabile in cima al file e il lancio partiva su qualcosa che non c'entrava.

`subfinder-cli` toglie quel difetto. Lo scope diventa un file con nome, firma di chi autorizza e date di validità. Il target lo scegli a riga di comando e viene confrontato con quel file prima che subfinder venga nemmeno cercato nel `PATH`.

## Tre decisioni di progetto

**Il dry-run è il comportamento normale.** Senza `--esegui` il programma stampa il comando e lo registra. Partire per sbaglio è più difficile che non partire per niente.

**Nel dubbio si rifiuta.** Un target con un formato strano, un URL con credenziali nell'host, un hostname che risolve in un indirizzo escluso: tutto rifiutato. Il costo di un falso rifiuto è dover correggere una riga di scope. Il costo di un falso via libera è un incidente.

**Nessuna dipendenza.** Solo la libreria standard di Python. Uno strumento che deve garantire cosa lancia non dovrebbe portarsi dietro cinquanta pacchetti di cui fidarsi.

## Cosa trovi nel repository

```
subfinder-cli/
├── src/subfindercli/
│   ├── scope.py      carica lo scope e decide se un target è ammesso
│   ├── spec.py       profili, flag vietati e formato dei risultati di subfinder
│   ├── profili.py    struttura dei profili e filtro sui flag
│   ├── runner.py     costruisce il comando e lo lancia (mai una shell)
│   ├── audit.py      registro a catena di hash
│   ├── risultati.py  lettura, riepilogo e confronto dei risultati
│   └── cli.py        argomenti, messaggi, codici di uscita
├── tests/            unittest, senza rete e senza subfinder installato
├── docs/             questa documentazione
├── examples/         scope d'esempio
├── lab/              bersagli volutamente vulnerabili (Docker)
└── scripts/          il cheatsheet shell originale
```

## A chi serve

A chi fa test di sicurezza su incarico e vuole una traccia pulita di cosa ha lanciato, quando e con quale autorizzazione. A chi studia e vuole un'abitudine sana fin dal primo giorno: prima lo scope, poi il comando. A chi ha un team e vuole che nessuno incolli un target preso da una chat in un comando.

## A chi non serve

A chi cerca un modo di agire di nascosto o fuori perimetro. I flag che servono a quello sono vietati.

## Da dove continuare

Se è la prima volta che fai un test di sicurezza, leggi [02-autorizzazione.md](02-autorizzazione.md) prima di ogni altra cosa. Se ti serve solo capire come si scrive lo scope, vai a [03-scope.md](03-scope.md).
