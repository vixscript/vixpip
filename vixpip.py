#!/usr/bin/env python3
"""
vixpip — simple package manager for vixscript extensions (fixed)
"""

import sys, json, pathlib, shutil, zipfile, urllib.request

# ----- config -----
EXT_DIR = pathlib.Path.home() / ".vixscript/extensions"
EXT_DIR.mkdir(parents=True, exist_ok=True)

PACKAGE_INDEX_URL = "https://vixscript.github.io/extensions/extensions.json"

# ----- helpers -----
def fetch_package_index():
    try:
        with urllib.request.urlopen(PACKAGE_INDEX_URL) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except Exception as e:
        print("failed to fetch package index:", e)
        return {}

def install(pkg_name):
    index = fetch_package_index()
    if pkg_name not in index:
        print(f"package {pkg_name} not found in index")
        return

    url = index[pkg_name]["url"]
    zip_path = EXT_DIR / f"{pkg_name}.zip"
    target_dir = EXT_DIR / pkg_name

    print(f"downloading {pkg_name}...")
    try:
        urllib.request.urlretrieve(url, zip_path)
    except Exception as e:
        print("download failed:", e)
        return

    # unzip and flatten
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            members = zip_ref.namelist()
            # find common top folder
            top_folder = members[0].split("/")[0] if "/" in members[0] else ""
            for member in members:
                # remove top-level folder if present
                path_in_zip = member[len(top_folder)+1:] if top_folder and member.startswith(top_folder) else member
                if not path_in_zip:
                    continue
                target_path = target_dir / path_in_zip
                if member.endswith("/"):
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    with zip_ref.open(member) as source, open(target_path, "wb") as target:
                        target.write(source.read())
        zip_path.unlink()
        print(f"{pkg_name} installed successfully!")
    except Exception as e:
        print("failed to extract:", e)

def uninstall(pkg_name):
    pkg_path = EXT_DIR / pkg_name
    if not pkg_path.exists():
        print(f"{pkg_name} is not installed")
        return
    shutil.rmtree(pkg_path)
    print(f"{pkg_name} uninstalled")

def list_installed():
    EXT_DIR.mkdir(parents=True, exist_ok=True)
    installed = [p.name for p in EXT_DIR.iterdir() if p.is_dir()]
    if installed:
        print("installed packages:")
        for name in installed:
            print(" -", name)
    else:
        print("no packages installed")

# ----- main CLI -----
def main():
    if len(sys.argv) < 2:
        print("usage: python vixpip.py [install|uninstall|list] [package]")
        return

    cmd = sys.argv[1].lower()
    pkg = sys.argv[2] if len(sys.argv) >= 3 else None

    if cmd == "install" and pkg:
        install(pkg)
    elif cmd == "uninstall" and pkg:
        uninstall(pkg)
    elif cmd == "list":
        list_installed()
    else:
        print("unknown command or missing package")

if __name__ == "__main__":
    main()
