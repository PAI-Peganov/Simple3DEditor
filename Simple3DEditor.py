#!/usr/bin/env python3
import sys
import subprocess


def main():
    args = sys.argv[1:]

    if "--help" in args:
        with open("README.md", "r", encoding="utf-8") as f:
            for line in f.readlines():
                print(line)
        return

    subprocess.run(["python", "src/QtApp.py"])


if __name__ == "__main__":
    main()
