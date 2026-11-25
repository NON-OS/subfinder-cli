# subfinder-cli

🌐 [Italiano](README.md) · **English** · [中文](README.zh.md)

[![ci](https://github.com/NON-OS/subfinder-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/NON-OS/subfinder-cli/actions/workflows/ci.yml)
![License MIT](https://img.shields.io/badge/License-MIT-yellow)
![python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![Kali · Parrot · Linux](https://img.shields.io/badge/Kali%20%C2%B7%20Parrot%20%C2%B7%20Linux-primary-1793d1)
![subfinder](https://img.shields.io/badge/wrapper%20for-subfinder-green)
![dependencies 0](https://img.shields.io/badge/dependencies-0-lightgrey)

```
  ┌─ scope ─┐   ┌─ dry-run ─┐   ┌─ confirm ─┐   ┌─ subfinder ─┐   ┌─ audit ─┐   ┌─ report ─┐
  │ check   │ → │ show      │ → │ ticket    │ → │ runs    │ → │ chain   │ → │ summary  │
  └─────────┘   └───────────┘   └───────────┘   └─────────┘   └─────────┘   └──────────┘
```

Passive subdomain enumeration with a validated scope, dry-run by default and a hash-chained audit. Authorized domains only.

> **Only systems you own or have written authorization for.** Read [DISCLAIMER.md](DISCLAIMER.md) before you launch anything.

## What it is

`subfinder-cli` is a thin orchestrator around ProjectDiscovery's subfinder. It does not replace subfinder and does not reimplement its sources. It does three things: it checks that the domain is in the declared scope, it keeps a log of what was run, and it filters the results before they reach other tools.

Passive enumeration seems harmless, and mostly it is: it never contacts the target. The risk comes afterward. Subfinder turns up names nobody authorized you to touch (vendors, third-party services, subdomains hosted by others), and if that list feeds straight into a port scan, you have scanned systems that are not yours. That is what the `filtra` command is for: it reads a list from stdin and lets through only what the scope names.

## In action

![subfinder-cli in guided mode on Kali Linux](docs/img/guida-kali.en.png)

*Guided mode (`subfinder-cli guida`) running on Kali Linux: logo, profile selection, scope validation, command preview. Real screenshot.*

```console
$ subfinder-cli --lang en lancia completo example.org --scope scope.toml
Engagement: ACME-2026 (ACME-2026-014)
Profile   : completo - All available sources. [noise low]
  ok  example.org  (matches example.org)
Command   : subfinder -all -silent -dL out/esempio/target.txt -o out/esempio/risultati.txt
Activity  : passive enumeration: it queries public sources and does not contact the targets. The results can still fall outside the scope: filter them with 'filtra' before passing them to other tools.

Dry-run: nothing was run. Add --esegui to actually run it.
```

With an out-of-scope target, even among valid ones, nothing runs:

```console
$ subfinder-cli --lang en lancia completo example.org altro.org --scope scope.toml
subfinder-cli: targets out of scope, running nothing:
  altro.org: hostname not among the included ones
$ echo $?
3
```

The `lancia` command never runs without `--esegui`. What you see above is a preview.

The output follows the language you pick: `--lang it|en|zh` or the `NONOS_LANG` variable (handy for setting it system-wide). It always starts in Italian.

## What it does

| | |
|---|---|
| Scope | Domain, host or URL (`dominio` mode), with exclusions and validity dates. When in doubt, it refuses. |
| Dry-run | By default nothing runs. `--esegui` asks for confirmation. |
| Profiles | 5, each marked with its noise level and when to use it. |
| Flag filter | Flags that bypass the scope or seize control of the output are blocked. |
| List filter | `filtra` reads a list from stdin and lets through only what is in scope. |
| Signed scope | The client signs the scope with their SSH key. If the file changes after signing, nothing runs. |
| Audit | Hash-chained log. Scope hash and signer included, sensitive values masked. |
| Report | Summary of results as text, Markdown or JSON. |
| Diff | What changed between two runs, with an exit code for CI. |
| Dependencies | None: just the Python standard library. |

## Platform

Built for **Kali**, **Parrot** and Linux in general: that is where these tools live and where `subfinder-cli` gets used. It also runs on macOS. Windows is untested, and there some privilege checks (`os.geteuid`) do not apply.

## Installation

You need Python 3.11 or newer and subfinder on your `PATH`. Kali/Debian: sudo apt install subfinder. Anywhere with Go: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

```sh
git clone git@github.com:NON-OS/subfinder-cli.git
cd subfinder-cli
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
subfinder-cli doctor
```

## First use

### The simplest way: guided mode

`subfinder-cli guida` asks you one question at a time — scope, profile, target — shows the command preview, and launches nothing without your final confirmation. It is the recommended way to start:

```sh
subfinder-cli guida
```

### Or by command

```sh
subfinder-cli init scope.toml          # crea il modello
$EDITOR scope.toml               # compilalo con il cliente
subfinder-cli verifica example.org --scope scope.toml
subfinder-cli lancia completo example.org --scope scope.toml            # dry-run
subfinder-cli lancia completo example.org --scope scope.toml --esegui   # parte davvero
```

In a terminal, `--esegui` asks you to type the engagement ticket. In a script, use `--conferma`. Other subfinder flags go after `--`, unless they are among the forbidden ones ([docs/04-profili.md](docs/en/04-profili.md)).

A full flow:

```sh
subfinder-cli lancia completo example.org --scope scope.toml --esegui
subfinder-cli rapporto out/*-completo/ --formato markdown > sottodomini.md
```

## Commands

| Command | What it does |
|---|---|
| `guida` | step-by-step interactive mode: scope → profile → target → confirmation |
| `lancia <profilo> <target...>` | validates and builds (or runs) subfinder. With `-` it reads targets from stdin |
| `filtra` | reads targets from stdin and prints only those in scope |
| `verifica <target...>` | tells you whether the targets are in scope, without launching |
| `scope-firma <file>` / `scope-verifica <file>` | signs and checks the scope with an SSH key |
| `rapporto <file_or_dir>` | summary of results: list of subdomains |
| `confronta <old> <new>` | differences between two runs |
| `profili` | lists the profiles with their exact flags |
| `audit [file]` | verifies the log's hash chain |
| `init [file]` | creates a scope file to fill in |
| `doctor` | checks subfinder, version, privileges |

## Profiles

| Profile | What it does | Noise | Root |
|---|---|---|---|
| `base` | Free sources only, clean output. | low | no |
| `completo` | All available sources. | low | no |
| `ricorsivo` | All sources, including on the subdomains it finds. | low | no |
| `sorgenti` | Like completo, but in JSON with the source of each result. | low | no |
| `prudente` | Recursive, with request and time limits. | low | no |

![subfinder-cli doctor and profiles on Kali Linux](docs/img/info-kali.en.png)

*`subfinder-cli doctor` (finds the real subfinder binary in `/usr/bin/`) and the profile list, on Kali Linux.*

## Exit codes

| Code | Meaning |
|---|---|
| 0 | all good |
| 1 | `confronta --exit-code` found differences |
| 2 | wrong arguments or a forbidden flag |
| 3 | at least one target out of scope |
| 4 | scope unreadable, malformed or expired |
| 5 | subfinder missing |
| 6 | run without confirmation, or a profile that needs root without sudo |
| 7 | subfinder exited with an error, or the audit chain is broken |

## The tool chain

This repository is one of eight, designed to work together. Each one checks the scope on its own.

```mermaid
flowchart LR
    subfinder[subfinder-cli]
    dnsx[dnsx-cli]
    subfinder --> dnsx
    naabu[naabu-cli]
    dnsx --> naabu
    httpx[httpx-cli]
    naabu --> httpx
    katana[katana-cli]
    httpx --> katana
    ffuf[ffuf-cli]
    katana --> ffuf
    nuclei[nuclei-cli]
    ffuf --> nuclei
    style subfinder stroke-width:3px
```

- [dnsx-cli](https://github.com/NON-OS/dnsx-cli): dns resolution
- [naabu-cli](https://github.com/NON-OS/naabu-cli): port scanning
- [httpx-cli](https://github.com/NON-OS/httpx-cli): http probes
- [katana-cli](https://github.com/NON-OS/katana-cli): web crawling
- [ffuf-cli](https://github.com/NON-OS/ffuf-cli): path fuzzing
- [nuclei-cli](https://github.com/NON-OS/nuclei-cli): vulnerability scanning
- [nmap-cli](https://github.com/NON-OS/nmap-cli): port and service scanning with nmap

## Documentation

1. [Introduction and philosophy](docs/en/01-introduzione.md)
2. [Authorization: what you need before touching a target](docs/en/02-autorizzazione.md)
3. [The scope file](docs/en/03-scope.md)
4. [Profiles and forbidden flags](docs/en/04-profili.md)
5. [The audit log](docs/en/05-audit.md)
6. [Architecture](docs/en/06-architettura.md)
7. [Where to try it safely](docs/en/07-lab.md)
8. [Reports and diffs](docs/en/08-rapporti.md)
9. [Signed scope](docs/en/09-firma.md)
10. [Compatibility and testing](docs/en/10-compatibilita.md)

The shell cheatsheet the project grew out of is in [scripts/](scripts/).

## What it does not do

It does not find out whether you have permission: you declare that in the scope file, and the program takes your word for it. It does not protect against anyone who runs `subfinder` directly. The flag filter is a safety net against mistakes, not a sandbox. The details are in [docs/06-architettura.md](docs/en/06-architettura.md).

## Development

```sh
make check     # ruff (lint + format), mypy --strict, test e coverage
```

No runtime dependencies (just the standard library). Development tools install with `pip install -e ".[dev]"`. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

MIT, see [LICENSE](LICENSE). The license covers the code; it does not authorize any activity.
