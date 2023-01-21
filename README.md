# AdiBags Creator (by Zottelchen)

## What does it do?

It takes item IDs from lists in /items and creates an AdiBags Plugin from that. Just put your Blizzard API credentials into system variables BLIZZ_ID and BLIZZ_SECRET and run create.py.

## Changes from Version 1

* If it isn't clear, this is breaking changes. Stuff in ./items/ needs to be updated.
* The addon code is ~~slightly better (think about upgrading from 'common' to 'uncommon'😅)~~  a new flavor of weird and has new features such as:
    * prefixes
    * custom colors
    * grouped item categories
    * localization
    * categories are sorted alphabetically
* The item lists are now in a proper config format (toml instead of loose text files)
* The generator code has been reworked to be hopefully less of a headache to work with
* some environment variables are no longer environment variables, but instead can be found in items/_addon.toml
* The markdown file now is sorted & contains a sample image of the color used for the item category
* the builder now uses poetry for dependency management instead of pip

## Environment Variables

* BLIZZARD_API_ID: Your Blizzard API ID
* BLIZZARD_API_SECRET: Your Blizzard API Secret
* BLIZZARD_API_REGION: Your Blizzard API Region (default: eu), only relevant for authentication
* GITHUB_GIST_ID: The GIST ID which contains item names (defaults to "[b86d83d7b11377fb4a143d9cb12aef64](https://gist.github.com/Zottelchen/b86d83d7b11377fb4a143d9cb12aef64)")
* GITHUB_TOKEN: Your GitHub Token for adding item names to the cache - not needed, the cache is read-only by default. Only use, if you set up your own item name cache.
* DEBUG: Set to 1 to disable fetching of item names and also maybe print some extra stuff

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
# according to the TOML spec, the category_description inline table should be in a single line
# there are three descriptions: _ (the default), markdown & addon
# _ will be used for both by default, but if one (or both) of the other two is defined, they will be used instead for their respective target
category_description = { _ = "Hearthstones are used to teleport to a previously visited location.", markdown = "This overwrites the description for markdown. It is optional, if not found, the default description is used instead.", addon = "This overwrites the description ingame. It is optional, if not found, the default description is used instead." }
mergeable = true # if true, there will be an extra option to merge all the subcategories of this file into one (default: false)
merged_by_default = false # if true, the merged category will be enabled by default (default: true, but will only take effect if mergeable above is enabled)
```

Then follows one or more lists of items. These will be grouped ingame:

```toml 
[normal] #categorie separator. it isn't used in the addon.
name = "Normal Hearthstone" # name of the category
enabled_by_default = false # if the category should be enabled by default - if this is missing, the creator assumes TRUE
description = { _ = "A Hearthstone" } # this works similiar to the category description
color = 0xff0000 # color of the category - make sure to use hex values (0x prefix and no "" around the value)
bonus_condition = false # very optional - IGNORING the ID list, if this is a method name (e.g. "C_ItemUpgrade.CanUpgradeItem") items returning true with that method will be in the category
override_method = false # very optional - IN ADDITION to the ID list, the item is checked against this method (e.g. "C_LegendaryCrafting.IsRuneforgeLegendary"). If the method returns FALSE, the item IS in the category
items = [ # list of item ids
    6948,
    140192,
    110560
]
```