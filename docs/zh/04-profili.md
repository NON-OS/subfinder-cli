# 配置与被禁标志

🌐 [Italiano](../04-profili.md) · [English](../en/04-profili.md) · **中文**

> ⚠️ 本页为机器翻译草稿，正式发布前需母语者校对。

| 配置 | 作用 | 噪声 | Root |
|---|---|---|---|
| `base` | 仅使用免费数据源，输出干净。 | 低 | 否 |
| `completo` | 使用所有可用的数据源。 | 低 | 否 |
| `ricorsivo` | 使用所有数据源，并对找到的子域名继续递归。 | 低 | 否 |
| `sorgenti` | 与 completo 相同，但以 JSON 输出，并标注每条结果的来源。 | 低 | 否 |
| `prudente` | 递归，但带请求数和时间限制。 | 低 | 否 |

`subfinder-cli profili` 会打印每个配置的具体标志。

## 各配置的作用

**base** (`-silent`). 仅使用免费数据源，输出干净。 第一轮侦察，查看域名是否有明显的子域名。

**completo** (`-all -silent`). 使用所有可用的数据源。 当 base 配置不够用时使用。数据源越多耗时越长，最好的数据源还需要 API 密钥。

**ricorsivo** (`-all -recursive -silent`). 使用所有数据源，并对找到的子域名继续递归。 用于多级域名（a.b.c.域名）。会大幅增加耗时。

**sorgenti** (`-all -oJ -cs`). 与 completo 相同，但以 JSON 输出，并标注每条结果的来源。 用于了解哪个数据源发现了什么，并评估哪些 API 密钥值得投入。

**prudente** (`-all -recursive -rl 10 -timeout 30 -max-time 5 -silent`). 递归，但带请求数和时间限制。 当数据源对你有速率限制，或你希望一次任务在确定的时间内（5 分钟）完成时使用。

## 手动传入标志

`--` 之后写的所有内容都会追加在配置标志之后传给 subfinder，前提是不在被禁清单中。比对时不区分大小写，`-flag valore` 和 `-flag=valore` 两种写法都能识别，一个或两个短横线均可。

```sh
subfinder-cli lancia completo example.org --scope scope.toml -- -timeout 5
```

## 被禁标志清单

| 标志 | 原因 |
|---|---|
| `-d`, `-domain`, `-dl`, `-list` | 域名来自经过作用域校验的文件 |
| `-o`, `-output`, `-od`, `-output-dir` | 输出由 subfinder-cli 管理 |
| `-up`, `-update` | 程序更新应单独进行，而不是在一次授权任务中进行 |

## 过滤器做不到的事

它不是沙箱。想绕过它并不难，比如直接调用 `subfinder`。它的作用是拦住失误和坏习惯，而不是拦住一个已经能访问你终端的恶意人员。如果某项与客户约定好的活动需要用到被禁标志，请直接使用 subfinder，并在项目记录中注明这一选择。
