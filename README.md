# dice 🎲

终端掷骰子小工具：跑团、桌游、抽签，一行命令搞定。

纯 Python 标准库，零依赖。随机源用 `secrets`（密码学安全随机），公平掷骰。

## 用法

```bash
python -m dice 2d6+3      # 掷 2 个 6 面骰，加 3
python -m dice d20        # 1 个 20 面骰（d20 = 1d20）
python -m dice 4d8-2      # 4 个 8 面骰，减 2
python -m dice 2d6 --count 5   # 连掷 5 次，给出最小/最大/平均
python -m dice --stats --trials 1000 3d6   # 分布直方图
python -m dice 2d6 --json      # JSON 输出，方便脚本
```

输出示例：

```
[4, 2] + 3 = 9
```

## 记法

标准 `NdM±K`：N 个 M 面骰，±K 修正值。

- `d20` 等价于 `1d20`
- 骰数 1–1000，面数 2–10000
- 非法记法（如 `2x6`）中文报错，exit 2

## 设计取舍

- 默认用 `secrets.randbelow`，不追求速度，追求公平。
- `--stats` 做的是蒙特卡洛直方图：`3d6` 的理论期望是 10.5，1000 次试验均值应在 10.5 ± 0.5 内——可用来验证随机源没跑偏。

## 已知局限

- `--stats` 是模拟统计不是解析计算，试验次数越大越准。
- 这是娱乐/桌游工具，不是密码学随机数发生器——要密钥请用兄弟项目 `passgen`。

## 许可证

MIT，Copyright (c) 2026 ljiang9。
