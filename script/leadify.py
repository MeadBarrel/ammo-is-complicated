import json
import logging
import os
from functools import partial
from pathlib import Path
from typing import Callable, Iterator

from lxml import etree
from rimworld.mod import dataclass, make_element
from rimworld.patch import PatchOperation, PatchOperationReplace
from rimworld.patch.operations.add import SafeElement
from rimworld.xml import ElementXpath, ensure_element_text

from .consts import DATA_FOLDER


@dataclass
class FoundIngredients:
    things: dict[str, int]
    categories: dict[str, int]


def leadify_bullets(
    ce_tree: etree._ElementTree,
    ingredient_defnames: dict[str, str],
    path: Path,
):
    with open(DATA_FOLDER.joinpath("ammo.json"), "r", encoding="utf-8") as f:
        ammo_data = json.load(f)

    ammo_data = {
        k: preprocess_weights(v, ingredient_defnames) for k, v in ammo_data.items()
    }

    for label, weights in ammo_data.items():
        try:
            make_ammo_patch(ce_tree, label, weights, path)
        except RuntimeError as e:
            logging.getLogger(__name__).error(str(e))


def make_ammo_patch(
    ce_tree: etree._ElementTree, label: str, weights: dict[str, float], path: Path
):
    if (ammo_def := find_ammo_def(ce_tree, label)) is None:
        raise RuntimeError(f"Could not find def with label {label}")
    ammo_def_name = ensure_element_text(ammo_def.find("defName"))
    operations = []
    for recipe in ammo_recipes(ce_tree, ammo_def_name):
        operations = list(recipe_patches(recipe, weights))
    if operations:
        path = path.joinpath(f"Patches/{ammo_def_name}.xml")
        os.makedirs(path.parent, exist_ok=True)
        patch_root = etree.Element("Patch")
        patch_tree = etree.ElementTree(patch_root)
        for operation in operations:
            operation_node = etree.Element("Operation")
            operation.to_xml(operation_node)
            patch_root.append(operation_node)
        patch_tree.write(
            path, pretty_print=True, xml_declaration=True, encoding="utf-8"
        )


def recipe_patches(
    recipe: etree._Element, weights: dict[str, float]
) -> Iterator[PatchOperation]:
    thing_ingredients = {
        name: int(count)
        for _ in recipe.findall("ingredients")
        for li in _.findall("li")
        for _ in li.findall("count")
        if (count := _.text) is not None
        for _ in li.findall("filter")
        for _ in _.findall("thingDefs")
        for _ in _.findall("li")
        if (name := _.text) is not None
    }
    category_ingredients = {
        name: int(count)
        for _ in recipe.findall("ingredients")
        for li in _.findall("li")
        for _ in li.findall("count")
        if (count := _.text) is not None
        for _ in li.findall("filter")
        for _ in _.findall("categories")
        for _ in _.findall("li")
        if (name := _.text) is not None
    }

    ammo_weight = thing_ingredients.pop("Steel", 0) + thing_ingredients.pop(
        "Uranium", 0
    )
    new_weights = {k: int(max(1, round(v * ammo_weight))) for k, v in weights.items()}
    new_thing_ingredients = {
        k: thing_ingredients.get(k, 0) + new_weights.get(k, 0)
        for k in set([*thing_ingredients, *new_weights])
    }

    recipe_defname = ensure_element_text(recipe.find("defName"))

    yield PatchOperationReplace(
        xpath=ElementXpath(f'/Defs/RecipeDef[defName="{recipe_defname}"]/ingredients'),
        value=SafeElement(
            VALUE(
                E(
                    "ingredients",
                    [
                        LI([FILTER(THINGDEFS(LI(k))), COUNT(str(v))])
                        for k, v in new_thing_ingredients.items()
                    ]
                    + [
                        LI([FILTER(E("categories", LI(k))), COUNT(str(v))])
                        for k, v in category_ingredients.items()
                    ],
                )
            )
        ),
    )
    yield PatchOperationReplace(
        xpath=ElementXpath(
            f'/Defs/RecipeDef[defName="{recipe_defname}"]/fixedIngredientFilter'
        ),
        value=SafeElement(
            VALUE(
                E(
                    "fixedIngredientFilter",
                    [
                        THINGDEFS([LI(k) for k in new_thing_ingredients]),
                        E("categories", [LI(k) for k in category_ingredients]),
                    ],
                )
            )
        ),
    )


def E(
    tag: str, children: etree._Element | list[etree._Element] | str
) -> etree._Element:
    if isinstance(children, str):
        return make_element(tag, children)
    if isinstance(children, list):
        return make_element(tag, children=children)
    return make_element(tag, children=[children])


LI = partial(E, "li")
VALUE = partial(E, "value")
FILTER = partial(E, "filter")
THINGDEFS = partial(E, "thingDefs")
COUNT = partial(E, "count")


def ammo_recipes(tree: etree._ElementTree, def_name: str) -> Iterator[etree._Element]:
    return (
        node
        for node in tree.findall("RecipeDef")
        for _ in node.findall("products")
        for _ in _.findall(def_name)
    )


def preprocess_weights(
    weights: dict[str, float],
    ingredient_defnames: dict[str, str],
) -> dict[str, float]:
    weights_ = {}

    for ingredient_name, ingredient_weight in weights.items():
        ingredient_def_name = ingredient_defnames.get(ingredient_name, None)
        if ingredient_def_name is None:
            continue
        weights_[ingredient_def_name] = (
            weights_.get(ingredient_def_name, 0.0) + ingredient_weight
        )

    weights = weights_

    total_weight = sum(weights.values())
    return {k: w / total_weight for k, w in weights.items()}


def find_ammo_def(ce_tree: etree._ElementTree, label: str) -> etree._Element | None:
    return next(
        (
            node
            for node in ce_tree.getroot().findall("ThingDef")
            for _ in node.findall("label")
            if _.text == label
        ),
        None,
    )
