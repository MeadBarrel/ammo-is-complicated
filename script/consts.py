from pathlib import Path

ROOT_FOLDER = Path(__file__).parent.parent
BUILD_FOLDER = ROOT_FOLDER.joinpath("build")
RELEASE_FOLDER = ROOT_FOLDER.joinpath("release")
DATA_FOLDER = ROOT_FOLDER.joinpath("data")
CE_FOLDER = BUILD_FOLDER.joinpath("ce")


INGREDIENT_DEFNAMES_STRIKE_THE_EARTH = {
    "steel": "Steel",
    "uranium": "Uranium",
    "brass": "DF_Brass",
    "copper": "DF_CopperIngot",
    "lead": "DF_LeadIngot",
    "powder": "Chemfuel",
}


INGREDIENT_DEFNAMES_CUPROS_ALLOYS = {
    "steel": "Steel",
    "uranium": "Uranium",
    "brass": "CAL_Brass",
    "copper": "CAL_Copper",
    "lead": "CAL_Lead",
    "powder": "Chemfuel",
}

INGREDIENT_DEFNAMES_EMM = {
    "steel": "Steel",
    "uranium": "Uranium",
    "brass": "VMEu_Copper",
    "copper": "VMEu_Copper",
    "lead": "VMEu_Lead",
    "powder": "Chemfuel",
}
