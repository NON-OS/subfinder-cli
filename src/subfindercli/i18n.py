"""Catalogo messaggi e scelta della lingua.

Default: italiano. La lingua si sceglie, in ordine: flag --lang, variabile
NONOS_LANG (così NONOS può impostarla a livello di sistema), poi italiano.
Il locale di sistema non conta: si parte sempre in italiano. I nomi dei comandi, dei profili e dei
flag non cambiano mai: solo i messaggi.

Ogni testo che l'utente vede passa da `t()`. Se una voce manca in una
lingua, `t()` ripiega sull'italiano: non si rompe nulla.
"""

from __future__ import annotations

import os

LINGUE = ("it", "en", "zh")
_lingua = "it"


def imposta_lingua(override: str | None = None) -> str:
    """Decide la lingua una volta, all'avvio, e la memorizza."""
    global _lingua
    for candidato in (override, os.environ.get("NONOS_LANG")):
        if candidato:
            codice = candidato.strip().lower().replace("-", "_")[:2]
            if codice in LINGUE:
                _lingua = codice
                return _lingua
    _lingua = "it"
    return _lingua


def lingua() -> str:
    return _lingua


def si_accettati() -> set[str]:
    """Risposte che contano come 'si'' in qualsiasi lingua."""
    return {"s", "si", "sì", "y", "yes", "是", "shi"}


_RUMORE = {
    "en": {"basso": "low", "medio": "medium", "alto": "high"},
    "zh": {"basso": "低", "medio": "中", "alto": "高"},
}


def rumore(valore: str) -> str:
    """Il livello di rumore di un profilo, nella lingua scelta."""
    return _RUMORE.get(_lingua, {}).get(valore, valore)


# id -> {lingua: testo}. subfinder-cli è sostituito a build-time; {campi} a runtime.
MSG: dict[str, dict[str, str]] = {
    # -- banner e avvio ----------------------------------------------------
    "banner_sub": {
        "it": " subfinder-cli {ver} — scope-first, dry-run di default",
        "en": " subfinder-cli {ver} — scope-first, dry-run by default",
        "zh": " subfinder-cli {ver} — 作用域优先，默认 dry-run",
    },
    "hint_guida": {
        "it": "Prova:  subfinder-cli guida   — modalità interattiva, passo per passo",
        "en": "Try:    subfinder-cli guida   — interactive, step by step",
        "zh": "试试:   subfinder-cli guida   — 交互式，一步步进行",
    },
    "hint_help": {
        "it": "        subfinder-cli --help  — tutti i comandi",
        "en": "        subfinder-cli --help  — all commands",
        "zh": "        subfinder-cli --help  — 所有命令",
    },
    "avviso": {
        "it": "subfinder-cli è pensato solo per sistemi che possiedi o su cui hai un'autorizzazione\n"
        "scritta. Leggi DISCLAIMER.md prima di usarlo.",
        "en": "subfinder-cli is meant only for systems you own or have written authorization\n"
        "to test. Read DISCLAIMER.md before using it.",
        "zh": "subfinder-cli 只能用于你拥有的系统，或已获得书面授权的系统。\n使用前请阅读 DISCLAIMER.md。",
    },
    # -- help di argparse --------------------------------------------------
    "help_lancia": {
        "it": "valida i target e costruisce (o lancia) {nome}",
        "en": "validate the targets and build (or run) {nome}",
        "zh": "校验目标并构建（或运行）{nome}",
    },
    "help_target_lancia": {
        "it": "uno o più target; '-' legge i target da stdin",
        "en": "one or more targets; '-' reads targets from stdin",
        "zh": "一个或多个目标；'-' 表示从 stdin 读取目标",
    },
    "help_esegui": {
        "it": "lancia davvero {nome} (default: dry-run)",
        "en": "actually run {nome} (default: dry-run)",
        "zh": "真正运行 {nome}（默认：dry-run）",
    },
    "help_conferma": {
        "it": "salta la domanda, per l'uso non interattivo",
        "en": "skip the prompt, for non-interactive use",
        "zh": "跳过确认提问，用于非交互场景",
    },
    "help_out": {
        "it": "cartella di output (default: out/<data>-<profilo>)",
        "en": "output directory (default: out/<date>-<profile>)",
        "zh": "输出目录（默认：out/<日期>-<配置>）",
    },
    "help_wordlist": {
        "it": "wordlist (default: quella del profilo)",
        "en": "wordlist (default: the profile default)",
        "zh": "字典（默认：配置自带的字典）",
    },
    "help_filtra": {
        "it": "legge target da stdin e stampa solo quelli nello scope",
        "en": "read targets from stdin and print only those in scope",
        "zh": "从 stdin 读取目标，只输出作用域内的",
    },
    "help_verifica": {
        "it": "controlla se dei target sono nello scope, senza lanciare nulla",
        "en": "check whether targets are in scope, without running anything",
        "zh": "检查目标是否在作用域内，不运行任何东西",
    },
    "help_scope_firma": {
        "it": "firma lo scope con una chiave SSH (lo fa chi autorizza)",
        "en": "sign the scope with an SSH key (done by whoever authorizes)",
        "zh": "用 SSH 密钥签名作用域（由授权人执行）",
    },
    "help_scope_verifica": {
        "it": "controlla la firma di uno scope, senza lanciare nulla",
        "en": "check a scope signature, without running anything",
        "zh": "检查作用域签名，不运行任何东西",
    },
    "help_firma_default": {
        "it": "default: <scope>.sig",
        "en": "default: <scope>.sig",
        "zh": "默认：<scope>.sig",
    },
    "help_profili": {
        "it": "elenca i profili disponibili",
        "en": "list the available profiles",
        "zh": "列出可用配置",
    },
    "help_audit": {
        "it": "verifica l'integrità del registro di audit",
        "en": "verify the integrity of the audit log",
        "zh": "校验审计日志的完整性",
    },
    "help_init": {
        "it": "crea un file scope da compilare",
        "en": "create a scope file to fill in",
        "zh": "生成一个待填写的作用域文件",
    },
    "help_doctor": {
        "it": "controlla l'ambiente ({nome}, versione, privilegi)",
        "en": "check the environment ({nome}, version, privileges)",
        "zh": "检查环境（{nome}、版本、权限）",
    },
    "help_guida": {
        "it": "modalità interattiva: ti guida da scope al lancio, passo per passo",
        "en": "interactive mode: walks you from scope to run, step by step",
        "zh": "交互模式：从作用域到运行，一步步引导",
    },
    "help_rapporto": {
        "it": "riepilogo dei risultati di un lancio",
        "en": "summary of the results of a run",
        "zh": "一次运行结果的汇总",
    },
    "help_confronta": {
        "it": "differenze tra due lanci",
        "en": "differences between two runs",
        "zh": "两次运行之间的差异",
    },
    "help_exit_code": {
        "it": "esce con 1 se ci sono differenze (utile in CI)",
        "en": "exit with 1 if there are differences (useful in CI)",
        "zh": "有差异时以 1 退出（适合 CI）",
    },
    "help_firmatari": {
        "it": "file allowed_signers: se c'è, lo scope deve essere firmato da una di queste chiavi",
        "en": "allowed_signers file: if given, the scope must be signed by one of these keys",
        "zh": "allowed_signers 文件：若指定，作用域必须由其中某个密钥签名",
    },
    "help_firma_staccata": {
        "it": "firma staccata (default: <scope>.sig)",
        "en": "detached signature (default: <scope>.sig)",
        "zh": "分离签名（默认：<scope>.sig）",
    },
    "mv_file_o_cartella": {"it": "FILE_O_CARTELLA", "en": "FILE_OR_DIR", "zh": "文件或目录"},
    "mv_vecchio": {"it": "VECCHIO", "en": "OLD", "zh": "旧"},
    "mv_nuovo": {"it": "NUOVO", "en": "NEW", "zh": "新"},
    "mv_chiave": {"it": "CHIAVE_PRIVATA", "en": "PRIVATE_KEY", "zh": "私钥"},
    # -- output di lancia --------------------------------------------------
    "out_ingaggio": {
        "it": "Ingaggio : {nome} ({rif})",
        "en": "Engagement: {nome} ({rif})",
        "zh": "项目     : {nome} ({rif})",
    },
    "out_firma": {
        "it": "Firma    : valida, {id} ({fp})",
        "en": "Signature : valid, {id} ({fp})",
        "zh": "签名     : 有效，{id} ({fp})",
    },
    "out_profilo": {
        "it": "Profilo  : {nome} - {desc} [rumore {rumore}]",
        "en": "Profile   : {nome} - {desc} [noise {rumore}]",
        "zh": "配置     : {nome} - {desc} [噪声 {rumore}]",
    },
    "out_ok": {
        "it": "  ok  {target}  ({motivo})",
        "en": "  ok  {target}  ({motivo})",
        "zh": "  ok  {target}  ({motivo})",
    },
    "out_comando": {
        "it": "Comando  : {cmd}",
        "en": "Command   : {cmd}",
        "zh": "命令     : {cmd}",
    },
    "out_nota": {
        "it": "Nota     : {nota}",
        "en": "Note      : {nota}",
        "zh": "注意     : {nota}",
    },
    "out_attivita": {
        "it": "Attività: {nota}",
        "en": "Activity  : {nota}",
        "zh": "活动     : {nota}",
    },
    "out_nota_root": {
        "it": "Nota     : il profilo '{nome}' richiede root (sudo).",
        "en": "Note      : the '{nome}' profile needs root (sudo).",
        "zh": "注意     : 配置 '{nome}' 需要 root（sudo）。",
    },
    "nota_binario": {
        "it": "{bin} non è installato qui: il comando sotto è solo un'anteprima.",
        "en": "{bin} is not installed here: the command below is only a preview.",
        "zh": "{bin} 未在此安装：下面的命令只是预览。",
    },
    "out_dry_run": {
        "it": "\nDry-run: non ho lanciato niente. Aggiungi --esegui per partire davvero.",
        "en": "\nDry-run: nothing was run. Add --esegui to actually run it.",
        "zh": "\nDry-run：什么都没有运行。加上 --esegui 才会真正运行。",
    },
    "out_risultati": {
        "it": "\nRisultati in {cartella}/  (riepilogo: subfinder-cli rapporto {cartella})",
        "en": "\nResults in {cartella}/  (summary: subfinder-cli rapporto {cartella})",
        "zh": "\n结果在 {cartella}/  （汇总：subfinder-cli rapporto {cartella}）",
    },
    "conf_intro": {
        "it": "\nStai per lanciare per conto di: {auth}",
        "en": "\nYou are about to run on behalf of: {auth}",
        "zh": "\n你即将代表以下人员运行：{auth}",
    },
    "conf_prompt": {
        "it": "Scrivi il riferimento dell'ingaggio ({rif}) per continuare: ",
        "en": "Type the engagement reference ({rif}) to continue: ",
        "zh": "输入项目编号（{rif}）以继续：",
    },
    "err_serve_wordlist": {
        "it": "serve una wordlist: usa --wordlist FILE",
        "en": "a wordlist is required: use --wordlist FILE",
        "zh": "需要字典：请使用 --wordlist FILE",
    },
    "err_sudo": {
        "it": "il profilo '{nome}' va lanciato con sudo",
        "en": "the '{nome}' profile must be run with sudo",
        "zh": "配置 '{nome}' 必须用 sudo 运行",
    },
    "err_wordlist_nf": {
        "it": "wordlist non trovata: {wl} (installa SecLists o passa --wordlist)",
        "en": "wordlist not found: {wl} (install SecLists or pass --wordlist)",
        "zh": "找不到字典：{wl}（安装 SecLists 或传入 --wordlist）",
    },
    "err_conferma": {
        "it": "conferma mancante, non parte nulla",
        "en": "no confirmation given, nothing runs",
        "zh": "未确认，不运行任何东西",
    },
    "err_codice": {
        "it": "{nome} è uscito con codice {rc}",
        "en": "{nome} exited with code {rc}",
        "zh": "{nome} 以代码 {rc} 退出",
    },
    "err_stdin_vuoto": {
        "it": "stdin vuoto: nessun target",
        "en": "stdin is empty: no targets",
        "zh": "stdin 为空：没有目标",
    },
    "err_interrotto": {"it": "interrotto", "en": "interrupted", "zh": "已中断"},
    "err_extra": {
        "it": "'--' si usa solo con 'lancia'",
        "en": "'--' can only be used with 'lancia'",
        "zh": "'--' 只能与 'lancia' 一起使用",
    },
    # -- filtra / verifica / firma -----------------------------------------
    "filtra_tot": {
        "it": "{tenuti} nello scope, {scartati} scartati",
        "en": "{tenuti} in scope, {scartati} dropped",
        "zh": "{tenuti} 个在作用域内，{scartati} 个已丢弃",
    },
    "ver_ok": {"it": "ok ", "en": "ok ", "zh": "ok "},
    "ver_no": {"it": "NO ", "en": "NO ", "zh": "否 "},
    "firma_fatto": {"it": "Firmato: {sig}", "en": "Signed: {sig}", "zh": "已签名：{sig}"},
    "firma_consegna": {
        "it": "Consegna al cliente il file di scope e la firma: lui conserva la chiave pubblica.",
        "en": "Give the client the scope file and the signature: they keep the public key.",
        "zh": "把作用域文件和签名交给客户：公钥由客户保管。",
    },
    "scopever_ok": {
        "it": "ok: firma valida di {id} ({fp})",
        "en": "ok: valid signature by {id} ({fp})",
        "zh": "ok：{id} 的有效签名（{fp}）",
    },
    # -- profili / audit / init / doctor / rapporto ------------------------
    "lbl_rumore": {"it": "rumore", "en": "noise", "zh": "噪声"},
    "lbl_quando": {"it": "Quando", "en": "When", "zh": "适用"},
    "audit_ok": {
        "it": "ok: {righe} righe, catena integra",
        "en": "ok: {righe} lines, chain intact",
        "zh": "ok：{righe} 行，哈希链完整",
    },
    "audit_ko": {
        "it": "catena non valida: {errore}",
        "en": "invalid chain: {errore}",
        "zh": "哈希链无效：{errore}",
    },
    "init_esiste": {
        "it": "{p} esiste già, non lo sovrascrivo",
        "en": "{p} already exists, not overwriting it",
        "zh": "{p} 已存在，不覆盖",
    },
    "init_creato": {
        "it": "Creato {p}. Compilalo prima di usarlo: i valori d'esempio non autorizzano niente di reale.",
        "en": "Created {p}. Fill it in before use: the sample values authorize nothing real.",
        "zh": "已创建 {p}。使用前请填写：示例值不授权任何真实操作。",
    },
    # riga intera: i caratteri cinesi occupano due colonne e {:<10} li conterebbe come una
    "doc_versione": {"it": "versione  : {v}", "en": "version   : {v}", "zh": "版本      : {v}"},
    "non_riconosciuta": {"it": "non riconosciuta", "en": "not recognized", "zh": "无法识别"},
    "root_si": {"it": "si", "en": "yes", "zh": "是"},
    "root_no": {
        "it": "no (alcuni profili richiedono sudo)",
        "en": "no (some profiles need sudo)",
        "zh": "否（部分配置需要 sudo）",
    },
    "rapporto_titolo": {"it": "Rapporto {nome}", "en": "{nome} report", "zh": "{nome} 报告"},
    # -- scope: motivi -----------------------------------------------------
    "sc_vuoto": {"it": "target vuoto", "en": "empty target", "zh": "目标为空"},
    "sc_flag": {
        "it": "un target non può iniziare con '-': sembra un flag",
        "en": "a target cannot start with '-': it looks like a flag",
        "zh": "目标不能以 '-' 开头：看起来像一个标志",
    },
    "sc_dominio_no_ip": {
        "it": "serve un nome di dominio, non un indirizzo IP",
        "en": "a domain name is required, not an IP address",
        "zh": "需要域名，而不是 IP 地址",
    },
    "sc_dominio_valido": {
        "it": "serve un nome di dominio valido, senza schema né percorso",
        "en": "a valid domain name is required, with no scheme or path",
        "zh": "需要有效的域名，不带协议和路径",
    },
    "sc_formato": {
        "it": "formato non riconosciuto (ammessi: IP, CIDR, hostname; niente range alla nmap)",
        "en": "unrecognized format (allowed: IP, CIDR, hostname; no nmap-style ranges)",
        "zh": "无法识别的格式（允许：IP、CIDR、主机名；不支持 nmap 式的范围）",
    },
    "sc_cidr_url": {
        "it": "sembra un CIDR: in modalità url servono URL o singoli host",
        "en": "looks like a CIDR: url mode needs URLs or single hosts",
        "zh": "看起来是 CIDR：url 模式需要 URL 或单个主机",
    },
    "sc_host": {"it": "host {host}: {motivo}", "en": "host {host}: {motivo}", "zh": "主机 {host}：{motivo}"},
    "sc_sovrappone": {
        "it": "si sovrappone all'esclusione {esclusa}",
        "en": "overlaps the exclusion {esclusa}",
        "zh": "与排除项 {esclusa} 重叠",
    },
    "sc_dentro": {"it": "dentro {inclusa}", "en": "inside {inclusa}", "zh": "在 {inclusa} 内"},
    "sc_non_in_rete": {
        "it": "non è contenuto in nessuna rete inclusa",
        "en": "not contained in any included network",
        "zh": "不在任何已包含的网络内",
    },
    "sc_host_escluso": {
        "it": "hostname escluso esplicitamente",
        "en": "hostname explicitly excluded",
        "zh": "主机名被明确排除",
    },
    "sc_risolve_escl": {
        "it": "risolve in {ip}, che è dentro l'esclusione {esclusa}",
        "en": "resolves to {ip}, which is inside the exclusion {esclusa}",
        "zh": "解析为 {ip}，位于排除项 {esclusa} 内",
    },
    "sc_combacia": {"it": "combacia con {modello}", "en": "matches {modello}", "zh": "匹配 {modello}"},
    "sc_host_non_incl": {
        "it": "hostname non presente tra gli inclusi",
        "en": "hostname not among the included ones",
        "zh": "主机名不在包含列表中",
    },
    "sc_fuori": {
        "it": "target fuori scope, non eseguo nulla:\n{righe}",
        "en": "targets out of scope, running nothing:\n{righe}",
        "zh": "目标超出作用域，不运行任何东西：\n{righe}",
    },
    "sc_url_trucchi": {
        "it": "URL con spazi, backslash o credenziali (@): rifiutato, è un classico per confondere i filtri",
        "en": "URL with spaces, backslashes or credentials (@): rejected, a classic trick to fool filters",
        "zh": "含空格、反斜杠或凭据（@）的 URL：已拒绝，这是绕过过滤的常见手法",
    },
    "sc_url_schema": {
        "it": "schema '{scheme}' non ammesso (solo http e https)",
        "en": "scheme '{scheme}' not allowed (only http and https)",
        "zh": "不允许的协议 '{scheme}'（只允许 http 和 https）",
    },
    "sc_url_malformato": {"it": "URL malformato", "en": "malformed URL", "zh": "URL 格式错误"},
    "sc_url_no_host": {"it": "nessun host nell'URL", "en": "no host in the URL", "zh": "URL 中没有主机"},
    # -- scope: errori del file --------------------------------------------
    "sc_non_ancora": {
        "it": "lo scope '{nome}' diventa valido il {dal}, oggi è {oggi}",
        "en": "scope '{nome}' becomes valid on {dal}, today is {oggi}",
        "zh": "作用域 '{nome}' 于 {dal} 生效，今天是 {oggi}",
    },
    "sc_scaduto": {
        "it": "lo scope '{nome}' è scaduto il {fino}, oggi è {oggi}",
        "en": "scope '{nome}' expired on {fino}, today is {oggi}",
        "zh": "作用域 '{nome}' 已于 {fino} 过期，今天是 {oggi}",
    },
    "sc_data_toml": {
        "it": "'{chiave}' deve essere una data TOML (AAAA-MM-GG)",
        "en": "'{chiave}' must be a TOML date (YYYY-MM-DD)",
        "zh": "'{chiave}' 必须是 TOML 日期（YYYY-MM-DD）",
    },
    "sc_campo_mancante": {
        "it": "campo obbligatorio mancante o vuoto: engagement.{chiave}",
        "en": "required field missing or empty: engagement.{chiave}",
        "zh": "必填字段缺失或为空：engagement.{chiave}",
    },
    "sc_non_trovato": {
        "it": "file di scope non trovato: {p}",
        "en": "scope file not found: {p}",
        "zh": "找不到作用域文件：{p}",
    },
    "sc_toml": {
        "it": "TOML non valido in {p}: {e}",
        "en": "invalid TOML in {p}: {e}",
        "zh": "{p} 中的 TOML 无效：{e}",
    },
    "sc_sezioni": {
        "it": "servono le sezioni [engagement] e [scope]",
        "en": "the [engagement] and [scope] sections are required",
        "zh": "需要 [engagement] 和 [scope] 两个段",
    },
    "sc_date_invertite": {
        "it": "valido_fino precede valido_dal",
        "en": "valido_fino comes before valido_dal",
        "zh": "valido_fino 早于 valido_dal",
    },
    "sc_include_vuoto": {
        "it": "scope.include è vuoto: uno scope senza target non autorizza niente",
        "en": "scope.include is empty: a scope with no targets authorizes nothing",
        "zh": "scope.include 为空：没有目标的作用域不授权任何东西",
    },
    "sc_campo_lista": {
        "it": "scope.{campo} deve essere una lista di stringhe",
        "en": "scope.{campo} must be a list of strings",
        "zh": "scope.{campo} 必须是字符串列表",
    },
    "sc_tutto_internet": {
        "it": "scope.include contiene {voce}: equivale a 'tutto internet'",
        "en": "scope.include contains {voce}: that means 'the whole internet'",
        "zh": "scope.include 含有 {voce}：等于“整个互联网”",
    },
    "sc_voce_non_valida": {
        "it": "voce non valida in scope.{campo}: {voce}",
        "en": "invalid entry in scope.{campo}: {voce}",
        "zh": "scope.{campo} 中的条目无效：{voce}",
    },
    "sc_wildcard_tld": {
        "it": "scope.include contiene {voce}: wildcard su un TLD",
        "en": "scope.include contains {voce}: a wildcard on a TLD",
        "zh": "scope.include 含有 {voce}：对顶级域使用通配符",
    },
    # -- runner ------------------------------------------------------------
    "run_non_trovato": {
        "it": "{bin} non trovato nel PATH. {inst}",
        "en": "{bin} not found in PATH. {inst}",
        "zh": "PATH 中找不到 {bin}。{inst}",
    },
    "run_non_sembra": {
        "it": "{binario} non sembra {nome}: l'output di '{cmd}' non contiene '{ric}'. {inst}",
        "en": "{binario} does not look like {nome}: the output of '{cmd}' does not contain '{ric}'. {inst}",
        "zh": "{binario} 看起来不是 {nome}：'{cmd}' 的输出中没有 '{ric}'。{inst}",
    },
    # -- firma -------------------------------------------------------------
    "fi_no_keygen": {
        "it": "ssh-keygen non trovato: serve OpenSSH per firmare e verificare lo scope",
        "en": "ssh-keygen not found: OpenSSH is needed to sign and verify the scope",
        "zh": "找不到 ssh-keygen：签名和校验作用域需要 OpenSSH",
    },
    "fi_sig_esiste": {
        "it": "{sig} esiste già: non lo sovrascrivo, cancellalo se vuoi rifirmare",
        "en": "{sig} already exists: not overwriting it, delete it if you want to re-sign",
        "zh": "{sig} 已存在：不覆盖，如需重新签名请先删除",
    },
    "fi_non_riuscita": {
        "it": "firma non riuscita: {err}",
        "en": "signing failed: {err}",
        "zh": "签名失败：{err}",
    },
    "fi_errore_ignoto": {"it": "errore sconosciuto", "en": "unknown error", "zh": "未知错误"},
    "fi_non_trovata": {
        "it": "firma non trovata: {sig} (si crea con 'subfinder-cli scope-firma')",
        "en": "signature not found: {sig} (create it with 'subfinder-cli scope-firma')",
        "zh": "找不到签名：{sig}（用 'subfinder-cli scope-firma' 创建）",
    },
    "fi_firmatari_nf": {
        "it": "file dei firmatari non trovato: {f}",
        "en": "signers file not found: {f}",
        "zh": "找不到签名者文件：{f}",
    },
    "fi_nessuno": {
        "it": "la firma non è di nessuno dei firmatari ammessi",
        "en": "the signature does not belong to any allowed signer",
        "zh": "该签名不属于任何允许的签名者",
    },
    "fi_non_valida": {
        "it": "firma non valida: lo scope è stato modificato dopo la firma, oppure la firma non è per questo programma",
        "en": "invalid signature: the scope was changed after signing, or the signature is not for this program",
        "zh": "签名无效：作用域在签名后被修改，或该签名不是给本程序的",
    },
    # -- risultati ---------------------------------------------------------
    "ri_nessun_file": {
        "it": "nessun file 'risultati*' in {p}",
        "en": "no 'risultati*' file in {p}",
        "zh": "{p} 中没有 'risultati*' 文件",
    },
    "ri_non_trovato": {"it": "non trovato: {p}", "en": "not found: {p}", "zh": "找不到：{p}"},
    "ri_totale": {"it": "{n} risultati", "en": "{n} results", "zh": "{n} 条结果"},
    "ri_totale_md": {"it": "Risultati: {n}", "en": "Results: {n}", "zh": "结果：{n}"},
    "ri_quanti": {"it": "Quanti", "en": "Count", "zh": "数量"},
    "ri_nessuna_diff": {"it": "Nessuna differenza.", "en": "No differences.", "zh": "没有差异。"},
    # -- audit -------------------------------------------------------------
    "au_inesistente": {"it": "file inesistente", "en": "file does not exist", "zh": "文件不存在"},
    "au_formato": {
        "it": "riga {n}: formato illeggibile",
        "en": "line {n}: unreadable format",
        "zh": "第 {n} 行：格式无法读取",
    },
    "au_spezzata": {
        "it": "riga {n}: la catena si spezza qui",
        "en": "line {n}: the chain breaks here",
        "zh": "第 {n} 行：哈希链在此断裂",
    },
    "au_alterato": {
        "it": "riga {n}: contenuto alterato",
        "en": "line {n}: content altered",
        "zh": "第 {n} 行：内容被篡改",
    },
    # -- profili: flag vietati ---------------------------------------------
    "pr_vietato": {
        "it": "{flag} non è ammesso: {motivo}",
        "en": "{flag} is not allowed: {motivo}",
        "zh": "{flag} 不被允许：{motivo}",
    },
    # -- modalità guidata -------------------------------------------------
    "guida_tty": {
        "it": "la modalità guidata ha bisogno di un terminale interattivo",
        "en": "guided mode needs an interactive terminal",
        "zh": "引导模式需要交互式终端",
    },
    "guida_intro": {
        "it": "Modalità guidata. Niente parte senza la tua conferma finale.\n",
        "en": "Guided mode. Nothing runs without your final confirmation.\n",
        "zh": "引导模式。没有你最后的确认，什么都不会运行。\n",
    },
    "prompt_scope": {
        "it": "File di scope [scope.toml]: ",
        "en": "Scope file [scope.toml]: ",
        "zh": "作用域文件 [scope.toml]: ",
    },
    "prompt_crea_scope": {
        "it": "{percorso} non esiste. Ne creo uno da compilare? [s/N] ",
        "en": "{percorso} does not exist. Create one to fill in? [y/N] ",
        "zh": "{percorso} 不存在。创建一个待填写的? [y/N] ",
    },
    "scope_creato": {
        "it": "Creato {percorso}. Compilalo coi dati dell'ingaggio, poi rilancia 'subfinder-cli guida'.",
        "en": "Created {percorso}. Fill it in with the engagement details, then run 'subfinder-cli guida' again.",
        "zh": "已创建 {percorso}。填入项目信息后，再次运行 'subfinder-cli guida'。",
    },
    "guida_ingaggio": {
        "it": "Ingaggio: {nome} ({rif}), autorizzato da {auth}.\n",
        "en": "Engagement: {nome} ({rif}), authorized by {auth}.\n",
        "zh": "项目: {nome} ({rif})，授权人 {auth}。\n",
    },
    "profili_disponibili": {
        "it": "Profili disponibili:",
        "en": "Available profiles:",
        "zh": "可用配置:",
    },
    "prompt_profilo": {
        "it": "\nQuale profilo? [numero o nome] ",
        "en": "\nWhich profile? [number or name] ",
        "zh": "\n选哪个配置? [编号或名称] ",
    },
    "profilo_no": {
        "it": "profilo non riconosciuto",
        "en": "profile not recognized",
        "zh": "无法识别的配置",
    },
    "prompt_target": {
        "it": "\nTarget per il profilo '{profilo}' (separati da spazio): ",
        "en": "\nTargets for the '{profilo}' profile (space-separated): ",
        "zh": "\n配置 '{profilo}' 的目标（用空格分隔）: ",
    },
    "target_no": {
        "it": "nessun target indicato",
        "en": "no target given",
        "zh": "未指定目标",
    },
    "prompt_wordlist": {
        "it": "Wordlist [Invio per quella del profilo]: ",
        "en": "Wordlist [Enter for the profile default]: ",
        "zh": "字典 [回车使用配置默认]: ",
    },
    "prompt_esegui": {
        "it": "\nLanciare davvero? Rispondi no per un dry-run. [s/N] ",
        "en": "\nRun for real? Answer no for a dry-run. [y/N] ",
        "zh": "\n真的运行? 回答 no 做 dry-run。[y/N] ",
    },
}


def t(key: str, **campi: object) -> str:
    voci = MSG.get(key, {})
    testo = voci.get(_lingua) or voci.get("it") or key
    return testo.format(**campi) if campi else testo


# Le frasi interne di argparse (usage, options, errori), nella lingua scelta.
# argparse le passa a gettext: cli.py gli sostituisce questa funzione.
_ARGPARSE: dict[str, dict[str, str]] = {
    "usage: ": {"it": "uso: ", "zh": "用法："},
    "positional arguments": {"it": "argomenti posizionali", "zh": "位置参数"},
    "options": {"it": "opzioni", "zh": "选项"},
    "show this help message and exit": {"it": "mostra questo aiuto ed esce", "zh": "显示帮助信息并退出"},
    "show program's version number and exit": {"it": "mostra la versione ed esce", "zh": "显示版本号并退出"},
    "%(prog)s: error: %(message)s\n": {"it": "%(prog)s: errore: %(message)s\n", "zh": "%(prog)s：错误：%(message)s\n"},
    "the following arguments are required: %s": {
        "it": "mancano argomenti obbligatori: %s",
        "zh": "缺少必需的参数：%s",
    },
    "unrecognized arguments: %s": {"it": "argomenti non riconosciuti: %s", "zh": "无法识别的参数：%s"},
    "invalid choice: %(value)r (choose from %(choices)s)": {
        "it": "scelta non valida: %(value)r (scegli tra %(choices)s)",
        "zh": "无效的选择：%(value)r（可选：%(choices)s）",
    },
    "expected one argument": {"it": "serve un argomento", "zh": "需要一个参数"},
}


def argparse_gettext(messaggio: str) -> str:
    return _ARGPARSE.get(messaggio, {}).get(_lingua, messaggio)
