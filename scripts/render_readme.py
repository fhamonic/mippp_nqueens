#!/usr/bin/env python3
"""Fill the tables of README.md from the CSVs in results/.

Every table in the README sits between a pair of HTML comments naming the
script that renders it (HTML comments are invisible on GitHub):

    <!-- table:mippp_vs_others -->
    | N | MIP++ | ... |
    <!-- /table -->

Running this script replaces each block with the current output of
`scripts/tables/<name>.py`, so the README never drifts from `results/`. The
prose around the blocks is edited by hand and never touched -- which is why
there is no README.md.in: the README is its own template.

    python3 scripts/render_readme.py            # rewrite the stale tables
    python3 scripts/render_readme.py --check    # report them and exit 1

`--check` is the one to run in CI or a pre-commit hook: it proves every number
a reviewer reads is the number in the committed CSVs.
"""

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
TABLES = ROOT / "scripts" / "tables"

BLOCK = re.compile(
    r"(?P<open><!-- table:(?P<name>[\w.-]+) -->\n)"
    r"(?P<body>.*?)"
    r"(?P<close>\n<!-- /table -->)",
    re.DOTALL,
)


def render(name: str) -> str:
    """Run one table script from the repository root and return its output."""
    script = TABLES / f"{name}.py"
    if not script.is_file():
        sys.exit(f"error: README.md asks for table '{name}', but {script} is missing")
    # cwd=ROOT so the scripts' "results/..." paths resolve; running the script
    # by path puts its own directory first on sys.path, which is how they find
    # their `helper` module.
    done = subprocess.run(
        [sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True
    )
    if done.returncode != 0:
        sys.exit(f"error: {script.name} failed:\n{done.stderr.strip()}")
    return done.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fill the tables of README.md from the CSVs in results/."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report stale tables and exit 1 instead of rewriting them",
    )
    args = parser.parse_args()

    text = README.read_text()
    pieces, stale, count, pos = [], [], 0, 0
    for match in BLOCK.finditer(text):
        fresh = render(match["name"])
        pieces.append(text[pos : match.start()])
        pieces.append(match["open"] + fresh + match["close"])
        pos = match.end()
        count += 1
        if fresh != match["body"]:
            stale.append((match["name"], match["body"], fresh))
    pieces.append(text[pos:])

    if count == 0:
        sys.exit("error: no <!-- table:... --> markers found in README.md")

    if not stale:
        print(f"README.md is up to date ({count} tables).")
        return 0

    for name, old, new in stale:
        print(f"--- stale table: {name}")
        diff = difflib.unified_diff(
            old.splitlines(), new.splitlines(), "README.md", f"{name}.py", lineterm=""
        )
        print("\n".join(diff))

    if args.check:
        print(f"\n{len(stale)} of {count} tables are stale; run without --check to fix.")
        return 1

    README.write_text("".join(pieces))
    print(f"\nRewrote {len(stale)} of {count} tables in README.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
