#!/usr/bin/env python3
# PHP watcher, called every hour by .github/workflows/php-watcher.yml (the WHY is described there).
#
# Compares the php-fpm package versions packages.sury.org (Ondrej Sury) currently publishes for noble with the
# versions of our last release (.github/php-versions.json). When a PHP version got a new package
# version (a new PHP release like 8.4.27 -> 8.4.28, or a new package revision like
# 8.4.27-1 -> 8.4.27-2, which is how security fixes are backported), it
#   - bumps the shopware-essentials patch version: highest version of CHANGELOG.md and Docker Hub + 1 (1.5.0 -> 1.5.1),
#   - adds a changelog entry for the new release,
#   - raises the PHP versions in the existing SVRUnit tests (tests/svrunit/**/*.yml) to the new
#     package version, so a build from an outdated mirror (old PHP package) fails before anything is pushed,
#   - updates .github/php-versions.json,
#   - writes release=true and version=x.y.z to $GITHUB_OUTPUT.
# The workflow then commits these files and starts the CircleCI releases
# (shopware-essentials and the Shopware images from tests/scripts/php_watch_targets.py).
#
# Nothing is released while
#   - the repository is not in sync for amd64 and arm64 (a multi-arch build in that window ends up
#     with mismatching or broken packages),
#   - packages.sury.org or Docker Hub can't be reached.
# The next run tries again.
#
# If .github/php-versions.json does not exist, it is created with the current versions and
# nothing is released (bootstrap=true).
#
# Options:
#   --dry-run            only print what would happen, change no files.
import argparse
import functools
import glob
import gzip
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

SERIES = "noble"  # ubuntu:24.04 in src/Dockerfile
ARCHS = ["amd64", "arm64"]
# the php repository the image installs from (src/Dockerfile). The Launchpad ppa:ondrej/php
# is being merged into packages.sury.org and gets no new PHP versions for noble anymore.
PACKAGES = "https://packages.sury.org/php/dists/" + SERIES + "/main/binary-{arch}/Packages.gz"

INSTALL_SCRIPT = "src/scripts/install_php.sh"
LOCK_FILE = ".github/php-versions.json"
# the released versions on Docker Hub, the new version is based on the highest one
DOCKER_HUB_TAGS = "https://hub.docker.com/v2/repositories/dockware/shopware-essentials/tags?page_size=100"
CHANGELOG = "CHANGELOG.md"
SVRUNIT_TESTS = "tests/svrunit/**/*.yml"


def upstream(package_version):
    # "1:7.4.33-31+ubuntu24.04.1+deb.sury.org+1" -> "7.4.33"
    return package_version.split(":", 1)[-1].split("-", 1)[0]


def dpkg_compare(a, b):
    # debian version order (epochs, revisions, ~), exactly like apt decides what gets installed
    if a == b:
        return 0
    lower = subprocess.run(["dpkg", "--compare-versions", a, "lt", b]).returncode == 0
    return -1 if lower else 1


@functools.lru_cache(maxsize=None)
def packages(arch):
    # all package versions of the repository for one architecture: {"php8.4-fpm": ["8.4.27-1...", ...]}
    # the repository sometimes answers slowly or with 503 right after releases, retry before giving up
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(PACKAGES.format(arch=arch), timeout=60) as r:
                text = gzip.decompress(r.read()).decode()
            break
        except OSError as e:
            print(f"{arch}: php repository request failed (attempt {attempt}/3): {e}")
            if attempt == 3:
                raise
            time.sleep(10 * attempt)
    found = {}
    for block in text.split("\n\n"):
        name = re.search(r"^Package: (\S+)", block, re.M)
        version = re.search(r"^Version: (\S+)", block, re.M)
        if name and version:
            found.setdefault(name.group(1), []).append(version.group(1))
    return found


def fetch(v):
    # newest php-fpm version per architecture, this is what apt installs in the image
    found = {}
    for arch in ARCHS:
        versions = packages(arch).get(f"php{v}-fpm")
        if versions:
            found[arch] = max(versions, key=functools.cmp_to_key(dpkg_compare))
    return found


def output(**values):
    for k, v in values.items():
        print(f"{k}={v}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            for k, v in values.items():
                f.write(f"{k}={v}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # single source of truth: the active (not commented) entries in install_php.sh
    with open(INSTALL_SCRIPT) as f:
        versions = re.findall(r'^\s*"(\d+\.\d+):\d+"', f.read(), re.M)

    current = {}
    for v in versions:
        try:
            found = fetch(v)
        except OSError as e:
            # repository down: no release, the next run tries again
            print(f"::warning::php repository not reachable, skipping this run: {e}")
            output(release="false")
            return
        missing = [a for a in ARCHS if a not in found]
        if missing or len(set(found.values())) > 1:
            print(f"PHP {v}: NOT IN SYNC for amd64/arm64 {found} missing={missing}, waiting for the next run")
            output(release="false")
            return
        current[v] = found[ARCHS[0]]

    if not os.path.exists(LOCK_FILE):
        # first run: remember what is published now, release nothing
        print(f"{LOCK_FILE} does not exist, creating it with the currently published versions")
        if not args.dry_run:
            write_lock(current)
        output(release="false", bootstrap="true")
        return

    with open(LOCK_FILE) as f:
        released = json.load(f)

    changes = []
    for v in versions:
        old, new = released.get(v), current[v]
        if old is None:
            # a php version that was just added to install_php.sh comes with its own release
            print(f"PHP {v}: new in {INSTALL_SCRIPT}, recording {new}")
            continue
        # every new package version counts, revisions included: they carry the backported security fixes
        changed = old != new
        print(f"PHP {v}: released {old}, published {new}" + ("  -> NEW" if changed else ""))
        if changed:
            changes.append((v, old, new))

    if not changes:
        output(release="false")
        return

    try:
        version = next_version()
    except OSError as e:
        # without docker hub we can't be sure about the next version: no release, the next run tries again
        print(f"::warning::docker hub not reachable, skipping this run: {e}")
        output(release="false")
        return
    print(f"New release {version}")
    if not args.dry_run:
        write_changelog(version, changes)
        write_svrunit_tests(changes)
        write_lock(current)
    output(release="true", version=version)


def write_lock(current):
    with open(LOCK_FILE, "w") as f:
        json.dump(current, f, indent=4)
        f.write("\n")


def package(package_version):
    # "1:7.4.33-31+ubuntu24.04.1+deb.sury.org+1" -> "1:7.4.33-31"
    return package_version.split("+", 1)[0]


def write_svrunit_tests(changes):
    # the existing tests check the PHP version of the image, e.g.
    #   name: "php8.4-cli package is >= 8.4.27-1"  /  command: "... ge 8.4.27-1 ..."
    #   name: "PHP 8.4 CLI is patched (>= 8.4.27)" /  command: "... php8.4 -v ... ge 8.4.27 ..."
    # every line of a changed PHP version gets the complete new version (package and x.y.z),
    # so a build from an outdated mirror fails before anything is pushed.
    for v, old, new in changes:
        line_of_version = re.compile(rf"php(-fpm)?\s*{re.escape(v)}(?![\d])", re.I)
        old_upstream = re.compile(rf"(?<![\d.:]){re.escape(upstream(old))}(?![\d.-])")
        updated = []
        for path in sorted(glob.glob(SVRUNIT_TESTS, recursive=True)):
            with open(path) as f:
                lines = f.read().split("\n")
            changed = False
            for i, line in enumerate(lines):
                if not line_of_version.search(line):
                    continue
                new_line = line.replace(package(old), package(new))
                new_line = old_upstream.sub(upstream(new), new_line)
                if new_line != line:
                    lines[i] = new_line
                    changed = True
            if changed:
                with open(path, "w") as f:
                    f.write("\n".join(lines))
                updated.append(path)
        if updated:
            print(f"PHP {v}: updated SVRUnit tests " + ", ".join(updated))
        else:
            print(f"::warning::PHP {v}: no SVRUnit test with version {package(old)} / {upstream(old)} found")


def semver(text):
    return tuple(int(x) for x in text.split("."))


def next_version():
    # highest version of CHANGELOG.md and Docker Hub, so a version that was released
    # without a changelog entry is never released again (or overwritten as "latest")
    with open(CHANGELOG) as f:
        m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", f.read(), re.M)
    if not m:
        sys.exit(f"no '## [x.y.z]' release found in {CHANGELOG}")
    versions = [m.group(1)]

    url = DOCKER_HUB_TAGS
    while url:
        data = json.load(urllib.request.urlopen(url, timeout=30))
        versions += [t["name"] for t in data["results"] if re.fullmatch(r"\d+\.\d+\.\d+", t["name"])]
        url = data.get("next")

    highest = max(versions, key=semver)
    if highest != m.group(1):
        print(f"{CHANGELOG} ends at {m.group(1)}, but {highest} is already released on Docker Hub")
    major, minor, patch = semver(highest)
    return f"{major}.{minor}.{patch + 1}"


def write_changelog(version, changes):
    lines = []
    for v, old, new in changes:
        if upstream(old) != upstream(new):
            lines.append(f"- Updated PHP {v} from {upstream(old)} to {upstream(new)}.")
        else:
            lines.append(f"- Updated PHP {v} package from {old} to {new} (package update, backported fixes).")
    entry = f"## [{version}]\n\n### Security\n\n" + "\n".join(lines) + "\n\n"

    with open(CHANGELOG) as f:
        content = f.read()
    # insert before the newest release
    m = re.search(r"^## \[", content, re.M)
    content = content[:m.start()] + entry + content[m.start():]
    with open(CHANGELOG, "w") as f:
        f.write(content)


if __name__ == "__main__":
    main()
