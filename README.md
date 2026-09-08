# 我的 Codex 桌宠

跨设备保存、安装和上传个人自定义桌宠。素材放在 `pets/<id>/` 中，保留原始 `pet.json` 和它引用的 spritesheet，不修改动画或版本。

| ID | 桌宠 | 格式 |
| --- | --- | --- |
| `baiqi` | 白起 | v2 |
| `kyubey` | 丘比 / Kyubey | v1（原清单未指定版本） |
| `toyama-kasumi` | 户山香澄 | v2 |
| `wakaba-mutsumi` | 若叶睦 | v2 |
| `wakaba-mutsumi-tsukinomori` | 若叶睦·月之森校服 | v2 |

## 直接让 Codex 操作

在其他设备向 Codex 发送：

> 请克隆 https://github.com/X-Immortal/my-codex-pets ，阅读 README.md，把仓库中所有桌宠安装到当前设备的 Codex。遇到同名且内容不同的桌宠先告诉我。

上传其他设备的桌宠：

> 请将本机所有自定义 Codex 桌宠同步到 git@github.com:X-Immortal/my-codex-pets.git，先拉取远程，再导出、检查、提交和推送。遇到同名且内容不同的桌宠先告诉我。

上传设备需要对仓库有写入权限，使用已配置的 GitHub SSH 或 HTTPS 认证。这里是文件同步仓库，安装通过下方脚本完成。

## 安装

需要 Git 和 Python 3.9+，无需第三方 Python 包。以下用 `python` 表示 Python 3；macOS/Linux 通常用 `python3`，Windows 也可用 `py -3`。

```sh
git clone https://github.com/X-Immortal/my-codex-pets.git
cd my-codex-pets
python pets.py list
python pets.py install
```

只装一个，或先预览：

```sh
python pets.py install baiqi
python pets.py install --dry-run
```

默认安装到 `$CODEX_HOME/pets`，未设置时使用 `~/.codex/pets`（Windows 为 `%USERPROFILE%\.codex\pets`）。可用 `--codex-home PATH` 指定 Codex 数据目录。安装后在 Codex 桌宠选择界面选择；若列表未刷新，重启 Codex。素材目录和版本依据本机已安装桌宠及 hatch-pet 格式核对，尚未在其他操作系统上实机验证。

更新已有仓库和桌宠：

```sh
git pull --ff-only
python pets.py install --dry-run
python pets.py install
```

相同文件会跳过；同名但内容不同时，整批操作会在复制前停止。确认以仓库版本为准后运行 `python pets.py install --replace`。旧目录会备份到 Codex 数据目录的 `pet-backups/`。恢复时关闭 Codex，将对应备份目录的文件复制回 `pets/<id>/`。

## 从其他设备上传

第一次可通过 SSH 克隆（或使用已认证的 HTTPS checkout）：

```sh
git clone git@github.com:X-Immortal/my-codex-pets.git
cd my-codex-pets
```

每次上传：

```sh
git pull --ff-only
python pets.py export --dry-run
python pets.py export
python pets.py validate
git status --short
git diff --stat
git add pets
git commit -m "Sync custom Codex pets"
git push origin main
```

`export` 默认收集本机桌宠目录里的所有有效桌宠；也可 `python pets.py export baiqi` 只导出一个。只复制清单及其引用的图片，不收集账号、配置、会话或生成过程文件。

如果同名冲突，检查差异后用 `python pets.py export baiqi --replace` 保留本机版本；仓库旧版本备份到本地 `pet-backups/`，此目录不会提交。脚本不自动删除任何另一台设备的桌宠，也不自动执行 Git 提交。没有变更时不需要提交。

多设备同时上传导致 push 被拒绝时，先 `git fetch origin` 并检查、合并远程更改，再推送；不要 force-push。图片冲突需要决定保留哪份，或为其中一个桌宠改目录名并同步修改 `pet.json` 的 `id`。

## 校验和备份

`python pets.py validate` 检查清单、版本、路径与素材存在性并显示 SHA-256；它不评判动画美术质量。`SHA256SUMS.txt` 是首次同步的原始文件校验记录，后续修改素材时可按需更新。初始内容共 5 个桌宠、10 个原始文件。

可使用 GitHub 的 **Code → Download ZIP** 下载仓库，解压后直接运行安装脚本。源素材包含作品角色，仓库不额外授予这些角色或素材的商业使用许可。
