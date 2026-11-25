# Profili e flag vietati

🌐 **Italiano** · [English](en/04-profili.md) · [中文](zh/04-profili.md)

| Profilo | Cosa fa | Rumore | Root |
|---|---|---|---|
| `base` | Solo fonti gratuite, output pulito. | basso | no |
| `completo` | Tutte le fonti disponibili. | basso | no |
| `ricorsivo` | Tutte le fonti, anche sui sottodomini trovati. | basso | no |
| `sorgenti` | Come completo, ma in JSON con la fonte di ogni risultato. | basso | no |
| `prudente` | Ricorsivo con limite di richieste e di tempo. | basso | no |

`subfinder-cli profili` stampa i flag esatti di ciascuno.

## Cosa fa ciascun profilo

**base** (`-silent`). Solo fonti gratuite, output pulito. Primo giro per vedere se il dominio ha sottodomini evidenti.

**completo** (`-all -silent`). Tutte le fonti disponibili. Quando il profilo base non basta. Più fonti = più tempo, e servono le chiavi API per le migliori.

**ricorsivo** (`-all -recursive -silent`). Tutte le fonti, anche sui sottodomini trovati. Per domini con molti livelli (a.b.c.dominio). Allunga molto i tempi.

**sorgenti** (`-all -oJ -cs`). Come completo, ma in JSON con la fonte di ogni risultato. Per capire quale fonte ha trovato cosa, e valutare quali chiavi API valgono la pena.

**prudente** (`-all -recursive -rl 10 -timeout 30 -max-time 5 -silent`). Ricorsivo con limite di richieste e di tempo. Quando le fonti ti limitano o vuoi un lancio che finisca in tempi certi (5 minuti).

## Passare flag a mano

Tutto ciò che scrivi dopo `--` finisce a subfinder, dopo i flag del profilo, a patto che non sia nell'elenco dei vietati. Il confronto non distingue maiuscole e minuscole e accetta sia `-flag valore` sia `-flag=valore`, con uno o due trattini.

```sh
subfinder-cli lancia completo example.org --scope scope.toml -- -timeout 5
```

## Elenco dei vietati

| Flag | Perché |
|---|---|
| `-d`, `-domain`, `-dl`, `-list` | i domini arrivano dal file validato contro lo scope |
| `-o`, `-output`, `-od`, `-output-dir` | l'output lo gestisce subfinder-cli |
| `-up`, `-update` | l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato |

## Quello che il filtro non fa

Non è una sandbox. Se vuoi aggirarlo ci riesci, per esempio chiamando `subfinder` direttamente. Serve a fermare gli errori e le abitudini sbagliate, non un malintenzionato che ha già accesso al tuo terminale. Se ti serve un flag vietato per un'attività concordata con il cliente, usa subfinder direttamente e annota la scelta nell'ingaggio.
