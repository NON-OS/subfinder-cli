# Disclaimer

Leggilo tutto. Non è un testo di rito.

## In due righe

Usare subfinder contro un sistema che non è tuo, senza il permesso scritto di chi lo gestisce, può essere un reato. Questo strumento esiste per ridurre il rischio di errore di chi ha già l'autorizzazione, non per darti il diritto di usarlo.

## Cosa fa questo strumento al bersaglio

subfinder è passivo: interroga fonti pubbliche (certificate transparency, archivi, motori) e non invia traffico ai tuoi target. Anche così, va usato solo su domini per cui hai un incarico: una lista di sottodomini è informazione sensibile del cliente.

## Cosa puoi analizzare

- Sistemi tuoi, in una rete tua.
- Macchine virtuali e container che hai creato tu, per esempio il lab in `lab/`.
- Sistemi di un cliente, solo dopo aver firmato un contratto o una lettera di autorizzazione che nomina i target, il periodo e le attività consentite.
- Target di un programma di bug bounty, solo quelli elencati nello scope del programma e rispettando le sue regole sulle attività vietate.
- Piattaforme di allenamento (Hack The Box, TryHackMe e simili) nei limiti dei loro regolamenti.

## Cosa non puoi analizzare

Tutto il resto. In particolare: la rete dell'ufficio "per curiosità", il sito di un ex datore di lavoro, un dominio trovato su un motore di ricerca, il router del vicino, un'azienda che "tanto non se ne accorge". Il fatto che un servizio sia raggiungibile non significa che tu abbia il permesso di interrogarlo.

## Il quadro legale, in breve

Non sono un avvocato e questo non è un parere legale. Le norme cambiano da paese a paese e nel tempo. Se lavori per un cliente, fatti dire da un legale cosa conta come autorizzazione valida.

- **Italia.** L'accesso abusivo a un sistema informatico è previsto dall'art. 615-ter del codice penale. L'art. 635-bis e seguenti puniscono il danneggiamento di dati e sistemi, che un'analisi sbagliata può provocare davvero.
- **Unione europea.** La direttiva 2013/40/UE chiede agli Stati membri di punire gli attacchi contro i sistemi informativi.
- **Stati Uniti.** Il Computer Fraud and Abuse Act.
- **Regno Unito.** Il Computer Misuse Act 1990.

## Autorizzazione scritta: cosa deve contenere

Almeno questo. Il dettaglio è in [docs/02-autorizzazione.md](docs/02-autorizzazione.md).

1. Chi autorizza, con nome, ruolo e il potere di farlo per quei sistemi.
2. Quali target, in forma esatta (indirizzi, reti, domini).
3. Da quando a quando.
4. Quali attività sono consentite e quali no.
5. Un contatto da chiamare se qualcosa va storto.

Se una di queste cose manca, non sei pronto.

## Il software

Il software è fornito così com'è, senza garanzie, come dice la licenza MIT. Può contenere errori. Il controllo dello scope è una rete di sicurezza: se lo scope file è sbagliato, il programma ti lascerà analizzare il target sbagliato, perché si fida di quello che gli scrivi.

L'autore non risponde dell'uso che ne fai. Chi usa subfinder-cli è l'unico responsabile di ciò che analizza, di avere l'autorizzazione, e delle conseguenze.

## Segnalare un abuso

Se vedi questo strumento usato per attaccare sistemi altrui, scrivimi con una segnalazione privata, vedi [SECURITY.md](SECURITY.md).
