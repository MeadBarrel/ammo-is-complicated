import os
import shutil

import click

import script
from script.consts import RELEASE_FOLDER


@click.group
def main():
    pass


@click.command
def build():
    script.build()


@click.command
def install():
    local_mods_folder = os.getenv("RIMWORLD_LOCAL_MODS_FOLDER")
    if local_mods_folder is None:
        raise RuntimeError("environment variable RIMWORLD_LOCAL_MODS_FOLDER not found")
    path = os.path.join(local_mods_folder, "ammo_is_complicated")
    shutil.rmtree(path)
    shutil.copytree(RELEASE_FOLDER, path)


main.add_command(build)
main.add_command(install)


if __name__ == "__main__":
    main()
