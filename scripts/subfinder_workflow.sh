#!/usr/bin/env bash
# subfinder_workflow_v2.sh
# Riferimento operativo completo. Solo target autorizzati.
# Le note spiegano il perché e il quando, non solo il cosa.

DOMAIN="<DOMINIO_TARGET>"
DOMAINS_FILE="<FILE_CON_LISTA_DOMINI>"
OUT="<PREFISSO_OUTPUT>"

# ---------------------------------------------------------------
# Prerequisiti e configurazione
# subfinder funziona subito con le fonti gratuite, ma le fonti
# più potenti (Shodan, Censys, VirusTotal) richiedono API key
# nel file ~/.config/subfinder/provider-config.yaml.
# Senza chiavi, subfinder NON dà errore: salta silenziosamente
# quelle fonti. Se i risultati sono pochi, il primo sospetto
# è la configurazione, non il target.
# ---------------------------------------------------------------
subfinder -version
subfinder -ls  # elenca tutte le fonti disponibili

# ---------------------------------------------------------------
# Enumerazione base (passiva, fonti gratuite)
# Veloce, ma copertura limitata. Punto di partenza per capire
# se il dominio ha sottodomini evidenti.
# ---------------------------------------------------------------
subfinder -d "$DOMAIN" -silent -o "$OUT.base.txt"

# ---------------------------------------------------------------
# Enumerazione ampia (-all)
# Usa tutte le fonti disponibili, incluse quelle con API key.
# La documentazione ufficiale lo marca esplicitamente come "slow".
# È il flag da usare quando la copertura conta più della velocità.
# ---------------------------------------------------------------
subfinder -d "$DOMAIN" -all -silent -o "$OUT.all.txt"

# ---------------------------------------------------------------
# Enumerazione ricorsiva (-recursive): cosa fa DAVVERO
# La documentazione ufficiale è chiara: -recursive NON significa
# "cerca sottodomini di sottodomini". Significa "usa SOLO le fonti
# che possono gestire sottodomini ricorsivi (es. subdomain.domain.tld
# vs domain.tld)".
# Quindi non espande la ricerca di per sé: restringe il set di fonti
# a quelle capaci di gestire input ricorsivi. Va usato insieme a -all
# per avere senso operativo.
# ---------------------------------------------------------------
subfinder -d "$DOMAIN" -all -recursive -silent -o "$OUT.recursive.txt"

# ---------------------------------------------------------------
# Filtri: match e filter
# -m tiene solo i sottodomini che matchano il pattern.
# -f esclude quelli che matchano.
# Utile per isolare ambienti specifici o escludere domini fuori scope.
# ---------------------------------------------------------------

# Solo ambienti di sviluppo/staging.
subfinder -d "$DOMAIN" -all -m "dev,staging,test" -silent -o "$OUT.dev.txt"

# Escludi domini fuori scope.
subfinder -d "$DOMAIN" -all -f "blog,support,help" -silent -o "$OUT.scoped.txt"

# ---------------------------------------------------------------
# Active subdomains only (-nW)
# La documentazione ufficiale descrive -nW come "display active
# subdomains only". In pratica rimuove i sottodomini
# che non risolvono (wildcard & dead subdomains) direttamente
# in fase di enumerazione, senza passare per dnsx.
# Utile quando vuoi un filtro rapido e non hai bisogno di
# risoluzione DNS dettagliata.
# ---------------------------------------------------------------
subfinder -d "$DOMAIN" -all -nW -silent -o "$OUT.active.txt"

# ---------------------------------------------------------------
# Rate limiting
# -rl: richieste al secondo globali.
# -rls: rate limit per singola fonte, formato key=value
#       con unità /s esplicita (es. "hackertarget=10/s,shodan=15/s").
# -timeout: secondi di attesa prima del timeout (default 30).
# -max-time: minuti totali per l'enumerazione (default 10).
#
# Le fonti gratuite hanno rate limit stretti. Se vedi 429,
# abbassa -rl e applica -rls per fonte specifica.
# ---------------------------------------------------------------

# Conservativo per evitare ban dalle fonti gratuite.
subfinder -d "$DOMAIN" -all -recursive -rl 10 -timeout 30 -max-time 5 -silent -o "$OUT.safe.txt"

# Rate limit per fonte con formato corretto: provider=rate/s.
subfinder -d "$DOMAIN" -all -rls "hackertarget=10/s,shodan=15/s" -silent -o "$OUT.rls.txt"

# ---------------------------------------------------------------
# Output strutturato
# -oJ produce JSONL.
# -cs include le fonti nell'output, ma FUNZIONA SOLO con -oJ
# (JSONL). Se usi -cs senza -oJ, il flag viene
# ignorato silenziosamente.
# ---------------------------------------------------------------

# JSONL con sorgente attribuita. -cs richiede -oJ, altrimenti
# viene ignorato.
subfinder -d "$DOMAIN" -all -oJ -cs -o "$OUT.sources.jsonl"

# Output semplice per pipeline (solo sottodomini, una riga each).
subfinder -d "$DOMAIN" -all -recursive -silent -o "$OUT.subs.txt"

# ---------------------------------------------------------------
# Multi-dominio (-dL)
# -dL carica una lista di domini da file.
# -oD scrive un file per dominio nella directory specificata.
# ---------------------------------------------------------------
subfinder -dL "$DOMAINS_FILE" -all -recursive -rl 20 -silent -o "$OUT.multi.txt"

# ---------------------------------------------------------------
# Pipeline: subfinder → dnsx (con wildcard filtering) → httpx → nuclei
#
# Il passaggio con dnsx è importante: subfinder può restituire
# sottodomini che non risolvono o che sono wildcard DNS.
# dnsx con -wd filtra i wildcard in modo esplicito.
#
# Nota: la documentazione dnsx indica -wd (wildcard-domain) come
# flag per il filtering wildcard manuale.
# -aw (auto-wildcard) è un'alternativa che rileva automaticamente
# i wildcard su più domini.
# ---------------------------------------------------------------

# Step 1: subfinder.
subfinder -d "$DOMAIN" -all -recursive -silent -o /tmp/subs.txt

# Step 2: dnsx risolve e filtra wildcard.
# -wd richiede il dominio per il filtering wildcard.
# -a record A, -resp output completo.
if command -v dnsx &>/dev/null; then
    dnsx -l /tmp/subs.txt -a -resp -wd "$DOMAIN" -silent -o /tmp/resolved.txt
else
    echo "dnsx non installato. Salto risoluzione DNS e wildcard filtering."
    cp /tmp/subs.txt /tmp/resolved.txt
fi

# Step 3: httpx verifica quali host sono vivi.
if command -v httpx &>/dev/null; then
    cat /tmp/resolved.txt | httpx -silent -sc -title -td -mc 200,401,403 -o /tmp/live_hosts.txt
else
    echo "httpx non installato. Pipeline fermata."
    exit 1
fi

# Step 4: nuclei sui vivi.
if command -v nuclei &>/dev/null; then
    nuclei -l /tmp/live_hosts.txt -severity critical,high -exclude-tags intrusive,dos -jsonl -o /tmp/nuclei_findings.jsonl
else
    echo "nuclei non installato. Pipeline fermata a live_hosts.txt."
fi

# ---------------------------------------------------------------
# Comando di produzione completo
# Enumerazione ampia, ricorsiva, active-only, rate limitato,
# timeout totale controllato, output semplice.
# ---------------------------------------------------------------
subfinder -d "$DOMAIN" \
  -all \
  -recursive \
  -nW \
  -rl 20 \
  -timeout 30 \
  -max-time 5 \
  -silent \
  -o "$OUT.subs.txt"
