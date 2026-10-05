"""dice - 终端掷骰子工具。

标准记法 NdM±K：N 个 M 面骰，加/减修正值 K。
随机源用 secrets（密码学安全随机），公平掷骰。
"""
import argparse
import collections
import json
import re
import secrets
import sys

VERSION = "0.1.0"

NOTATION_RE = re.compile(r"^\s*(\d*)\s*[dD]\s*(\d+)\s*([+-]\s*\d+)?\s*$")


def parse_notation(text):
    """解析骰子记法，返回 (骰数, 面数, 修正值)。非法记法抛 ValueError。"""
    m = NOTATION_RE.match(text)
    if not m:
        raise ValueError(f"无法解析骰子记法：{text!r}（形如 2d6+3、d20、4d8-2）")
    n = int(m.group(1)) if m.group(1) else 1
    faces = int(m.group(2))
    mod = int(m.group(3).replace(" ", "")) if m.group(3) else 0
    if n < 1 or n > 1000:
        raise ValueError(f"骰子数量 {n} 超出范围（1-1000）")
    if faces < 2 or faces > 10000:
        raise ValueError(f"骰子面数 {faces} 超出范围（2-10000）")
    return n, faces, mod


def roll(n, faces):
    """掷 n 个 faces 面骰，返回每颗点数列表。"""
    return [secrets.randbelow(faces) + 1 for _ in range(n)]


def roll_total(n, faces, mod):
    dice = roll(n, faces)
    return dice, sum(dice) + mod


def format_roll(dice, mod, total):
    dice_str = "[" + ", ".join(str(d) for d in dice) + "]"
    if mod > 0:
        return f"{dice_str} + {mod} = {total}"
    if mod < 0:
        return f"{dice_str} - {-mod} = {total}"
    return f"{dice_str} = {total}"


def cmd_roll(args):
    try:
        n, faces, mod = parse_notation(args.notation)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.count and args.count > 1:
        totals = []
        lines = []
        for _ in range(args.count):
            dice, total = roll_total(n, faces, mod)
            totals.append(total)
            lines.append(format_roll(dice, mod, total))
        if args.json:
            print(json.dumps({
                "notation": args.notation,
                "rolls": [{"total": t} for t in totals],
                "min": min(totals), "max": max(totals),
                "avg": round(sum(totals) / len(totals), 2),
            }, ensure_ascii=False))
        else:
            for line in lines:
                print(line)
            print(f"共 {args.count} 次：最小 {min(totals)}，最大 {max(totals)}，"
                  f"平均 {sum(totals) / len(totals):.2f}")
        return 0
    dice, total = roll_total(n, faces, mod)
    if args.json:
        print(json.dumps({
            "notation": args.notation, "dice": dice,
            "modifier": mod, "total": total,
        }, ensure_ascii=False))
    else:
        print(format_roll(dice, mod, total))
    return 0


def cmd_stats(args):
    try:
        n, faces, mod = parse_notation(args.notation)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    trials = args.trials
    if trials < 1 or trials > 100000:
        print("error: 试验次数超出范围（1-100000）", file=sys.stderr)
        return 2
    counter = collections.Counter()
    for _ in range(trials):
        _, total = roll_total(n, faces, mod)
        counter[total] += 1
    lo, hi = min(counter), max(counter)
    peak = max(counter.values())
    width = 40
    mean = sum(t * c for t, c in counter.items()) / trials
    print(f"===== 分布统计：{args.notation} × {trials} 次 =====")
    print(f"均值 {mean:.2f}（理论期望 {(n * (faces + 1) / 2 + mod):.2f}）")
    for t in range(lo, hi + 1):
        c = counter.get(t, 0)
        bar = "█" * round(c / peak * width) if peak else ""
        print(f"  {t:>4}  {c:>6}  {bar}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="dice", description="终端掷骰子：dice 2d6+3")
    p.add_argument("--version", action="version", version=f"dice {VERSION}")

    p.add_argument("notation", nargs="?", default=None, help="骰子记法，如 2d6+3、d20")
    p.add_argument("--count", type=int, default=1, help="掷多次并给出统计")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    p.add_argument("--stats", dest="stats", action="store_true",
                   help="分布直方图（与 --trials 配合）")
    p.add_argument("--trials", type=int, default=1000, help="--stats 的试验次数")

    args = p.parse_args(argv)
    if not args.notation:
        p.print_usage(sys.stderr)
        print("error: 请给出骰子记法，例如：dice 2d6+3", file=sys.stderr)
        return 2
    if args.stats:
        args.trials = args.trials
        return cmd_stats(args)
    return cmd_roll(args)


if __name__ == "__main__":
    sys.exit(main())
