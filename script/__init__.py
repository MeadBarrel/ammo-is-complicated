import os
import shutil
from pathlib import Path

from git import Repo
from lxml import etree
from rimworld.mod import (GameVersion, LoadFolder, LoadFolders, Mod, ModAbout,
                          ModDependency, ModsConfig, load_xml)
from rimworld.xml import merge

from .consts import (BUILD_FOLDER, CE_FOLDER, DATA_FOLDER,
                     INGREDIENT_DEFNAMES_CUPROS_ALLOYS,
                     INGREDIENT_DEFNAMES_EMM,
                     INGREDIENT_DEFNAMES_STRIKE_THE_EARTH, RELEASE_FOLDER)
from .leadify import leadify_bullets


def build():
    if BUILD_FOLDER.exists():
        shutil.rmtree(BUILD_FOLDER)
    if RELEASE_FOLDER.exists():
        shutil.rmtree(RELEASE_FOLDER)
    os.makedirs(RELEASE_FOLDER.joinpath("About"), exist_ok=True)
    os.makedirs(BUILD_FOLDER, exist_ok=True)
    about = ModAbout(
        package_id="tashka.complexammo",
        name="Ammo is complicated",
        authors=["tashka"],
        supported_versions=(GameVersion.new("1.5"),),
        description="Makes ammo-making process require lead, brass, and chemfuel for powder",
        mod_dependencies=[
            ModDependency(
                package_id="ceteam.combatextended",
                display_name="Combat Extended",
                steam_workshop_url="https://steamcommunity.com/sharedfiles/filedetails/?id=2890901044",
            ),
        ],
        load_after=[
            "ceteam.combatextended",
            "hol.dfore",
            "mlie.cuprosalloys",
            "argon.vmeu",
        ],
    )
    about.to_xml().write(
        RELEASE_FOLDER.joinpath("About", "About.xml"),
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
    )

    loadfolders = LoadFolders(
        {
            GameVersion.new("1.5"): [
                LoadFolder(
                    if_mod_active="hol.dfore", path=Path("Mods", "StrikeTheEarth")
                ),
                LoadFolder(
                    if_mod_active="mlie.cuprosalloys", path=Path("Mods", "CuprosAlloys")
                ),
                LoadFolder(
                    if_mod_active="argon.vmeu",
                    path=Path("Mods", "ExpandedMaterialsMetals"),
                ),
            ],
        }
    )
    loadfolders.to_xml().write(
        RELEASE_FOLDER.joinpath("LoadFolders.xml"),
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
    )

    shutil.copy(
        DATA_FOLDER.joinpath("Preview.png"),
        RELEASE_FOLDER.joinpath("About", "Preview.png"),
    )

    # Clone Combat Extended
    Repo.clone_from(
        "git@github.com:CombatExtended-Continued/CombatExtended.git", CE_FOLDER
    )

    ce_tree = etree.ElementTree(etree.Element("Defs"))
    ce_mod = Mod.load(CE_FOLDER)
    mods_config = ModsConfig(
        GameVersion.new("1.5"),
        [
            "Ludeon.Rimworld.Royalty",
            "Ludeon.Rimworld.Ideology",
            "Ludeon.Rimworld.Biotech",
            "Ludeon.Rimworld.Anomaly",
        ],
        [],
    )
    for def_file in ce_mod.def_files(mods_config):
        merge(ce_tree, load_xml(def_file))

    leadify_bullets(
        ce_tree,
        INGREDIENT_DEFNAMES_STRIKE_THE_EARTH,
        RELEASE_FOLDER.joinpath("Mods", "StrikeTheEarth"),
    )
    leadify_bullets(
        ce_tree,
        INGREDIENT_DEFNAMES_CUPROS_ALLOYS,
        RELEASE_FOLDER.joinpath("Mods", "CuprosAlloys"),
    )
    leadify_bullets(
        ce_tree,
        INGREDIENT_DEFNAMES_EMM,
        RELEASE_FOLDER.joinpath("Mods", "ExpandedMaterialsMetals"),
    )
    shutil.rmtree(BUILD_FOLDER)
