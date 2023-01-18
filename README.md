# AdiBags Creator (by Zottelchen)

## What does it do?

It takes item IDs from lists in /items and creates an AdiBags Plugin from that. Just put your Blizzard API credentials into system variables BLIZZ_ID and BLIZZ_SECRET and run create.py.

## Changes from Version 1

* The addon code is slightly better and features new features such as:
    * prefixes
    * custom colors #TODO
    * grouped item categories #TODO
    * localization #TODO
* The item lists are now in a proper config format (toml instead of loose text files)
* The generator code has been reworked to be hopefully less of a headache to work with
* some environment variables are no longer environment variables, but instead can be found in items/_addon.toml
* The markdown file now is sorted & contains a sample image of the color used for the item category

## Environment Variables

* BLIZZARD_API_ID: Your Blizzard API ID
* BLIZZARD_API_SECRET: Your Blizzard API Secret
* BLIZZARD_API_REGION: Your Blizzard API Region (default: eu), only relevant for authentication
* GITHUB_GIST_ID: The GIST ID which contains item names (defaults to "[b86d83d7b11377fb4a143d9cb12aef64](https://gist.github.com/Zottelchen/b86d83d7b11377fb4a143d9cb12aef64)")
* GITHUB_TOKEN: Your GitHub Token for adding item names to the cache - not needed, the cache is read-only by default. Only use, if you setup your own item name cache.

* DEBUG: Set to 1 to disable fetching of item names

## _addon.toml

There now is a file *_addon.toml* in the items folder which defines some basics for the addon/filter. This file contains the following options:

```toml
filter_name = "V2_TESTING" # The name of the filter
filter_description = "This is a test addon for V2" # The description of the filter
filter_author = "Zottelchen" # The author of the filter
prefixes = ["V2", "icon:134157"] # The prefixes which can be selected ingame. If you want to use an icon, use the icon: prefix


[replacers] # this table contains replacers. e.g. if there is "ENTRY" here, all files will replace "%ENTRY%" with whatever is defined below. The following are currently used:
ADDON_COLOR = 0xff0000 #make sure to use the correct format - 0xRRGGBB
TOC_VERSION = "100002" # the TOC version of the addon
CURSE_ID = "no_curse_id" # the curse id of the addon - important if you use BigWigsMods/packager
WAGO_ID = "no_wago_id" # the wago id of the addon - important if you use BigWigsMods/packager
WOW_INTERFACE_ID = "no_wowi_id" # the wowinterface id of the addon - important if you use BigWigsMods/packager
```

## ID Lists

At the top level there are 3 properties:

```toml
category_name = "Hearthstones"
category_color = 0x0000ff # make sure to use hex values (0x prefix and no "" around the value)
category_description = { _ = "Hearthstones are used to teleport to a previously visited location.",
markdown = "This overwrites the description for markdown. It is optional, if not found, the default description is used instead.",
addon = "This overwrites the description ingame. It is optional, if not found, the default description is used instead." }
# according to the TOML spec, the category_description inline table should be in a single line
```

Then follows one or more lists of items. These will be grouped ingame:

```toml 
[normal] #categorie separator. it isn't used in the addon.
name = "Normal Hearthstone" #name of the category
disabled_by_default = false # if the category should be disabled by default
description = { _ = "A Hearthstone" } # this works similiar to the category description
color = 0xff0000 # color of the category - make sure to use hex values (0x prefix and no "" around the value)
items = [ # list of item ids
    6948
]
```