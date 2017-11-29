#!/usr/bin/env python3

import re
import sys

from subprocess import check_output

def extract(filename, regex):
    with open(filename, "rt") as file:
        match = re.search(regex, file.read(), re.MULTILINE)
    if not match:
        print("Could not find version in", filename)
        sys.exit(1)
    return match.group(1)

git_version = check_output(["git", "describe", "--dirty"])
git_version = git_version.decode("utf-8").strip()
print("GIT checkout version:", git_version)

setup_version = extract("setup.py", r'^\s+version=\"([^"]+)\",$')
print("setup.py version:", setup_version)

appveyor_version = extract("appveyor.yml", r'version:\s*([0-9.]+)\.\{build\}')
print("AppVeyor version:", appveyor_version)

REGEXP = r"^\[Application\]\n[^\[]*^version=\s*(\S*)$"
installer_version = extract("installer.cfg", REGEXP)
print("Windows installer version:", installer_version)

REGEXP = r"^\[Build\]\n[^\[]*^installer_name\s*=.*-win32-(.*)\.exe$"
installer_name_version = extract("installer.cfg", REGEXP)
print("Windows installer name version:", installer_name_version)

if "-" not in git_version:
    # a tagged release
    if git_version != setup_version:
        print("GIT version does not match setup version!")
        sys.exit(1)
else:
    # not an official release, we need it different
    all_tags = check_output(["git", "tag", "-l"])
    all_tags = all_tags.decode("utf-8").strip().split()
    if setup_version in all_tags:
        print("Code changed, but setup version is equal to an existing tag!")
        sys.exit(1)

if appveyor_version != setup_version:
    print("Wrong version in appveyor.yml!")
    sys.exit(1)

if installer_version != setup_version:
    print("Wrong version in installer.cfg!")
    sys.exit(1)

if installer_name_version != setup_version:
    print("Wrong version in installer_name in installer.cfg!")
    sys.exit(1)

print("Versions OK! :-)")
