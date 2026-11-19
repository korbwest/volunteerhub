"""Validate a commit message file or every commit in a Git revision range."""

import argparse
import re
import subprocess
from pathlib import Path

PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-zA-Z0-9_./-]+\))?!?: \S.*$"
)


def valid_message(message: str) -> bool:
    title = message.splitlines()[0] if message else ""
    return bool(PATTERN.fullmatch(title)) and len(title) <= 100


def git(*arguments):
    return subprocess.check_output(["git", *arguments], encoding="utf-8").strip()


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=Path)
    group.add_argument("--range", dest="revision")
    args = parser.parse_args()
    if args.file:
        messages = [(str(args.file), args.file.read_text(encoding="utf-8"))]
    else:
        messages = [
            (sha, git("show", "-s", "--format=%B", sha))
            for sha in git("rev-list", args.revision).splitlines()
        ]
    invalid = [
        (ref, body.splitlines()[0] if body else "")
        for ref, body in messages
        if not valid_message(body)
    ]
    for ref, title in invalid:
        print(f"Invalid Conventional Commit: {ref}: {title}")
    if invalid:
        raise SystemExit(1)
    print(f"Validated {len(messages)} commit message(s)")


if __name__ == "__main__":
    main()
