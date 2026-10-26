# Clash 订阅聚合工具

自动从多个公开源采集、过滤、去重并合并 Clash 代理配置文件。

## 功能

- 从多个公开源自动获取免费代理节点
- 过滤本地 IP、无效节点和含 `reality-opts` 但缺失 `short-id` 的节点
- 按服务器地址去重
- 合并到主配置文件，生成负载均衡和自动选择节点组
- 通过 GitHub Actions 定时自动运行（每 8 小时）

## 项目结构

```
├── src/
│   └── get_clash_subscribe/
│       └── main.py          # 主程序
├── .github/
│   └── workflows/
│       ├── main.yml         # 自动采集工作流（每 8 小时）
│       └── clear.yml        # 每周清理提交记录
├── public/
│   └── subscribe/           # 输出目录（clash.yml）
├── pyproject.toml           # Python 依赖配置
└── uv.lock                  # uv 锁文件
```

## 依赖

- Python >= 3.13
- pyyaml >= 6.0.2
- requests >= 2.32.3

## 本地运行

```bash
uv run python ./src/get_clash_subscribe/main.py
```

生成的配置文件输出至 `public/subscribe/clash.yml`。

## GitHub Actions

### 自动采集

`.github/workflows/main.yml` 负责：

1. 手动触发（`workflow_dispatch`）或每 8 小时定时触发
2. 使用 `uv` 安装 Python 和依赖
3. 执行 `main.py` 生成订阅
4. 自动提交并推送更改到仓库

### 清理提交记录

`.github/workflows/clear.yml` 每周一凌晨 2 点触发，重建仓库历史以保持提交记录简洁。

## 输出配置说明

合并后的配置包含以下代理组：

- **🪐 负载均衡** — 使用一致哈希策略的负载均衡组
- **♻️ 自动选择** — 自动检测延迟最低的节点

## ⚠️ 免责声明

- 链接均来自网络公开资源，仅用于学习研究
- 使用任何代理资源时请务必遵守当地法律法规
- 本工具不提供任何代理服务，不对节点可用性和安全性作任何保证
