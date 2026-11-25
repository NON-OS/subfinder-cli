# Introduction

🌐 [Italiano](../01-introduzione.md) · **English** · [中文](../zh/01-introduzione.md)

This tool started as a shell script I used to remember subfinder commands: flag choices, order of work, notes on what is worth doing and what is not. It was an executable notebook. It worked, but it had a flaw: one wrong variable at the top of the file and the run went off against something unrelated.

`subfinder-cli` removes that flaw. The scope becomes a file with a name, the signature of whoever authorizes it, and validity dates. You pick the target on the command line and it is checked against that file before subfinder is even looked up in `PATH`.

## Three design decisions

**Dry-run is the normal behavior.** Without `--esegui` the program prints the command and logs it. Starting by mistake is harder than not starting at all.

**When in doubt, refuse.** A target with an odd format, a URL with credentials in the host, a hostname that resolves to an excluded address: all refused. The cost of a false refusal is fixing one line of scope. The cost of a false go-ahead is an incident.

**No dependencies.** Only the Python standard library. A tool that has to guarantee what it runs should not carry fifty packages you have to trust.

## What is in the repository

```
subfinder-cli/
├── src/subfindercli/
│   ├── scope.py      loads the scope and decides whether a target is allowed
│   ├── spec.py       profiles, forbidden flags and subfinder result format
│   ├── profili.py    profile structure and flag filter
│   ├── runner.py     builds the command and runs it (never a shell)
│   ├── audit.py      hash-chained log
│   ├── risultati.py  reading, summarizing and comparing results
│   └── cli.py        arguments, messages, exit codes
├── tests/            unittest, no network and no subfinder installed
├── docs/             this documentation
├── examples/         example scopes
├── lab/              deliberately vulnerable targets (Docker)
└── scripts/          the original shell cheatsheet
```

## Who it is for

People doing contracted security testing who want a clean record of what they ran, when, and under which authorization. Students who want a healthy habit from day one: scope first, then the command. Team leads who want nobody pasting a target from a chat into a command.

## Who it is not for

Anyone looking for a way to act covertly or outside the agreed perimeter. The flags that serve that purpose are forbidden.

## Where to go next

If this is your first security test, read [02-autorizzazione.md](02-autorizzazione.md) before anything else. If you only need to know how to write the scope, go to [03-scope.md](03-scope.md).
