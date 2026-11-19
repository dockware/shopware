#!/usr/bin/env python3
# Hourly PHP watcher (see .github/workflows/php-watcher.yml).
#
# Compares the php-fpm versions the ondrej/php PPA currently publishes with the
# versions of our last release (.github/php-versions.json). When a PHP version
# got a new upstream release (e.g. 8.4.27 -> 8.4.28) it
#   - bumps the shopware-essentials patch version from the newest CHANGELOG.md entry (1.4.0 -> 1.4.1),
#   - adds a changelog entry for the new release,
#   - raises the PHP versions in the existing SVRUnit tests (tests/svrunit/**/*.yml),
#     so the release build fails if an outdated mirror delivered an older PHP version,
#   - updates .github/php-versions.json,
#   - writes release=true and version=x.y.z to $GITHUB_OUTPUT.
# The workflow then commits these files and starts the CircleCI releases
# (essentials, current Shopware version and the LTS versions).
#
# Nothing happens while the PPA is not in sync for amd64 and arm64,
# a multi-arch build in that window ends up with mismatching or broken packages.
# The next run tries again.
#
# Options:
#   --include-revisions  also release on package-only rebuilds (8.4.27-1 -> 8.4.27-2).
#                        Needed for EOL versions (7.4, 8.0, 8.1), where ondrej only
#                        ships backported fixes as new package revisions.
#   --dry-run            only print what would happen, change no files.
import argparse
import glob
import json
import os
import re
import sys
import time
import urllib.request

SERIES = "noble"  # ubuntu:24.04 in src/Dockerfile
ARCHS = ["amd64", "arm64"]
API = "https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php?ws.op=getPublishedBinaries&binary_name=php{v}-fpm&exact_match=true&status=Published"

INSTALL_SCRIPT = "src/scripts/install_php.sh"
LOCK_FILE = ".github/php-versions.json"
CHANGELOG = "CHANGELOG.md"
SVRUNIT_TESTS = "tests/svrunit/**/*.yml"


def upstream(package_version):
    # "1:7.4.33-31+ubuntu24.04.1+deb.sury.org+1" -> "7.4.33"
    return package_version.split(":", 1)[-1].split("-", 1)[0]


def fetch(v):
    # launchpad sometimes takes a long time to answer, retry before giving up
    for attempt in range(1, 4):
        try:
            entries = json.load(urllib.request.urlopen(API.format(v=v), timeout=60))["entries"]
            break
        except OSError as e:
            print(f"PHP {v}: launchpad request failed (attempt {attempt}/3): {e}")
            if attempt == 3:
                raise
            time.sleep(10 * attempt)
    found = {}
    for e in entries:
        series, arch = e["distro_arch_series_link"].split("/")[-2:]
        if series == SERIES and arch in ARCHS:
            found[arch] = e["binary_package_version"]
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
    parser.add_argument("--include-revisions", action="store_true")
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
            # launchpad down: no release, the next run tries again
            print(f"::warning::launchpad not reachable, skipping this run: {e}")
            output(release="false")
            return
        missing = [a for a in ARCHS if a not in found]
        if missing or len(set(found.values())) > 1:
            print(f"PHP {v}: PPA NOT IN SYNC {found} missing={missing}, waiting for the next run")
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
        changed = upstream(old) != upstream(new) if not args.include_revisions else old != new
        print(f"PHP {v}: released {old}, published {new}" + ("  -> NEW" if changed else ""))
        if changed:
            changes.append((v, old, new))

    if not changes:
        output(release="false")
        return

    version = next_version()
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


def next_version():
    with open(CHANGELOG) as f:
        m = re.search(r"^## \[(\d+)\.(\d+)\.(\d+)\]", f.read(), re.M)
    if not m:
        sys.exit(f"no '## [x.y.z]' release found in {CHANGELOG}")
    major, minor, patch = map(int, m.groups())
    return f"{major}.{minor}.{patch + 1}"


def write_changelog(version, changes):
    lines = []
    for v, old, new in changes:
        if upstream(old) != upstream(new):
            lines.append(f"- Updated PHP {v} from {upstream(old)} to {upstream(new)}.")
        else:
            lines.append(f"- Updated PHP {v} package from {old} to {new} (ondrej/php rebuild).")
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
