import os
import sys
import json
import shutil
import requests
import click
import winreg


package_dir = "C:\\scripts\\"
domain = "http://localhost:9999"


def getPackagePath(packageName, version=None):
    packages = os.listdir(package_dir)
    for package in packages:
        metadata_path = os.path.join(package_dir, package, "metadata.json")
        if not os.path.exists(metadata_path):
            continue
        with open(metadata_path, encoding='utf-8') as f:
            metadata = json.load(f)
        if metadata['name'] == packageName:
            return os.path.join(package_dir, package)
    return os.path.join(package_dir, packageName)


def getPackageMetadata(packageName):
    response = requests.get(f"{domain}/{packageName}/json", timeout=3)
    if response.status_code == 404:
        click.echo(f"[-] Package {packageName} does not exist")
        sys.exit(1)
    else:
        return response.json()


def installPackage(packageName, version=None, i=domain):
    domain = i
    metadata = getPackageMetadata(packageName)
    if version and version not in metadata["releases"]:
        click.echo(
            f"[-] Version {version} does not exist for package {packageName}")
        sys.exit(1)
    else:
        version = version if version else metadata["info"]["version"]
    release = metadata["releases"][version]
    click.echo(f"[+] Installing package {packageName} version {version}...")
    click.echo(f'[*] Author: {metadata["info"]["author"]}')
    click.echo(f'[*] Description: {metadata["info"]["description"]}')
    click.echo(f'[*] Upload time: {release["upload_time"]}')
    url = domain + release["url"]
    filename = os.path.basename(url)
    package_path = os.path.join(package_dir, filename)
    response = requests.get(url)

    with open(package_path, "wb") as f:
        f.write(response.content)

    if filename.endswith(".zip"):
        import zipfile

        with zipfile.ZipFile(package_path, "r") as zip_ref:
            zip_ref.extractall(package_path.strip(".zip"))
    click.echo(f"[+] Deleting downloaded package {filename}...")
    os.remove(package_path)

    folder_path = package_path.strip(".zip")
    addFolderToPath(folder_path)
    click.echo(f"[+] Successfully installed package {filename}...")


def deletePackage(packageName, version=None, i=domain):
    domain = i
    click.echo(f"[+] Deleting package {packageName} version {version}...")
    package_path = getPackagePath(packageName, version)
    click.echo(f"[+] Package path: {package_path}")
    if os.path.exists(package_path):
        for foldername, subfolders, filenames in os.walk(package_path):
            for filename in filenames:
                if filename.endswith(".exe"):
                    os.system(f"taskkill /F /IM {filename}")
        shutil.rmtree(package_path)
        os.system(f"startup -d {packageName}")
        removePath(package_path)
        click.echo(f"[+] {packageName} has been uninstalled")
    else:
        click.echo(f"[-] {packageName} is not installed")


def listInstalledPackages():
    packages = os.listdir(package_dir)
    for package in packages:
        metadata_path = os.path.join(package_dir, package, "metadata.json")
        if not os.path.exists(metadata_path):
            continue
        with open(metadata_path, encoding='utf-8') as f:
            metadata = json.load(f)

        click.echo(f"{metadata['name']}=={metadata['version']}")


def addStartupItems(packagePath):
    metadata_path = os.path.join(package_dir, packagePath, "metadata.json")
    with open(metadata_path, encoding='utf-8') as f:
        metadata = json.load(f)
    for items in metadata['startup']:
        os.system(f"startup -a {items} {metadata['name']}")


def addFolderToPath(folderPath):
    pathKey = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
        0,
        winreg.KEY_ALL_ACCESS,
    )
    pathValue = winreg.QueryValueEx(pathKey, "PATH")[0]

    if folderPath not in pathValue:
        newPath = ";".join([pathValue, folderPath])
        winreg.SetValueEx(pathKey, "PATH", 0, winreg.REG_EXPAND_SZ, newPath)
        os.environ["PATH"] = newPath
        print(f'[+] Added {folderPath} to path.')
    winreg.CloseKey(pathKey)
    print(os.environ["PATH"])


def removePath(pathToRemove):
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        0,
        winreg.KEY_ALL_ACCESS,
    )
    value, type = winreg.QueryValueEx(key, "Path")
    paths = value.split(";")
    if pathToRemove in paths:
        paths.remove(pathToRemove)
        newValue = ";".join(paths)
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, newValue)
        winreg.CloseKey(key)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("packagename")
@click.option("--version", default=None)
@click.option("--i", default=domain)
def install(packagename, version, i):
    installPackage(packagename, version, i)


@cli.command()
@click.argument("packagename")
@click.option("--version", default=None)
@click.option("--i", default=domain)
def uninstall(packagename, version, i):
    deletePackage(packagename, version, i)


@cli.command()
def list():
    listInstalledPackages()


if __name__ == "__main__":
    if not os.path.exists(package_dir):
        os.makedirs(package_dir)
    cli()
