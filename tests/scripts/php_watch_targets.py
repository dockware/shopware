#!/usr/bin/env python3
# Finds the dockware/shopware images that the PHP watcher has to rebuild.
#
# Source of truth is Docker Hub: for "latest" and every "<major>-latest" tag (6.7-latest,
# 6.6-latest, ...) the Shopware version with the same digest is rebuilt, from
#   - main, if it is the CURRENT_SW_VERSION of main,
#   - otherwise the branch lts/sw-<version>.
# So only versions that are really published as latest are rebuilt, with the same tags.
#
# Prints one line per image: "<branch> <version> <setLatest> <setMajorLatest>"
# Majors in the env SKIP_MAJORS (space separated, e.g. "6.5") are skipped.
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

HUB = "https://hub.docker.com/v2/repositories/dockware/shopware/tags"


def get(url):
    for attempt in range(1, 4):
        try:
            return json.load(urllib.request.urlopen(url, timeout=30))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            error = e
        except OSError as e:
            error = e
        print(f"docker hub request failed (attempt {attempt}/3): {error}", file=sys.stderr)
        time.sleep(10 * attempt)
    raise error


def digest_of(tag):
    data = get(f"{HUB}/{tag}")
    return data and data.get("digest")


def version_with_digest(major, digest):
    url = f"{HUB}?name={major}.&page_size=100"
    while url:
        data = get(url)
        for t in data["results"]:
            if t.get("digest") == digest and re.fullmatch(r"\d+\.\d+\.\d+\.\d+", t["name"]):
                return t["name"]
        url = data.get("next")
    return None


def main():
    with open("makefile") as f:
        main_version = re.search(r"^CURRENT_SW_VERSION:=\s*(\S+)", f.read(), re.M).group(1)

    heads = subprocess.run(["git", "ls-remote", "--heads", "origin", "lts/sw-*"],
                           capture_output=True, text=True, check=True).stdout
    lts_branches = set(re.findall(r"refs/heads/(lts/sw-\S+)", heads))

    majors = {".".join(main_version.split(".")[:2])}
    majors |= {".".join(b[len("lts/sw-"):].split(".")[:2]) for b in lts_branches}
    skip = os.environ.get("SKIP_MAJORS", "").split()

    latest_digest = digest_of("latest")

    for major in sorted(majors, key=lambda m: [int(x) for x in m.split(".")], reverse=True):
        if major in skip:
            print(f"{major}: skipped (SKIP_MAJORS)", file=sys.stderr)
            continue
        digest = digest_of(f"{major}-latest")
        if not digest:
            print(f"{major}: no {major}-latest tag on docker hub, skipped", file=sys.stderr)
            continue
        version = version_with_digest(major, digest)
        if not version:
            print(f"::warning::{major}-latest: no version tag with the same digest found, skipped", file=sys.stderr)
            continue

        if version == main_version:
            branch = "main"
        elif f"lts/sw-{version}" in lts_branches:
            branch = f"lts/sw-{version}"
        else:
            print(f"::warning::{major}-latest is {version}, but there is no branch lts/sw-{version}, skipped", file=sys.stderr)
            continue

        is_latest = "true" if digest == latest_digest else "false"
        print(f"{branch} {version} {is_latest} true")


if __name__ == "__main__":
    main()
