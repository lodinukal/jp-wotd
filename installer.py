import requests
import platform

from pathlib import Path

github_url = "https://api.github.com/repos/lodinukal/jp-wotd/releases?per_page=1"

platform_to_asset = {
    "Windows": "jp-wotd.exe",
    "Linux": "jp-wotd-linux",
    "Darwin": "jp-wotd-darwin",
}
platform_asset = platform_to_asset[platform.system()]
install_path = Path.home() / ".jp-wotd"
platform_install = install_path / platform_asset
version_path = install_path / "version.txt"


def get_json():
    response = requests.get(github_url)
    return response.json()


def get_latest_release(json):
    return json[0]


def get_assets(d):
    return d["assets"]


def get_asset_url(d):
    for asset in get_assets(d):
        if asset["name"] == platform_asset:
            return asset["browser_download_url"]


def get_asset_words(d):
    for asset in get_assets(d):
        if asset["name"] == "words.csv":
            return asset["browser_download_url"]


def get_installed_version():
    if not version_path.exists():
        return None
    with open(version_path, "r") as f:
        return f.read().strip()


def write_version(version):
    with open(version_path, "w") as f:
        f.write(version)


def add_startup_windows():
    import winreg as reg
    import os

    s_name = "jp-wotd"
    address = f'"{platform_install}"'

    key = reg.HKEY_CURRENT_USER
    key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"

    print("Adding to startup...")

    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    reg.SetValueEx(open, s_name, 0, reg.REG_SZ, address)
    reg.CloseKey(open)

def remove_startup_windows():
    import winreg as reg
    import os

    s_name = "jp-wotd"

    key = reg.HKEY_CURRENT_USER
    key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"

    print("Removing from startup...")

    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    reg.DeleteValue(open, s_name)
    reg.CloseKey(open)


def install():
    j = get_json()
    d = get_latest_release(j)

    asset_url = get_asset_url(d)
    asset_words = get_asset_words(d)

    install_path.mkdir(exist_ok=True)

    current_version = get_installed_version()
    latest_version = d["tag_name"]
    if current_version == latest_version:
        print(f"Already installed ({latest_version})")
        return
    print(f"Installing {latest_version}...")

    with open(platform_install, "wb") as f:
        f.write(requests.get(asset_url).content)

    with open(install_path / "words.csv", "wb") as f:
        f.write(requests.get(asset_words).content)

    write_version(latest_version)

    if platform.system() == "Windows":
        add_startup_windows()

    print(f"Installed to {install_path}!")


def uninstall():
    if not install_path.exists():
        print("Not installed")
        return

    print("Uninstalling...")

    if platform.system() == "Windows":
        remove_startup_windows()

    platform_install.unlink()
    version_path.unlink()
    install_path.rmdir()

    print("Uninstalled!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall()
    elif len(sys.argv) > 1 and sys.argv[1] == "install":
        install()
    elif len(sys.argv) > 1:
        print("Invalid argument")
    else:
        install()
