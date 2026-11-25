# Contribuire

Il progetto è piccolo e vorrei che restasse così.

## Prima di aprire una pull request

Apri una issue e dimmi cosa vuoi cambiare. Evito di rifiutare lavoro già fatto.

Le modifiche che accetto volentieri: errori nel controllo dello scope, URL o target che il controllo non vede, flag che andrebbero vietati, documentazione poco chiara, test che mancano. Quelle che rifiuto: nuove dipendenze, nuovi profili che includono tecniche di evasione o brute force di credenziali, qualsiasi cosa che indebolisca un controllo.

## Regole

- Solo libreria standard di Python, versione 3.11 o successiva.
- Ogni correzione porta un test che prima falliva.
- Se tocchi `scope.py` o `spec.py`, aggiungi i casi limite che hai pensato, non solo quello felice.
- I messaggi di errore sono in italiano e dicono cosa fare, non solo cosa è andato storto.
- Nessun indirizzo reale negli esempi: usa gli intervalli riservati (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24) e il dominio `example.org`.

## Come si provano le modifiche

```sh
make check     # ruff e unittest
```

## Messaggi di commit

Una riga al presente che dica cosa cambia, in italiano. Se serve, una riga vuota e il perché.

```
Rifiuta gli URL con credenziali nell'host

http://10.0.0.5@evil.example sembra un indirizzo interno ma è un host esterno.
```
