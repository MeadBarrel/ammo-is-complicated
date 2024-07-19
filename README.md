# Ammo Is Complicated

"Ammo Is Complicated" is a Rimworld mod which makes ammo production use various materials
from various mods that add them. 

## Supported mods

 - [Strike the Earth! - Ores and Alloys](https://steamcommunity.com/sharedfiles/filedetails/?id=2938701885) - You need to have brass and lead enabled in the mod settings, otherwise you'll have errors all over the place
 - [Cupro's Alloys (continued)](https://steamcommunity.com/sharedfiles/filedetails/?id=2019702358)
 - [Expanded Materials - Metals](https://steamcommunity.com/sharedfiles/filedetails/?id=3263239001&searchtext=metals) - Uses copper instead of brass

## Building

The mod needs to first be built using python 3.12 (if you don't want/need to build it yourself, you can check pre-built releases to the right). 

 - install poetry
 - run poetry shell
 - run python main.py build

The final mod will be in the `release` folder.
