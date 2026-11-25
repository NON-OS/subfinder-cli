# Profiles and forbidden flags

🌐 [Italiano](../04-profili.md) · **English** · [中文](../zh/04-profili.md)

| Profile | What it does | Noise | Root |
|---|---|---|---|
| `base` | Free sources only, clean output. | low | no |
| `completo` | All available sources. | low | no |
| `ricorsivo` | All sources, including on the subdomains it finds. | low | no |
| `sorgenti` | Like completo, but in JSON with the source of each result. | low | no |
| `prudente` | Recursive, with request and time limits. | low | no |

`subfinder-cli profili` prints the exact flags of each one.

## What each profile does

**base** (`-silent`). Free sources only, clean output. First pass to see if the domain has any obvious subdomains.

**completo** (`-all -silent`). All available sources. When the base profile isn't enough. More sources means more time, and the best ones need API keys.

**ricorsivo** (`-all -recursive -silent`). All sources, including on the subdomains it finds. For domains with many levels (a.b.c.domain). Adds a lot of runtime.

**sorgenti** (`-all -oJ -cs`). Like completo, but in JSON with the source of each result. To see which source found what, and judge which API keys are worth it.

**prudente** (`-all -recursive -rl 10 -timeout 30 -max-time 5 -silent`). Recursive, with request and time limits. When sources are rate-limiting you or you want a run that finishes within a fixed window (5 minutes).

## Passing flags by hand

Everything you write after `--` goes to subfinder, after the profile flags, provided it is not on the forbidden list. The check is case-insensitive and accepts both `-flag valore` and `-flag=valore`, with one or two dashes.

```sh
subfinder-cli lancia completo example.org --scope scope.toml -- -timeout 5
```

## Forbidden list

| Flag | Why |
|---|---|
| `-d`, `-domain`, `-dl`, `-list` | domains come from the file validated against the scope |
| `-o`, `-output`, `-od`, `-output-dir` | output is handled by subfinder-cli |
| `-up`, `-update` | updating the program is done separately, not inside an authorized run |

## What the filter does not do

It is not a sandbox. If you want to get around it you can, for example by calling `subfinder` directly. It is there to stop mistakes and bad habits, not an attacker who already has access to your terminal. If you need a forbidden flag for an activity agreed with the client, use subfinder directly and record the decision in the engagement.
